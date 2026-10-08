import { env } from '$env/dynamic/public';
import { error, json } from '@sveltejs/kit';
import { FulcraAPI } from '$lib/api-client.js';
// See references/svelte/harness-owner.js — copy it to src/lib/server/harness-owner.js
import { isOwner } from '$lib/server/harness-owner.js';

/**
 * Server-side endpoints for harness dashboard
 *
 * Place at: src/routes/api/harness/
 * Create four files:
 * - runs/+server.js     (export GET_runs as GET)
 * - issues/+server.js   (export GET_issues as GET)
 * - overview/+server.js (export GET_overview as GET)
 * - owner/+server.js    (export GET_owner as GET)
 *
 * The owner's user id is a server-only env var (OWNER_USER_ID, no PUBLIC_
 * prefix). runs/issues/overview enforce ownership; owner reports it to the
 * client so the dashboard/nav can gate visibility without ever seeing the id.
 */

/**
 * Read the text contents of a file stored under a workspace folder.
 *
 * Fulcra's file API is two-step: list the folder to resolve the file's input
 * id, then download by that id. Folder paths are absolute, so a leading slash
 * is added when missing. The download endpoint returns raw text (not JSON), so
 * it is fetched directly rather than through the JSON-parsing client. Returns
 * null when the file doesn't exist yet.
 *
 * See: GET /input/v1/file?path=<folder> and
 *      GET /input/v1/file/{input_id}/download
 */
async function fetchWorkspaceFileText(endpoint, accessToken, workspacePath, fileName) {
  const folder = workspacePath.startsWith('/') ? workspacePath : `/${workspacePath}`;
  const apiClient = new FulcraAPI(endpoint, accessToken);
  const listing = await apiClient.get(`input/v1/file?path=${encodeURIComponent(folder)}`);
  const file = (listing?.files || []).find((f) => f.name === fileName);
  if (!file) {
    return null;
  }

  const response = await fetch(`${endpoint}input/v1/file/${file.id}/download`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return await response.text();
}

// runs/+server.js
export async function GET_runs({ cookies, url }) {
  const accessToken = cookies.get('fulcra_access_token');

  if (!accessToken) {
    throw error(401, 'Not authenticated');
  }

  // Only the harness owner may read run history.
  if (!isOwner(accessToken)) {
    throw error(403, 'Forbidden');
  }

  const annotationId = url.searchParams.get('annotation_id');
  // Default to a rolling 30-day window ending today when the client omits dates.
  const now = new Date();
  const startDate =
    url.searchParams.get('start_date') ||
    new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const endDate = url.searchParams.get('end_date') || now.toISOString().slice(0, 10);

  if (!annotationId) {
    throw error(400, 'annotation_id parameter required');
  }

  try {
    const apiClient = new FulcraAPI(env.PUBLIC_FULCRA_API_ENDPOINT, accessToken);
    // See API docs: https://docs.fulcradynamics.com/rest-api/
    // GET /data/v1alpha1/event/{data_type}?start_time=<ISO8601>&end_time=<ISO8601>
    const dataType = annotationId.replace('/', '%2F');
    const records = await apiClient.get(`data/v1alpha1/event/${dataType}?start_time=${startDate}T00:00:00Z&end_time=${endDate}T23:59:59Z`);
    return json(records);
  } catch (err) {
    console.error('Error fetching harness runs:', err);
    // No data yet for this annotation
    if (err.message?.includes('404')) {
      return json({ records: [] });
    }
    // Expired/invalid token: surface as 401 so the client can re-authenticate
    if (err.message?.includes('401')) {
      throw error(401, 'Session expired — please sign in again');
    }
    throw error(500, err.message || 'Failed to fetch harness runs');
  }
}

// issues/+server.js
export async function GET_issues({ cookies, url }) {
  const accessToken = cookies.get('fulcra_access_token');

  if (!accessToken) {
    throw error(401, 'Not authenticated');
  }

  // Only the harness owner may read the outstanding-issues file.
  if (!isOwner(accessToken)) {
    throw error(403, 'Forbidden');
  }

  const workspacePath = url.searchParams.get('workspace_path');

  if (!workspacePath) {
    throw error(400, 'workspace_path parameter required');
  }

  try {
    const content = await fetchWorkspaceFileText(
      env.PUBLIC_FULCRA_API_ENDPOINT,
      accessToken,
      workspacePath,
      'outstanding-issues.md'
    );
    // Empty string when there are no outstanding issues recorded yet.
    return new Response(content ?? '', {
      headers: { 'Content-Type': 'text/plain' }
    });
  } catch (err) {
    console.error('Error fetching outstanding issues:', err);
    return new Response('', {
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// overview/+server.js
// The nurse rewrites overview.md each loop: a concise summary of overall
// progress plus the milestone list. The dashboard renders it at the top.
export async function GET_overview({ cookies, url }) {
  const accessToken = cookies.get('fulcra_access_token');

  if (!accessToken) {
    throw error(401, 'Not authenticated');
  }

  // Only the harness owner may read the overview file.
  if (!isOwner(accessToken)) {
    throw error(403, 'Forbidden');
  }

  const workspacePath = url.searchParams.get('workspace_path');

  if (!workspacePath) {
    throw error(400, 'workspace_path parameter required');
  }

  try {
    const content = await fetchWorkspaceFileText(
      env.PUBLIC_FULCRA_API_ENDPOINT,
      accessToken,
      workspacePath,
      'overview.md'
    );
    // Empty string when the nurse hasn't written the overview yet.
    return new Response(content ?? '', {
      headers: { 'Content-Type': 'text/plain' }
    });
  } catch (err) {
    console.error('Error fetching overview:', err);
    return new Response('', {
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// owner/+server.js
// Reports whether the caller is the owner without exposing the owner id.
export async function GET_owner({ cookies }) {
  const accessToken = cookies.get('fulcra_access_token');
  return json({ isOwner: isOwner(accessToken) });
}
