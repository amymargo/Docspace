# Docspace

A lightweight shared document editor focused on the essentials: creating and editing documents, saving them, importing text, attaching images, and sharing work with teammates.

## Watch the walkthrough video on Youtube

**Walkthrough Video:** https://youtu.be/jr-p_ADXP0E

## Try the live demo

**Live app:** https://docspace-djcw.onrender.com/

Choose Amy, Alex, or Sam from the account selector in the top bar. To try sharing, create a document as Amy, share it with Alex or Sam, then switch accounts. Shared users can edit document content.

The free Render service may sleep when idle, and its local SQLite database can reset after a sleep or restart. The first request after inactivity may take about a minute to load.

## Run locally

Requirements: Python 3.12 or later. No third-party packages are needed.

```bash
python3 server.py
```

Open [http://localhost:8000](http://localhost:8000). 

The app creates `documents.db` next to `server.py` on first run.
To change the port, set `PORT`; to choose a database location, set `DOCS_DB`.

## Editing and files

The editor supports bold, italic, underline, headings, text sizes, lists, autosave, and reopening saved documents. Import `.txt` and `.md` files up to 1 MB. Word `.doc` and `.docx` files are not supported.

PNG, JPEG, GIF, and WebP images up to 10 MB can be inserted into documents and resized using the image-size menu.

**Export** opens the browser print dialog; choose **Save as PDF** there.

The sidebar supports pinning documents and sorting or filtering by last edited, created, alphabetical, shared with me, or owned by me.

## Verify

Run the API workflow tests with:

```bash
python3 -m unittest discover -s tests -v
```

## Architecture and scope

The app uses a Python standard-library HTTP server, a small browser UI, and SQLite. Documents and sharing relationships are stored in SQLite. Shared edits sync to other open views when the editor is not actively focused. This is lightweight polling, not real-time collaborative editing: there are no live cursors, revision history, or conflict-free simultaneous typing.

The seeded account selector is not secure authentication, and the app does not include production-grade HTML sanitization or multi-tenant protections. The free deployment is intended for review and demonstration, not durable storage or production use. See [ARCHITECTURE.md](ARCHITECTURE.md) for implementation choices and next steps.
