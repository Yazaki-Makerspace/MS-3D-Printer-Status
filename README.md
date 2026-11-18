# 3D Lab Printer Status

Live status of the Yazaki Makerspace 3D Lab printers, made for the TV screens.

**Page:** https://yazaki-makerspace.github.io/MS-3D-Printer-Status/

## How it updates

1. The printers report to Bambu Cloud.
2. A small collector on the Makerspace Surface kiosk reads that status (read only) every few seconds.
3. Every 3 minutes while something changes (every 10 minutes when nothing does), it sends the status here as a `repository_dispatch` event called `update-status`.
4. `.github/workflows/publish.yml` writes it to `status.json`, keeping only screen-safe fields (`tools/clean_status.py`), and republishes this site.
5. The page reloads `status.json` every 30 seconds. With no update for 18 minutes it greys out. After 6 hours it says printer status is offline.

## What is public

Printer name, model, class level, state, percent, minutes left, layers, a stage word, filament colors and types, and when the state began. Never file or job names, who printed, serial numbers, access codes or camera images.

## Page options

`?poll=30` seconds between reloads · `?done=60` minutes a finished print shows as DONE · `?src=<url>` read another status.json (it also reads the older PrintStatus format).

## Upkeep

- The collector's GitHub token expires. GitHub emails this account before it does. Make a new fine-grained token for this repo only (Contents: Read and write, Workflows: Read and write) and save it on the Surface with `python3 ~/makerspace-printers/login.py --github-token`.
- The collector's code and notes live with the Makerspace staff files (`1 Active/3D Lab Printer Status/`).
- If the page stops changing or deploys fail while the collector still sends (2026-11-17): push any small commit to `main`. Each Pages deployment is named after the commit, and a new commit gives it a new name.
- Since 2026-11-18 the publish workflow does this by itself: after each deploy it checks the live `status.json`, and if the page did not change it commits a new time to `.pages-nudge` (at most once per 30 minutes).
