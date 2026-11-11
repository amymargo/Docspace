# Docspace

A small, full-stack shared document editor built for Amy Margolina's AI-Native Full Stack Developer assignment. The project intentionally focuses on a coherent document lifecycle: create, edit, autosave, reopen, import plain text/Markdown, and share read-only access with another workspace user.

## Run locally

Requirements: Python 3.9+; no third-party packages or paid services.

```bash
python3 server.py
```

Open [http://localhost:8000](http://localhost:8000). SQLite is created automatically at `documents.db` next to `server.py`. Set `PORT` to change the port, or `DOCS_DB=/path/to/file.sqlite` to choose the database file.

### Demo users

Use the account menu in the top bar to switch identity:

- Amy Margolina — `amy@example.com` (default owner)
- Alex Rivera — `alex@example.com`
- Sam Chen — `sam@example.com`

Create a document as Amy, choose **Share**, and grant Alex or Sam access. Switch to that user to see the document marked **Shared**. Shared users can edit document content; owners retain control of sharing, renaming, and deletion. Open documents sync saved edits from other users when the editor is not actively focused. This seeded identity switch remains a demo model, not production authentication.

### Import support

The editor accepts `.txt` and `.md` files up to 1 MB; Word `.doc` and `.docx` files are not supported. Import with a document open to append file content; with no document open, import creates a document. Markdown headings (`#`, `##`, `###`) are converted to headings. Other Markdown syntax is kept as text. Word documents are not supported. Images can be embedded directly in a document (up to 10 MB each).

## Verify

Run the automated API workflow test:

```bash
python3 -m unittest discover -s tests -v
```

## Deployment

The app is a single Python web process with a persistent SQLite file. Deploy to any Python host that supports a persistent disk; configure `PORT` (provided by most platforms) and mount persistent storage for `documents.db` using `DOCS_DB`. This repository does not include hosting credentials or a deployment URL. Do not deploy the seeded identity-switching demo as a public production service without adding real authentication, CSRF protection, and per-user isolation.

## Scope

Included: responsive document list, rich-text editing (bold, italic, underline, headings, lists), autosave, SQLite persistence, owner/shared labels, seeded account switching, owner-only share grants with access removal, document deletion, and text/Markdown import.

Not included: real sign-in, collaborative simultaneous editing, real-time cursor presence or conflict-free simultaneous editing, revision history, Word import, or production-grade HTML sanitization. The demo uses a browser editor and stores its HTML. Treat it as a portfolio prototype, not a secure multi-tenant deployment.
