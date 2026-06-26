---
name: fulcra-ingest-magic-links
description: "Instructions for setting up webhooks (Magic Links) to allow external sources to push data directly to Fulcra without polling."
---

# Fulcra Magic Links (Webhooks)

Magic Links are dedicated, secure URLs that allow 3rd-party services (like GitHub, Zapier, IFTTT, or custom scripts) to push data directly into Fulcra, bypassing the need for an agent to constantly poll or run cron jobs.

## When to Use Magic Links
If a data source supports "Webhooks" or HTTP POST notifications (e.g., GitHub issue updates, Stripe payments, Slack messages), you should configure a Magic Link rather than setting up a local heartbeat/cron polling loop.

## Creating a Magic Link
You can generate a new magic link URL via the Fulcra CLI. 
When creating the link, you define where the incoming data should be stored in the user's File Store.

```bash
# Create a magic link that saves incoming payloads to a specific path
uv tool run fulcra-api magic-link create "ingest/github_webhooks/latest_payload.json"
```

The output will provide a unique URL.

## Magic Link URL Structure & Parameters

For direct data ingestion, Fulcra magic links have the following form:
`https://fulcra.io/e/<LINK ID>?value=<VALUE>&note=<NOTE>&tag=<TAG 1 UUID>&tag=<TAG 2 UUID>`

Notice how the magic link query parameters relate directly to the annotation recording data and metadata:
- `value`: Maps to the `data.value` field in the recorded annotation.
- `note`: Maps to the `data.note` field.
- `tag`: Maps to the `metadata.tags` array. You can include multiple `tag` parameters by passing the specific tag UUIDs.

*(Note: Exact CLI instructions for generating these parameterized links and retrieving the `<LINK ID>` will be provided in a future update. For now, ensure you understand how the URL parameters map to the underlying annotation schema.)*

## Configuring the External Source
Once you have the URL, provide it to the user or configure the 3rd-party service to send POST requests to it.

For example, if you are setting up GitHub webhooks:
1. Provide the user the Magic Link URL.
2. Instruct them to paste it into the "Payload URL" field in their GitHub repository webhook settings.
3. Tell them to set the content type to `application/json`.

## Processing Magic Link Data
Because the external service is now pushing data into the user's File Store (e.g., to `ingest/github_webhooks/latest_payload.json`), you can set up a background file watcher or instruct the `Librarian` agent to check that specific path periodically to process the newly arrived data just like any other uploaded file.

**Note:** If multiple pushes happen rapidly, the file at that path will be overwritten with the latest payload. Because Fulcra's File Store is versioned, previous payloads are not permanently lost, but typical magic link ingest scripts should process and archive the file quickly to maintain a clear pipeline.
