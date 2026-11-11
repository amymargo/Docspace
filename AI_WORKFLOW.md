# AI workflow note

- **Tools used:** OpenAI Codex in the terminal workspace.
- **Where AI helped:** turning the broad assignment into a small product slice, drafting the Python API/data model and browser UI, and preparing setup and architecture notes.
- **What I changed or constrained:** used only the Python standard library and SQLite to keep local setup free of third-party services; chose seeded identities and read-only sharing instead of implying secure authentication or conflict-safe collaboration; restricted imports to `.txt` and `.md`.
- **Verification:** added an automated API test covering document creation, owner visibility, share grant, recipient visibility, preserved content, and rejection of recipient writes. Review the interface manually by following the demo flow in README. The project has not been deployed, so no live-host behavior has been verified.
