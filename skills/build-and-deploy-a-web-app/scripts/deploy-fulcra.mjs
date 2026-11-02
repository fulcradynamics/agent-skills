import { execFileSync, spawn } from 'node:child_process';
import { mkdir, readFile, rename, writeFile, chmod } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseEnv } from 'node:util';

// Standalone: copy this file into a generated app's scripts/ directory.
// No token is persisted. Project identity is saved before platform mutation.
export async function deployFulcra({
  cwd = process.cwd(),
  name,
  framework = 'sveltekit',
  expectedDomain,
  values,
  accessToken,
  stateFile = '.private/fulcra-deployment.json',
  fetchImpl = fetch,
  run = runVercel
} = {}) {
  if (!['sveltekit', 'nextjs'].includes(framework))
    throw Error('Framework must be sveltekit or nextjs');
  if (!name || !/^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/.test(name))
    throw Error('Supply the authorized Fulcra namespace name');
  values ??= parseEnv(await readFile(join(cwd, '.env'), 'utf8'));
  for (const key of Object.keys(values)) {
    if (key === 'DEPLOYMENT_ID' || key.startsWith('VERCEL_'))
      throw Error(`${key} is reserved by Vercel; use an app-prefixed instance variable`);
  }
  accessToken ??= execFileSync('uvx', ['fulcra-api', 'auth', 'print-access-token'], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe']
  }).trim();
  if (!accessToken) throw Error('Fulcra CLI authentication required');
  async function json(url, options = {}, bearer = accessToken) {
    const response = await fetchImpl(url, {
      ...options,
      headers: { Authorization: `Bearer ${bearer}`, 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(30000)
    });
    // Error bodies may contain credentials or implementation details: report only status.
    if (!response.ok) {
      const endpoint = new URL(url);
      throw Error(
        `${options.method || 'GET'} ${endpoint.host}${endpoint.pathname} returned ${response.status}; preserve the existing project and resolve this operation's access/configuration`
      );
    }
    return response.json();
  }
  const directory = join(cwd, '.private'),
    statePath = join(cwd, stateFile);
  let state;
  try {
    state = JSON.parse(await readFile(statePath, 'utf8'));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    state = {};
  }
  const api = 'https://api.fulcradynamics.com';
  // Check current ownership even on redeploy. Never deploy solely from copied metadata.
  const projects = await json(`${api}/user/v1/deploy/project`);
  if (!Array.isArray(projects)) throw Error('Unexpected owned project list');
  const owned = projects.filter((p) => p.name === name);
  if (owned.length > 1) throw Error('Ambiguous namespace; resolve the owned project identity');
  if (
    state.project &&
    (state.project.name !== name ||
      !owned.some((p) => p.id === state.project.id && p.domain === state.project.domain))
  )
    throw Error(
      'Saved project does not match the currently owned namespace; recover metadata before deploying'
    );
  const project =
    state.project ??
    owned[0] ??
    (await json(`${api}/user/v1/deploy/project`, {
      method: 'POST',
      body: JSON.stringify({ name, framework })
    }));
  if (!project.id || !project.domain || project.name !== name)
    throw Error('Incomplete deployment project identity');
  if (expectedDomain && project.domain !== expectedDomain)
    throw Error('Unexpected deployment domain');
  state.project = project;
  await mkdir(directory, { recursive: true, mode: 0o700 });
  await chmod(directory, 0o700);
  async function save() {
    const temp = statePath + '.tmp';
    await writeFile(temp, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
    await chmod(temp, 0o600);
    await rename(temp, statePath);
  }
  await save();
  const credentials = await json(
    `${api}/user/v1/deploy/project/${encodeURIComponent(project.id)}/token`,
    { method: 'POST' }
  );
  if (!credentials.token || !credentials.platform_team_id || !credentials.platform_project_id)
    throw Error('Incomplete scoped credentials');
  const settingsURL = `https://api.vercel.com/v9/projects/${encodeURIComponent(credentials.platform_project_id)}?teamId=${encodeURIComponent(credentials.platform_team_id)}`;
  const wanted = {
    framework,
    buildCommand: 'npm run build',
    outputDirectory: null,
    nodeVersion: '24.x',
    autoExposeSystemEnvs: true
  };
  let settings = await json(settingsURL, {}, credentials.token);
  state.previousProductionDeploymentId = settings.targets?.production?.id ?? null;
  if (!Object.hasOwn(state, 'baselineProductionDeploymentId')) {
    state.baselineProductionDeploymentId = state.previousProductionDeploymentId;
    state.baselineProjectSettings = Object.fromEntries(
      [
        'framework',
        'buildCommand',
        'outputDirectory',
        'nodeVersion',
        'autoExposeSystemEnvs',
        'resourceConfig'
      ].map((key) => [key, settings[key] ?? null])
    );
  }
  state.beforeDeploySettings = Object.fromEntries(
    [
      'framework',
      'buildCommand',
      'outputDirectory',
      'nodeVersion',
      'autoExposeSystemEnvs',
      'resourceConfig'
    ].map((key) => [key, settings[key] ?? null])
  );
  await save(); // rollback identity/settings survive a failed PATCH or interrupted deployment
  const mismatch =
    Object.entries(wanted).some(([key, value]) => settings[key] !== value) ||
    settings.resourceConfig?.fluid !== true;
  if (mismatch) {
    await json(
      settingsURL,
      { method: 'PATCH', body: JSON.stringify({ ...wanted, resourceConfig: { fluid: true } }) },
      credentials.token
    );
    settings = await json(settingsURL, {}, credentials.token);
  }
  if (
    Object.entries(wanted).some(([key, value]) => settings[key] !== value) ||
    settings.resourceConfig?.fluid !== true
  )
    throw Error(
      'Project runtime/build settings did not persist; do not deploy over the working alias'
    );
  state.preflight = { ...wanted, fluid: true, checkedAt: new Date().toISOString() };
  await save();
  const args = ['--yes', '--engine-strict=false', 'vercel', 'deploy', '--prod', '--yes'];
  for (const [key, value] of Object.entries(values)) {
    if (key.startsWith('PUBLIC_') || key.startsWith('NEXT_PUBLIC_'))
      args.push('--build-env', `${key}=${value}`);
    args.push('--env', `${key}=${value}`);
  }
  const code = await run(
    args,
    {
      ...process.env,
      VERCEL_TOKEN: credentials.token,
      VERCEL_ORG_ID: credentials.platform_team_id,
      VERCEL_PROJECT_ID: credentials.platform_project_id
    },
    cwd
  );
  if (code !== 0)
    throw Error('Deployment failed; retain metadata and inspect build logs before retrying');
  return { project, url: `https://${project.domain}` };
}

async function runVercel(args, env, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn('npx', args, { cwd, env, stdio: 'inherit' });
    child.once('error', reject);
    child.once('exit', resolve);
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const [name, framework = 'sveltekit', expectedDomain] = process.argv.slice(2);
  try {
    const result = await deployFulcra({ name, framework, expectedDomain });
    console.log(
      `Deployed ${result.url}; evaluate authentication and real data before marking complete.`
    );
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
