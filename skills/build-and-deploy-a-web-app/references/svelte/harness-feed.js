import { groupRuns, mergeEvents, pollStart, selectedRunId } from './harness-state.js';

// Owns query/cursor state, not timers or rendering. The caller handles errors.
export class HarnessFeed {
  /** @param {(params: Record<string, string>) => Promise<Record<string, any>[]>} read */
  constructor(read) {
    this.read = read;
    /** @type {Record<string, any>[]} */
    this.events = [];
    /** @type {string | null} */
    this.selected = null;
    /** @type {string | null} */
    this.current = null;
    /** @type {string | null} */
    this.lastRead = null;
    this.polls = 0;
    this.busy = false;
    /** @type {Array<() => void>} */
    this.historyQueue = [];
  }

  async refresh(now = new Date().toISOString()) {
    if (this.busy) return;
    this.busy = true;
    try {
      const latest = await this.read({ mode: 'latest' });
      const current = groupRuns(latest)[0];
      let incoming = latest;
      if (current) {
        const changed = current.run_id !== this.current;
        const start = pollStart(current.run_start, changed ? null : this.lastRead, this.polls % 12 === 0);
        incoming = mergeEvents(incoming, await this.read({ start, end: now }));
        // Reconcile the previous run once on transition; it may have ended
        // between polls. Historical runs are reconciled when opened explicitly.
        const previous = groupRuns(this.events).find(run => run.run_id === this.current);
        if (changed && previous) incoming = mergeEvents(incoming, await this.read({start: previous.run_start, end: now}));
      }
      this.events = mergeEvents(this.events, incoming);
      this.current = current?.run_id || this.current;
      this.selected = selectedRunId(this.selected, groupRuns(this.events));
      this.lastRead = now;
      this.polls++;
    } finally {
      this.release();
    }
  }

  release() {
    const next = this.historyQueue.shift();
    // Transfer ownership without exposing an idle gap to the polling timer.
    if (next) next();
    else this.busy = false;
  }

  /** @param {string} start @param {string} end */
  async history(start, end) {
    // Explicit clicks must survive a slow poll or another history request.
    if (this.busy) await new Promise(resolve => this.historyQueue.push(() => resolve(undefined)));
    else this.busy = true;
    try {
      this.events = mergeEvents(this.events, await this.read({ start, end }));
      return true;
    } finally {
      this.release();
    }
  }
}
