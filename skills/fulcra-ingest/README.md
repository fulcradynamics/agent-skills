# fulcra-ingest

Gets the data you already own — out of a download folder, or straight off an API — and into somewhere it is useful.

Most services will give you your data if you ask — Spotify, Netflix, and the rest will email you an export. What arrives is a zip of CSVs and JSON in whatever shape that company happened to pick, which is why those exports usually get downloaded once and never opened again.

This skill does the unglamorous part. Point it at an export you have uploaded to your Fulcra file store, and it works out what the file actually contains, maps it onto Fulcra annotations, and ingests it — preserving where each record came from and how confident the match was.

You do not have to start from a downloaded file. Point it at an API instead — or a local service, or a CLI tool on your machine — and it will fetch the data for you first, then land it in the file store and carry on down the same mapping and ingest path. It asks before reaching out to anything external, and confirms what is being collected, where it goes, and how often. That last part is what turns a one-time import into something that keeps up on its own.

The result is that a Netflix export stops being a file and starts being data you can query alongside everything else you have, by any agent you have given access.

Supports multiple export formats, and keeps provenance so you can always tell what came from where.
