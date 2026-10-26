# Agent workflow

The repository contains a portable skill at `skills/itol-workflow/SKILL.md`. It is an instruction package for an existing assistant, not a separate autonomous runtime or LLM service. CLI knowledge is bundled in wheels and works offline.

1. Run `itol backends` and inspect inputs. For tree parsing install `.[trees]`; for the advanced PyiTOL backend use Python 3.10+ and `.[all]`.
2. Read only the relevant knowledge topics. Use `tree inspect` before matching annotation IDs; do not rename leaves to make a mismatch disappear.
3. Select encodings based on actual measurements. Generate native annotations with `--tree` to validate IDs; use the optional backend for additional template families.
4. Write reusable dataset/export configuration. Record input file hashes and package versions in the user's working report if provenance matters.
5. Package inputs and inspect upload `--dry-run`. Send data to iTOL only when that workflow is authorized and account prerequisites exist; no automatic credential search is needed.
6. Export the selected tree ID, then inspect the actual figure before describing visual quality. Report offline, simulated HTTP and successful real service validation separately.

For PyiTOL, inspect `itol pyitol --help` and subcommand help in the installed version. `itol pyitol ...` forwards arguments without a shell and preserves upstream output/exit status; it does not transform PyiTOL into the native JSON protocol. The optional integration is not a claim that every upstream feature has been acceptance-tested.

The original tree should remain available. Converting formats, rerooting or changing topology are scientific operations with different implications; a request to beautify a tree does not by itself justify altering its topology or support values.
