# Search discoverability

## Confirm before deployment

Recommend making the app's public pages findable in search engines. Ask:
“Your app's public pages will be eligible to appear in search results. Is that
OK, or would you prefer to discourage search indexing?” Wait for the answer
before the first public deployment. Record it in `decisions.md` and the spec;
do not silently infer consent. For an existing app, preserve its recorded choice
unless the user explicitly changes it.

Indexability is not a promise of search placement or immediate indexing. Neither
an unlisted URL nor crawler directives provide access control: private data and
the owner-only harness must remain protected by authentication and authorization.

## Default: discoverable public pages

The SvelteKit template already server-renders the public sign-in page and does
not block indexing. Preserve that behavior:

- Give public pages an app-specific title, description, and meaningful public
  content in the server-rendered HTML. Customize copy, not authentication.
- Do not add site-wide `noindex`, `nofollow`, `X-Robots-Tag: noindex`, or
  `Disallow: /` rules. Check existing app code and hosting configuration for
  conflicting directives rather than assuming the template controls them all.
- Keep links to public pages crawlable. For multi-page apps, include only public,
  canonical production URLs in a sitemap; do not publish private routes or data.
- Keep authenticated pages, APIs, and `/harness` protected. Exclude private pages
  from indexing with route-specific `noindex` where appropriate; never remove
  access checks to make the site discoverable.

No `robots.txt` is required to permit crawling. If one exists, allow public pages
and the assets needed to render them. Do not use preview URLs as canonical URLs.

## Opt-out: discourage indexing

If the user opts out, add this inside `<head>` in `src/app.html` so it is present
in the initial HTML of every page, including before JavaScript runs:

```html
<meta name="robots" content="noindex, nofollow" />
```

For public non-HTML resources that should also stay out of search, configure an
`X-Robots-Tag: noindex, nofollow` response header on those resources at the server
or hosting layer. Do not expose private resources in the first place.

Do **not** pair `noindex` with `Disallow: /`: crawlers must be able to fetch the
page to read the directive, and blocked URLs may still appear in search results.
Do not advertise opted-out pages in a sitemap. Explain that compliant crawlers
honor these signals, but they do not prevent sharing, unauthorized access, or
immediately remove previously indexed pages. Use authentication when privacy is
required.

If the user later opts in, remove the site-wide opt-out directives and recheck
hosting headers and crawler rules, without removing protections on private pages.

## Evaluate before handoff

Include these checks in M1's review and repeat them after changes to routing,
metadata, hosting configuration, or the user's discoverability choice:

1. Fetch the canonical production URL without a session cookie. Confirm a `200`
   response and useful public HTML, including its title and description. Verify
   private user data is absent and sign-in still works.
2. Inspect the response headers, initial HTML, and `/robots.txt` (a `404` is fine
   when no file is configured). For the discoverable choice, public pages must
   not carry `noindex` or be blocked from crawling. For opt-out, verify the
   `noindex, nofollow` meta tag is in the initial HTML, no conflicting crawler
   block prevents reading it, and any relevant non-HTML headers are present.
3. Verify unauthenticated requests still cannot retrieve private API data or
   owner-only harness data. Check any sitemap includes only intended public URLs.
4. Record the user's choice, tested production URL, commands, and observed
   headers/HTML in the review evidence. A local build does not establish the
   deployed policy: hosting-level headers or deployment protection can differ.
