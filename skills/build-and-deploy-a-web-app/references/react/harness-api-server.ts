import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import { FulcraAPI } from '@/lib/api-client';
// See references/react/harness-owner.ts — copy it to lib/server/harness-owner.ts
import { isOwner } from '@/lib/server/harness-owner';

/**
 * Server-side endpoints for the harness dashboard (Next.js app router).
 *
 * App-router route handlers each live in their own file, so create four:
 * - app/api/harness/runs/route.ts      (export the GET_runs body as GET)
 * - app/api/harness/issues/route.ts    (export the GET_issues body as GET)
 * - app/api/harness/overview/route.ts  (export the GET_overview body as GET)
 * - app/api/harness/owner/route.ts     (export the GET_owner body as GET)
 *
 * Each file imports { FulcraAPI } from '@/lib/api-client', { isOwner } from
 * '@/lib/server/harness-owner', and the shared fetchWorkspaceFileText helper
 * below (copy it into a small module, e.g. lib/server/harness-files.ts, or
 * inline it). The functions below are named GET_* only to show all four in one
 * reference — rename each to `GET` in its own route file.
 *
 * The owner's user id is a server-only env var (OWNER_USER_ID, no NEXT_PUBLIC_
 * prefix). runs/issues/overview enforce ownership; owner reports it to the
 * client so the dashboard/nav can gate visibility without ever seeing the id.
 *
 * The dashboard must fetch through these routes (never the Fulcra API directly)
 * to avoid CORS and to keep the token server-side. Endpoints are documented at
 * https://docs.fulcradynamics.com/rest-api/.
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
async function fetchWorkspaceFileText(
  endpoint: string,
  accessToken: string,
  workspacePath: string,
  fileName: string
): Promise<string | null> {
  const folder = workspacePath.startsWith('/') ? workspacePath : `/${workspacePath}`;
  const apiClient = new FulcraAPI(endpoint, accessToken);
  const listing = await apiClient.get(`input/v1/file?path=${encodeURIComponent(folder)}`);
  const file = (listing?.files || []).find((f: { name: string }) => f.name === fileName);
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

// app/api/harness/runs/route.ts  → export this as GET
export async function GET_runs(request: Request) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('fulcra_access_token')?.value;

  if (!accessToken) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  // Only the harness owner may read run history.
  if (!isOwner(accessToken)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const url = new URL(request.url);
  const annotationId = url.searchParams.get('annotation_id');
  // Default to a rolling 30-day window ending today when the client omits dates.
  const now = new Date();
  const startDate =
    url.searchParams.get('start_date') ||
    new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  const endDate = url.searchParams.get('end_date') || now.toISOString().slice(0, 10);

  if (!annotationId) {
    return NextResponse.json({ error: 'annotation_id parameter required' }, { status: 400 });
  }

  try {
    const apiClient = new FulcraAPI(process.env.NEXT_PUBLIC_FULCRA_API_ENDPOINT!, accessToken);
    // See API docs: https://docs.fulcradynamics.com/rest-api/
    // GET /data/v1alpha1/event/{data_type}?start_time=<ISO8601>&end_time=<ISO8601>
    const dataType = annotationId.replace('/', '%2F');
    const records = await apiClient.get(
      `data/v1alpha1/event/${dataType}?start_time=${startDate}T00:00:00Z&end_time=${endDate}T23:59:59Z`
    );
    return NextResponse.json(records);
  } catch (err) {
    console.error('Error fetching harness runs:', err);
    const message = err instanceof Error ? err.message : '';
    // No data yet for this annotation
    if (message.includes('404')) {
      return NextResponse.json({ records: [] });
    }
    // Expired/invalid token: surface as 401 so the client can re-authenticate
    if (message.includes('401')) {
      return NextResponse.json({ error: 'Session expired — please sign in again' }, { status: 401 });
    }
    return NextResponse.json({ error: message || 'Failed to fetch harness runs' }, { status: 500 });
  }
}

// app/api/harness/issues/route.ts  → export this as GET
export async function GET_issues(request: Request) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('fulcra_access_token')?.value;

  if (!accessToken) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  // Only the harness owner may read the outstanding-issues file.
  if (!isOwner(accessToken)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const url = new URL(request.url);
  const workspacePath = url.searchParams.get('workspace_path');

  if (!workspacePath) {
    return NextResponse.json({ error: 'workspace_path parameter required' }, { status: 400 });
  }

  try {
    const content = await fetchWorkspaceFileText(
      process.env.NEXT_PUBLIC_FULCRA_API_ENDPOINT!,
      accessToken,
      workspacePath,
      'outstanding-issues.md'
    );
    // Empty string when there are no outstanding issues recorded yet.
    return new NextResponse(content ?? '', { headers: { 'Content-Type': 'text/plain' } });
  } catch (err) {
    console.error('Error fetching outstanding issues:', err);
    return new NextResponse('', { headers: { 'Content-Type': 'text/plain' } });
  }
}

// app/api/harness/overview/route.ts  → export this as GET
// The nurse rewrites overview.md each loop: a concise summary of overall
// progress plus the milestone list. The dashboard renders it at the top.
export async function GET_overview(request: Request) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('fulcra_access_token')?.value;

  if (!accessToken) {
    return NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
  }

  // Only the harness owner may read the overview file.
  if (!isOwner(accessToken)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const url = new URL(request.url);
  const workspacePath = url.searchParams.get('workspace_path');

  if (!workspacePath) {
    return NextResponse.json({ error: 'workspace_path parameter required' }, { status: 400 });
  }

  try {
    const content = await fetchWorkspaceFileText(
      process.env.NEXT_PUBLIC_FULCRA_API_ENDPOINT!,
      accessToken,
      workspacePath,
      'overview.md'
    );
    // Empty string when the nurse hasn't written the overview yet.
    return new NextResponse(content ?? '', { headers: { 'Content-Type': 'text/plain' } });
  } catch (err) {
    console.error('Error fetching overview:', err);
    return new NextResponse('', { headers: { 'Content-Type': 'text/plain' } });
  }
}

// app/api/harness/owner/route.ts  → export this as GET
// Reports whether the caller is the owner without exposing the owner id.
export async function GET_owner() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('fulcra_access_token')?.value;
  return NextResponse.json({ isOwner: isOwner(accessToken) });
}
