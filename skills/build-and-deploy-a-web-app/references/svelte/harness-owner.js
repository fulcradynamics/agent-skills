import { env as privateEnv } from '$env/dynamic/private';

/**
 * Ownership check for the harness dashboard.
 *
 * The owner's Fulcra user id lives in the server-only OWNER_USER_ID env var
 * (no PUBLIC_ prefix), so it is never shipped to the browser. The caller's id
 * is read from the `fulcradynamics.com/userid` claim already carried in their
 * Fulcra access token (the JWT in the HTTP-only cookie): no network call is
 * made here, and the identity provider is only contacted once — at login, to
 * mint the token.
 *
 * We read the claim without re-verifying the JWT signature. The cookie is set
 * server-side after the Auth0 device flow, and every data request forwards the
 * same token to the Fulcra API, which rejects anything it did not issue — so a
 * forged token cannot return data even if it slipped past this gate.
 *
 * @param {string | undefined} accessToken - Fulcra access token from the cookie.
 * @returns {boolean} true only when the caller is the configured owner.
 */
export function isOwner(accessToken) {
  const ownerId = privateEnv.OWNER_USER_ID;
  if (!accessToken || !ownerId) return false;

  try {
    const payload = accessToken.split('.')[1];
    if (!payload) return false;
    const claims = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
    return claims['fulcradynamics.com/userid'] === ownerId;
  } catch {
    return false;
  }
}
