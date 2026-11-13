import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
const source = readFileSync(new URL('../../skills/build-and-deploy-a-web-app/references/svelte/HarnessDashboard.svelte', import.meta.url), 'utf8');
test('latest navigation button remains rendered inside latest overview without selection condition', () => {
  assert.ok(source.includes('<button onclick={viewLatest}>View latest run</button>'));
  assert.ok(!source.includes('{#if selected !== latest.run_id}'));
  assert.match(source, /bind:this={selectedRunSection}/);
});
for (const [selected, reduced] of [['latest', false], ['old', false], ['latest', true], ['old', true]]) {
  test(`latest navigation scrolls when selected=${selected}, reduced=${reduced}`, async () => {
    const match = source.match(/async function viewLatest\(\) \{([\s\S]*?)\n  \}/);
    assert.ok(match, 'dedicated click handler exists');
    const calls=[];
    const context={latest:{run_id:'latest'},selected,matchMedia:()=>({matches:reduced}),tick:async()=>calls.push('tick'),selectedRunSection:{scrollIntoView:opts=>calls.push(opts)}};
    context.openRun=run=>{calls.push(run.run_id);context.selected=run.run_id;return new Promise(()=>{});};
    vm.createContext(context);
    await vm.runInContext(`(async()=>{${match[1]}})()`,context);
    assert.equal(context.selected,'latest');
    assert.equal(calls.filter(x=>x==='latest').length,selected==='old'?1:0);
    assert.equal(calls.at(-1).behavior,reduced?'auto':'smooth');
    assert.equal(calls.at(-1).block,'start');
    assert.ok(calls.includes('tick'));
  });
}
