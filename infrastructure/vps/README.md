# VPS deployment

The app runs on the Contabo VPS next to the other personal apps. Caddy (owned by the `portfolio` stack) terminates TLS and proxies to the container over the shared `edge-net` Docker network. Nothing is published on a host port.

| File | Lives on the VPS at | Purpose |
| --- | --- | --- |
| `docker-compose.prod.yml` | `/opt/dsai/` | Two identical slots, `dsai-blue` and `dsai-green` |
| `env.example` | `/opt/dsai/.env` (mode 600) | Image repo and tag; `deploy.sh` rewrites `IMAGE_TAG` |
| `deploy.sh` | `/opt/dsai/` | SSH forced command for the CI deploy key: blue/green rollout |
| `dsai.service` | `/etc/systemd/system/` | Brings the live slot up after a reboot |
| `Caddyfile.block` | appended to `/opt/portfolio/Caddyfile` | `app.ml-visualizer.at` site block |
| `previews/dsai.conf`, `previews/dsai.env` | `/opt/previews/apps/` | Registers the app with the shared MR preview runner |

## How a deploy works

1. A `v*` tag builds `registry.gitlab.com/woofiowo/ml-visualizer:<tag>`.
2. The manual `deploy-production` job runs `ssh deploy@VPS <tag>`. The key is bound to `/opt/dsai/deploy.sh`, so it can run nothing else.
3. `deploy.sh` starts the idle slot, requires three consecutive healthy answers from `/_stcore/health`, rewrites the `reverse_proxy dsai-<slot>:8080` line in the Caddyfile, reloads Caddy through `/opt/caddy-reload.sh` and removes the old slot. If the health check or the Caddy reload fails, the live slot keeps all traffic.
4. The job finishes with an end-to-end `curl` against `PRODUCTION_URL`.

Roll back by re-running the job of an older tag.

## Merge request previews

The manual `deploy-review` job calls the shared runner (`/opt/previews/run.sh`) with `create dsai <MR> <sha> <tag>`. The result is `https://pr-<MR>.dsai.preview.woofi-developments.at`, behind the preview basic-auth login the other apps use. The container is replaced on every push and removed with the `stop-review` job or when the MR is merged or closed. The box caps previews at six across all apps.

DNS needs one wildcard record: `*.dsai.preview` A `167.86.115.79` in the `woofi-developments.at` zone.

## CI variables (GitLab, project 76772967)

| Variable | Notes |
| --- | --- |
| `VPS_HOST` | `167.86.115.79` |
| `VPS_KNOWN_HOSTS` | Pinned host key, so CI never trusts the VPS blindly |
| `VPS_DEPLOY_KEY` | File, protected (tags only). Bound to `/opt/dsai/deploy.sh` |
| `VPS_PREVIEW_KEY` | File. Bound to `/opt/previews/run.sh` |
| `PRODUCTION_URL` | `https://app.ml-visualizer.at` |

The VPS pulls with a read-only GitLab deploy token (`vps-pull`, scope `read_registry`), logged in once as the `deploy` user (`docker login registry.gitlab.com`). Rotate it by creating a new token and repeating that login.

## One-time bootstrap (already done)

Copy the files to the paths above, `echo blue > /opt/dsai/active_slot`, add the two `authorized_keys` lines (`command="/opt/dsai/deploy.sh",restrict <key>` and `command="/opt/previews/run.sh",restrict <key>`), add `dsai` to `PREVIEW_APPS` in `/opt/previews/lib.sh`, `systemctl enable dsai`, and run the first deploy through the pipeline.
