# build-and-deploy-a-web-app

Build your own web app on Fulcra and deploy it to a live address.

Tell your agent what you want to make. It turns the idea into a plan that uses what Fulcra offers (sign-in, saved user data, sharing between users, file storage), starts from the official SvelteKit template with sign-in already working, and deploys it to a my.fulcra.ai subdomain. You don't need a hosting account.

The app is built in small milestones. The Coordinator chooses light, focused or full checks with a reason: visual checks for presentation-only work, affected tests and user journeys for contained changes, and a separate evaluator for new, complex or security-sensitive work. The first baseline milestone always uses full deployed checks. Every tier needs real evidence, not just a successful build.

Your full spec, compact plan, current decisions and progress stay in a Fulcra workspace, with all run outcomes and older decisions preserved in history. Roles share startup context; workspace writes happen at closure. Interrupted attempts are stopped and closed before a fresh run starts within retry limits; inspected code and resources can be reused, not assumed passes. Bookkeeping failures do not require rebuilding verified work.

The owner-only Svelte dashboard shows live summary, tier/reason, actual steps, next actions, Nurse interventions and expandable evidence/history from structured v1 Event records. It keeps a five-second refresh cadence without polling workspace files. Existing apps use a deliberate upgrade that preserves old history and deployment IDs; legacy note records are not silently migrated.

Public pages are intended to be findable in search. Your agent confirms that choice before deployment and can discourage indexing if you prefer. Private data and the owner dashboard remain protected either way; search settings are not access controls.

Built on the Fulcra app templates, `fulcra-api`, and Fulcra deploy projects.
