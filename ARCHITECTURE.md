# Architecture and product decisions

## Application shape

Docspace is a small, single-process web app. `server.py` uses Python’s standard-library HTTP server to serve the browser assets and a JSON API. SQLite stores seeded demo users, document titles and HTML content, owner IDs, creation and update timestamps, and document share relationships.

The browser editor uses `contenteditable` for basic rich-text editing. It sends debounced saves to the API. The sidebar keeps pin choices, the selected demo account, and the sort/filter choice in browser `localStorage`; document data and sharing relationships live in SQLite.

## Sharing and collaboration

The app represents a user on each request with an `X-User-Id` header selected from the demo account menu. Owners can rename and delete documents, grant access, or remove a collaborator’s access. Shared users can edit document content and remove the shared document from their own list.

Open documents poll for newer saved content and refresh when the editor is not focused. This supports basic collaboration for sequential edits, but it is not real-time collaborative editing: there are no cursors, presence indicators, revision history, or conflict-free simultaneous editing. If two people save overlapping changes, the later save can replace the earlier content.

## Product choices

The assignment is broad, so the implementation focuses on the document lifecycle and a demonstrable share flow. Seeded accounts avoid spending the timebox on authentication infrastructure. Plain-text and Markdown import provide a useful, dependency-free workflow; Word formats are outside scope. Images can be embedded in document content. The app also supports pinning, list sort/filter options, and browser print-to-PDF export.

SQLite and the Python standard library keep local setup free of external dependencies. The included Render demo uses a free web service, whose local filesystem is ephemeral; its SQLite data can disappear after a sleep or restart. The live URL is listed in the README.

## Limitations and next steps

The demo identity selector is not authentication or a secure access-control boundary. The app is not suitable for private or production use without real sessions, CSRF protection, server-side HTML sanitization, and stronger tenant isolation. The next collaboration improvements would be optimistic version checks or an operation-based editor, conflict feedback, and live presence. Durable hosted storage would require moving SQLite to a persistent disk or managed database.
