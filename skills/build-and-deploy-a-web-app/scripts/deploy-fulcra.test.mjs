import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const module = await import('./deploy-fulcra.mjs').catch(() => ({}));
test('scoped deploy implementation is available', () =>
  assert.equal(typeof module.deployFulcra, 'function'));

function fixture() {
  const calls = [],
    deployed = [];
  let settings = {
    framework: null,
    buildCommand: '',
    outputDirectory: '.',
    nodeVersion: '24.x',
    resourceConfig: { fluid: true },
    autoExposeSystemEnvs: true,
    targets: { production: { id: 'previous-deployment' } }
  };
  const project = { id: 'owned-project', name: 'sample', domain: 'sample.my.fulcra.ai' };
  return {
    calls,
    deployed,
    project,
    async fetchImpl(url, options = {}) {
      calls.push({ url, ...options });
      if (url.endsWith('/user/v1/deploy/project')) {
        assert.notEqual(options.method, 'POST', 'parked namespace must be reused');
        return Response.json([project]);
      }
      if (url.endsWith('/owned-project/token'))
        return Response.json({
          token: 'scoped-secret',
          platform_team_id: 'team',
          platform_project_id: 'project'
        });
      if (url.startsWith('https://api.vercel.com/v9/projects/project?')) {
        if (options.method === 'PATCH') settings = { ...settings, ...JSON.parse(options.body) };
        return Response.json(settings);
      }
      throw Error('Unexpected request: ' + url);
    },
    async run(args, env) {
      deployed.push({ args, env });
      return 0;
    }
  };
}

if (module.deployFulcra) {
  test('reuses parked project, persists before deploy, repairs static settings, and isolates build secrets', async () => {
    const cwd = await mkdtemp(join(tmpdir(), 'fulcra-deploy-'));
    try {
      const f = fixture();
      await module.deployFulcra({
        cwd,
        name: 'sample',
        framework: 'sveltekit',
        expectedDomain: 'sample.my.fulcra.ai',
        values: { PUBLIC_AUTH0_DOMAIN: 'auth.example', SECRET: 'never-build' },
        accessToken: 'fulcra-secret',
        fetchImpl: f.fetchImpl,
        run: async (args, env) => {
          const saved = JSON.parse(await readFile(join(cwd, '.private/fulcra-deployment.json')));
          assert.equal(saved.project.id, f.project.id);
          assert.equal(saved.previousProductionDeploymentId, 'previous-deployment');
          assert.equal(saved.beforeDeploySettings.framework, null);
          return f.run(args, env);
        }
      });
      const patch = JSON.parse(f.calls.find((x) => x.method === 'PATCH').body);
      assert.equal(patch.framework, 'sveltekit');
      assert.equal(patch.buildCommand, 'npm run build');
      assert.equal(patch.outputDirectory, null);
      assert.equal(f.deployed.length, 1);
      const { args, env } = f.deployed[0];
      assert.ok(args.includes('SECRET=never-build'));
      assert.equal(args[args.indexOf('SECRET=never-build') - 1], '--env');
      assert.equal(args[args.indexOf('PUBLIC_AUTH0_DOMAIN=auth.example') - 1], '--build-env');
      assert.equal(env.VERCEL_TOKEN, 'scoped-secret');
      assert.equal(env.VERCEL_PROJECT_ID, 'project');
      const saved = await readFile(join(cwd, '.private/fulcra-deployment.json'), 'utf8');
      assert.ok(!saved.includes('secret'));
      assert.equal((await stat(join(cwd, '.private/fulcra-deployment.json'))).mode & 0o777, 0o600);
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });

  test('domain mismatch stops before obtaining a deployment token', async () => {
    const cwd = await mkdtemp(join(tmpdir(), 'fulcra-deploy-'));
    const f = fixture();
    try {
      await assert.rejects(
        module.deployFulcra({
          cwd,
          name: 'sample',
          framework: 'sveltekit',
          expectedDomain: 'other.my.fulcra.ai',
          values: {},
          accessToken: 'token',
          fetchImpl: f.fetchImpl,
          run: f.run
        }),
        /domain/i
      );
      assert.equal(f.calls.length, 1);
      assert.equal(f.deployed.length, 0);
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });

  test('unavailable project settings stop before deploy; no external account fallback', async () => {
    const cwd = await mkdtemp(join(tmpdir(), 'fulcra-deploy-'));
    const f = fixture();
    try {
      await assert.rejects(
        module.deployFulcra({
          cwd,
          name: 'sample',
          framework: 'sveltekit',
          values: {},
          accessToken: 'token',
          fetchImpl: async (url, options) =>
            url.startsWith('https://api.vercel.com/')
              ? new Response('', { status: 403 })
              : f.fetchImpl(url, options),
          run: f.run
        }),
        /GET api.vercel.com\/v9\/projects\/project returned 403/
      );
      assert.equal(f.deployed.length, 0);
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });

  test('connector recovery fields survive deploy in its existing private state file', async () => {
    const cwd = await mkdtemp(join(tmpdir(), 'fulcra-deploy-'));
    const f = fixture();
    const fs = await import('node:fs/promises');
    try {
      await fs.mkdir(join(cwd, '.private'));
      await fs.writeFile(
        join(cwd, '.private/deployment.json'),
        JSON.stringify({
          project: f.project,
          nativeControllerRunId: 'keep-root',
          harnessType: 'keep-v1-type'
        })
      );
      await module.deployFulcra({
        cwd,
        name: 'sample',
        framework: 'sveltekit',
        stateFile: '.private/deployment.json',
        values: {},
        accessToken: 'token',
        fetchImpl: f.fetchImpl,
        run: f.run
      });
      const state = JSON.parse(await fs.readFile(join(cwd, '.private/deployment.json')));
      assert.equal(state.nativeControllerRunId, 'keep-root');
      assert.equal(state.harnessType, 'keep-v1-type');
      await assert.rejects(fs.stat(join(cwd, '.private/fulcra-deployment.json')), {
        code: 'ENOENT'
      });
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });

  test('keeps the pre-bootstrap rollback checkpoint across two deployments', async () => {
    const cwd = await mkdtemp(join(tmpdir(), 'fulcra-deploy-'));
    const f = fixture();
    try {
      const options = {
        cwd,
        name: 'sample',
        framework: 'sveltekit',
        values: {},
        accessToken: 'token',
        fetchImpl: f.fetchImpl,
        run: f.run
      };
      await module.deployFulcra(options);
      await module.deployFulcra({
        ...options,
        fetchImpl: async (url, init) => {
          const response = await f.fetchImpl(url, init);
          if (url.startsWith('https://api.vercel.com/') && !init?.method) {
            const body = await response.json();
            body.targets.production.id = 'bootstrap-deployment';
            return Response.json(body);
          }
          return response;
        }
      });
      const state = JSON.parse(await readFile(join(cwd, '.private/fulcra-deployment.json')));
      assert.equal(state.previousProductionDeploymentId, 'bootstrap-deployment');
      assert.equal(state.baselineProductionDeploymentId, 'previous-deployment');
    } finally {
      await rm(cwd, { recursive: true, force: true });
    }
  });

  test('rejects reserved Vercel system variable before any request', async () => {
    const f = fixture();
    await assert.rejects(
      module.deployFulcra({
        name: 'sample',
        framework: 'sveltekit',
        values: { DEPLOYMENT_ID: 'instance-id' },
        accessToken: 'token',
        fetchImpl: f.fetchImpl,
        run: f.run
      }),
      /reserved/i
    );
    assert.equal(f.calls.length, 0);
  });
}
