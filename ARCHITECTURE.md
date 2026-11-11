# Architecture and product decisions

## Shape

`server.py` serves both the static browser app and a JSON API using Python's standard library. SQLite stores users, document title/content/owner/update time, and the document-to-user share relation. The browser editor is a `contenteditable` surface with a small formatting toolbar and a debounced save request. Each API request carries the selected demo identity in `X-User-Id`; the server checks ownership or a share row before returning content, and shared users can update content while only owners can rename or grant access. The browser refreshes an open document with newer saved content when the editor is not focused; this is lightweight sync rather than conflict-free simultaneous editing.

## Priorities

The core slice is the document lifecycle plus a demonstrable sharing journey. The seeded identity switch avoids spending the timebox on auth infrastructure while making owner/shared states testable. Read-only recipient access establishes a clear permission boundary and avoids ambiguous concurrent-write behavior. Text/Markdown import was chosen because it is useful immediately, easy to explain, and requires no external conversion service. SQLite keeps setup and local evaluation friction low.

## Tradeoffs and next steps

This prototype does not provide production authentication, CSRF defense, robust HTML sanitization, conflict resolution, revision history, or real-time collaboration. The demo account selector is not an access-control identity mechanism for a public deployment. With another 2–4 hours, add real authentication and sessions, server-side HTML allow-list sanitization, owner controls to revoke shares, safe shared editing with optimistic version checks, and deploy to a persistent-disk Python host. A hosted deployment requires credentials and a target account not available in this workspace.
