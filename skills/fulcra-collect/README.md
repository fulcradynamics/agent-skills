# fulcra-collect

Portable agent skill for creating Fulcra annotation types and recording consented user data through the Fulcra CLI.

Primary dependency:

```bash
uv tool run fulcra-api
```

Auth boundary:

- Agents may show users Fulcra auth URLs and device codes.
- Agents must not ask users to paste tokens, credential files, or private records into chat.
- Writes require clear user consent.
