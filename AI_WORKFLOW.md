# AI workflow note

## How I used AI

I used OpenAI Codex as a coding partner. I first brainstormed the product experience and wrote down how I envisioned this application. I then gave my notes and the assignment requirments to Codex to produce a working starting point. Building that first version would have taken me much longer if I had written all the code from scratch.

Afterward, I went requirement by requirement, compared the app with the assignment, and used Codex to implement and revise specific parts. I reviewed the changes, tried the flows in the app, and adjusted the product based on what felt useful and coherent. I treated the generated app as a draft to evaluate, not as a finished answer to accept without review.

## Changes guided by my review

I simplified the sidebar by replacing the Recent and Documents navigation with pinned documents and a direct document list. I removed the folder-style menu because the app has no folders. I added text-size controls, image insertion and resizing, document deletion, unsharing, account persistence, list sorting and filtering, and print-to-PDF export. I also changed sharing so invited demo users can edit content and see saved updates in other open views.

I tried `.docx` import and then removed it because it would require a lot more work to make it ready for deployment. The app keeps `.txt` and `.md` import instead. I also experimented with moving Share next to Export and Delete, but reverted that change when it hurt the layout. These choices came from reviewing the actual interface and deciding which features made the product clearer.

## What I intentionally deprioritized

- `.doc` and `.docx` import, after realizing it would need a lot more work
- Folders, because the current app is a lightweight document list and pinning covers the main quick-access need.
- A separate Share button placement beside Export and Delete, because it made the title row spacing worse.
- Live cursors, revision history, presence indicators, and conflict-free simultaneous typing.

## Key implementation decisions

- The Import action focuses on `.txt` and `.md`, which can be handled without extra services or dependencies.
- A visible Shared label helps distinguish owned documents from documents shared with the current demo account.
- Shared users can edit document content; document owners retain management actions such as renaming and deleting.
- The editor polls for newer saved content and refreshes an open document when it is not focused. This supports sequential collaboration, but overlapping edits can still conflict.
- Seeded accounts keep sharing reviewable without building a full authentication system, but they are not secure user accounts.

## Verification and remaining work

I used the API workflow tests for document creation, ownership, sharing, shared edits, deletion, and access removal, and checked the JavaScript syntax. I also manually reviewed the user flows and refined the sidebar, editor controls, and document actions in response to what I saw.

Local documents persist in SQLite across local server restarts. The free Render deployment uses an ephemeral filesystem, so its SQLite database can be cleared when the service sleeps or restarts. I would next connect a durable hosted database and verify persistence across a deployed restart. With a few more hours, I would also add live cursors, revision history, and safer conflict handling for simultaneous edits. Folders could be explored later if users need more organization than pins and sorting provide.
