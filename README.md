# Dynapps — Odoo Agent Farm

The kit behind the `dynapps-agent-farm` marketplace on the Dynapps systemprompt
instance. It carries governed Claude Code skills for Odoo delivery and the farm
agents that run those skills unattended against fixtures and evaluate the result.

## Two trees, two delivery paths

| Tree | Delivered by | Contents |
|------|--------------|----------|
| `plugins/` | Signed services bundle (OCI, `ghcr.io/systempromptio/systemprompt-agent-farm`), imported by the instance | Plugin `dynapps-odoo-delivery`: four skills and its hooks |
| `farm/` | Fetched by the instance from git (`ref: main`), never bundled | Farm definition, agent prompts, evals and fixtures (see `farm/FARM.md`) |

`.systempromptignore` keeps `farm/` and `tools/` out of the bundle.

### Skills

- `odoo_module_review` writes `REVIEW.md` with ORM, access and manifest findings.
- `odoo_migration_plan` writes `MIGRATION_PLAN.md` for a 16.0 to 17.0 upgrade.
- `odoo_release_notes` turns conventional commits into customer `RELEASE_NOTES.md`.
- `odoo_test_plan` writes `TEST_PLAN.md` and TransactionCase tests.

### Hooks

`plugins/dynapps-odoo-delivery/hooks/hooks.json` is inert unless
`SYSTEMPROMPT_FARM_RUN_ID` is set, so an ordinary session installing the plugin
is unaffected (governance for those comes from `dynapps-commons`). In a farm run
it requires `SYSTEMPROMPT_URL` and `SYSTEMPROMPT_TOKEN`, sends every tool call to
`/api/public/hooks/govern`, and tracks tool results and stops with the run id.
`tools/hooks-smoke.sh` exercises every command without network.

## Run the checks locally

```sh
python3 -m pip install --user pyyaml
python3 tools/farm-lint.py --strict
python3 -I tools/sanitize-kit.py --strict
sh tools/hooks-smoke.sh
systemprompt core marketplace import --from . --into ./out/services --strict
```

## Release

`metadata.version` in `.claude-plugin/marketplace.json` is the release. Merge to
`main` with a version no tag carries and `.github/workflows/publish-bundle.yml`
validates, signs, publishes `:vX.Y.Z` and `:stable`, and tags the release. That
workflow needs a published GitHub Release of `systempromptio/systemprompt-dynapps`;
until one exists, publish from the Dynapps repository with
`demo/agent-farm/10-publish-kit.sh`. Who may use the marketplace is declared on the
instance, never here. See `README-INTEGRATION.md`.
