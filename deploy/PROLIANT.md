# ProLiant deployment — resume when SSH is reachable

User authorization: upload the recruitment presentation when ProLiant returns,
enable WAN access, and add it to the existing portal index. Use this project as
the canonical source. Do not publish its content or source changes elsewhere.

## Package

Run `./.venv/bin/python tools/stage_proliant.py` from the project root.
Archive and SHA-256 manifest are in `artifacts/proliant-deploy/`.
The archive excludes credentials, the local venv, Git metadata and runtime state.
The Dockerfile installs the existing pinned application dependencies.

## Inspect before changing the server

Use `ssh -F /home/aridlin/.ssh/config -o BatchMode=yes -o ConnectTimeout=5 proliant-lan`;
try `proliant` as the WAN alternative. If neither answers, stay quiet and retry later.
On first successful connection inspect applicable AGENTS.md, OS/architecture,
Docker availability, available RAM/disk, port 18766, existing app services,
`/etc/caddy/whench2.Caddyfile`, and `/opt/servarr-index/index.html`.
Do not print portal credential hashes or copy local Codex credentials.

## Install and validate

1. Copy the archive to the host and verify its SHA-256 before unpacking into
   `/opt/live-explain-recruitment`. Back up any existing installation first.
2. Build `live-explain-recruitment:local` with
   `docker build -f deploy/Dockerfile -t live-explain-recruitment:local .`.
   If necessary, install only missing runtime packages; do not alter other containers.
3. Create `/var/lib/live-explain-recruitment`, owned by UID/GID 10001 with mode 0700.
   Install `deploy/live-explain-recruitment.service`, run daemon-reload and enable/start it.
   Verify `http://127.0.0.1:18766/health`, an actual JPEG frame and private state.
4. Add the authenticated `/live-explain/*` route to the live Caddy site.
   `deploy/portal.py:caddy_patch` prepares a bounded addition and refuses to proceed
   without the existing `media_auth` snippet. Check the actual auth mechanism still
   matches the portal; never expose the presenter API without portal authentication.
5. Add a **Live Explain** entry to the existing index in its current layout, linking
   to `/live-explain/`, with a separate presenter link to `/live-explain/presenter/`.
   Inspect actual HTML/JS navigation first. `index_patch` supports simple links only;
   if it refuses, make a minimal matching edit after inspecting the live structure.
   Do not replace the index or drop existing workspace links.
6. For Caddy/index: make timestamped backups, hash-check originals immediately before
   writing, validate with `/usr/local/bin/whench2-caddy validate`, then reload using
   its existing service. Roll back the edits if validation/reload fails.
7. Verify through the public HTTPS hostname: unauthenticated audience, frame, script
   and commands must be blocked by existing portal auth. In an authenticated browser
   verify index entry, rendered audience, separate phone presenter, advance/pause,
   dygresja/return, canonical switching and reconnect. Save browser evidence locally.

## Architecture and usage

One authoritative session runs on ProLiant using Qt's offscreen renderer. A laptop
browser displays the audience and a phone browser reads/controls the same session,
even from different networks. HTTPS and the existing portal auth protect both views.
The container has no public listener: host binding is `127.0.0.1:18766`.
Share only the audience browser window in Meet; the private presenter contains notes.

The existing Android APK still accepts only HTTP/IPv4 LAN addresses. This deployment
provides the **browser presenter over WAN**; do not claim that old APK supports WAN.
The desktop/LAN application remains available unchanged.

Report completion only after actual upload, service, Caddy, index and authenticated
WAN checks. Then disable the follow-up automation. A staged package is not deployment.

## Follow-up status

2026-10-27: user explicitly approved one unattended deployment after ProLiant
returns, including the service, Caddy and index, and disabling the schedule after
success. This supersedes the earlier read-only restriction from approval review.
The existing heartbeat `sprawd-powr-t-prolianta-dla-live-explain` was updated;
it checks every 15 minutes and must pause itself after verified deployment.
Deployment completed at 2026-10-27 06:55 UTC: archive SHA-256 verified, image
built, systemd enabled/active, Caddy validated/reloaded, two matching index entries
visible in a public browser. Backup: `/var/backups/live-explain-recruitment/20261027T065521Z`.
Public HTTPS returned 401 without authentication for audience, presenter, frame,
state and command endpoints. The deployed service passed script/version,
advance/pause, detour/return and undo checks; the actual Qt JPEG was inspected.

**Resume only verification; do not upload, rebuild, or replace portal files again.**
The remaining authenticated WAN browser test is blocked by missing portal login
in the test browser (`ERR_INVALID_AUTH_CREDENTIALS`). Ask the user to open the
presenter with their existing portal login and confirm the reader/controls.
Do not change passwords or weaken authentication. Physical phone/Meet rehearsal
also remains user-dependent. The heartbeat remains active until this final check;
stay quiet while that condition is unchanged. See the deployment-status JSON.
