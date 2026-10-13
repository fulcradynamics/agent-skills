# build-and-deploy-a-web-app

**Build a web app on Fulcra and put it online at its own address.**

Describe the app you want to your agent. It will plan the app, build it on Fulcra, and publish it to an address like `your-app.my.fulcra.ai`. You don't need a hosting account of your own for that address.

**What your app can do**
- Sign people in with their Fulcra account
- Save data for each user
- Share data and files between users
- Store files of any type

**How it's built**
The agent starts from a ready-made template in Svelte or React (two common ways to build websites) that already includes sign-in. It then builds the app in small steps, checking each step against the live app before moving on.

**Your work is saved**
Your plan, spec, decisions, and history are kept in a Fulcra workspace, so you or another agent can pick the project up later and keep improving it. A private dashboard, visible only to you, shows the evaluation results for each step.

**Built with:** Fulcra app templates, the `fulcra-api` library, and Fulcra deploy projects.

---

## For developers

- **Templates:** [Svelte](https://github.com/fulcradynamics/app-template-svelte) (default) or [React](https://github.com/fulcradynamics/app-template-react), both with Fulcra sign-in already working.
- **Account:** a Fulcra account. Accounts start free with 5 GB of storage, with paid plans beyond that.
- **Deployment:** apps deploy to a `my.fulcra.ai` subdomain through Fulcra deploy projects, with no Vercel account needed. A custom domain requires your own Vercel or other hosting account.
- **Code:** the generated app is an ordinary Svelte or React project in its own git repository, so you can read and edit it directly.
- **Workspace:** the plan, spec, decisions, progress, and run history live in Fulcra File Store under `workspace/<project-name>/`.
- **Skill source:** [SKILL.md](SKILL.md) and the [references](references/) folder describe the full build, evaluation, and deploy process.
