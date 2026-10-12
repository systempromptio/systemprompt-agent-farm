# Conventional commit to release-note mapping

| Commit type | Section | Notes |
|-------------|---------|-------|
| `feat` | New | Rewrite for the functional user. |
| `fix` | Fixed | Describe the symptom the user saw, not the cause. |
| `perf` | Fixed | "loads faster", "no longer times out". |
| `feat!`, `fix!`, footer `BREAKING CHANGE:` | Action required + its section | State the action. |
| `security` scope or changes to `ir.model.access.csv` | Action required | Name the group whose rights changed. |
| `chore(deps)` adding a module to `depends` | Action required | The dependency must be installed. |
| `migration`, files under `migrations/` | Action required | "Back up the database before upgrading." |
| `chore`, `ci`, `test`, `refactor`, `style`, `build` | omitted | Count only. |
| `docs` | omitted unless user documentation | |

Scope maps to the user-facing area: `fleet` -> "Fleet", `maintenance` -> "Maintenance requests",
`report` -> the report's printed name. Unknown scopes use the module display name.

A commit without a conventional prefix is classified by reading its diff summary; if still
unclear, list it under Fixed and flag it in a final "Unclassified" note for the developer.
