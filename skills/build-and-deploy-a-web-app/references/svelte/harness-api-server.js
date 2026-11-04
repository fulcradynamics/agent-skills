import { env } from '$env/dynamic/public';
import { env as privateEnv } from '$env/dynamic/private';
import { error, json } from '@sveltejs/kit';
import { isOwner } from '$lib/server/harness-owner.js';
import { parseRecords, recordsQuery } from '$lib/harness-state.js';

// Copy to src/lib/server/harness-api-server.js; route files re-export handlers.
// The claim gate is unchanged. Every data read also forwards the caller's token
// to Fulcra for signature/expiry and per-user authorization checks.
/** @param {import('@sveltejs/kit').RequestEvent} event */
export async function GET_runs({ cookies, url, fetch }) {
  const accessToken = cookies.get('fulcra_access_token');
  if (!accessToken) throw error(401, 'Not authenticated');
  if (!isOwner(accessToken)) throw error(403, 'Forbidden');

  let query;
  const dataType = privateEnv.HARNESS_DATA_TYPE || '';
  try {
    // Check server configuration independently of client range errors.
    query = recordsQuery(dataType);
  } catch {
    throw error(500, 'Configure HARNESS_DATA_TYPE as Event/<UUID>');
  }
  if (url.searchParams.get('mode') !== 'latest') {
    try {
      query = recordsQuery(dataType, url.searchParams.get('start'), url.searchParams.get('end'));
    } catch {
      throw error(400, 'Provide valid start and end timestamps, or mode=latest');
    }
  }

  const endpoint = new URL('data/v1/records', env.PUBLIC_FULCRA_API_ENDPOINT);
  endpoint.searchParams.set('q', query);
  let response;
  try {
    response = await fetch(endpoint, {
      headers: { Authorization: `Bearer ${accessToken}` },
      signal: AbortSignal.timeout(15000)
    });
  } catch {
    throw error(502, 'Harness upstream request failed');
  }
  if (!response.ok) {
    const status = [401, 403].includes(response.status) ? response.status : 502;
    throw error(status, `Harness upstream returned ${response.status}`);
  }
  try {
    const records = parseRecords(await response.text());
    return json({ records }, { headers: { 'Cache-Control': 'private, no-store' } });
  } catch {
    throw error(502, 'Invalid harness records from upstream');
  }
}

/** @param {import('@sveltejs/kit').RequestEvent} event */
export async function GET_owner({ cookies }) {
  return json({ isOwner: isOwner(cookies.get('fulcra_access_token')) }, {
    headers: { 'Cache-Control': 'private, no-store' }
  });
}
