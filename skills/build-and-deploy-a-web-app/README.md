# build-and-deploy-a-web-app

Build your own web app on Fulcra and deploy it to a live address.

Tell your agent what you want to make. It turns the idea into a plan that uses what Fulcra offers (sign-in, saved user data, sharing between users, file storage), starts from an official Svelte or React template with sign-in already working, and deploys it to a my.fulcra.ai subdomain. You don't need a hosting account.

The app is built in small milestones. Each one is generated, then checked separately against the live app before it counts as done. Your plan, spec, decisions, and history are kept in a Fulcra workspace, so you or another agent can pick the project back up and keep improving it. A dashboard inside the app, visible only to you, shows each milestone's runs and evaluation results.

Built on the Fulcra app templates, `fulcra-api`, and Fulcra deploy projects.

Deployment instructions and a [reusable helper](scripts/deploy-fulcra.mjs) are included in [the deploy reference](references/deploy.md), including reuse of an already-owned namespace. Apps needing durable cursors or periodic background work can use the [native state and scheduling pattern](references/native-state-and-scheduling.md) through the same Fulcra deployment; a separate database/hosting account is not the default requirement.
