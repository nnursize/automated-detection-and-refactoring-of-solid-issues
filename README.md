# S1-T7-Okeyish — CS 537 SDP Project

Automated detection of **SOLID design principle violations** in open-source codebases, driven by LLM scans across multiple prompting strategies.

## Team Information
**Team Code:** S1-T7

| Name | Student ID |
| :--- | :--- |
| Nurşize Turan | 22501408 |
| Melih Coşğun | 22301344 |
| Alperen Tolga Karaçam | 22501397 |

## Task Distribution

| Member | Repo 1 | Repo 2 | Repo 3 |
| :--- | :--- | :--- | :--- |
| **Nurşize Turan** | `psf/requests` (Python) | `google/gson` (Java) | `catchorg/Catch2` (C++) |
| **Melih Coşğun** | `logstash` (Java+Ruby) | `seaborn` (Python) | `jackson-core` (Java) |
| **Alperen Tolga Karaçam** | `alibaba/fastjson2` (Java) | `pallets/flask` (Python) | `Kotlin/kotlinx-datetime` (Kotlin) |

---

## Submission Results Folder

The final submission artifacts are consolidated under [Results/](Results/) so the detection and refactoring outputs can be checked from one place. The folder is organized by team member and assigned repository:

```text
Results/
|-- Nursize/
|   |-- requests/
|   |-- gson/
|   |-- Catch2/
|-- Melih/
| ...
|-- Alperen/
| ...
```


Each completed repository folder follows the same structure:

```text
<repo>/
|-- detection/
|   |-- 60_detection_<repo>.json  # final 60-candidate detection/refactor shortlist
|   `-- raw_scans/                # raw scan outputs copied from scans/<repo>/
|-- manual_labels/                # manual detection/refactor labels copied from evaluations/
`-- refactoring/
    |-- <repo>_pull_requests.json
    |-- <repo>_refactor_summary.md
    |-- raw_attempts/             # full per-issue prompts, raw responses, diffs, metrics, and mock PR files
    `-- refactored_codes/         # per-issue non-empty applied_diff.patch files only
```

For detection review, start with:

- `Results/<member>/<repo>/detection/60_detection_<repo>.json`
- `Results/<member>/<repo>/detection/raw_scans/registry.json`

For refactoring review, start with:

- `Results/<member>/<repo>/refactoring/<repo>_pull_requests.json`
- `Results/<member>/<repo>/refactoring/<repo>_refactor_summary.md`
- `Results/<member>/<repo>/refactoring/refactored_codes/<PRINCIPLE>/<issue_id>/applied_diff.patch`
- `Results/<member>/<repo>/refactoring/raw_attempts/<PRINCIPLE>/<issue_id>/applied_diff.patch`

The `refactored_codes/` folder is the quickest way to inspect only the code changes. It mirrors the `raw_attempts/` principle/issue layout, but includes only issues with a non-empty `applied_diff.patch`.

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd S1-T7-Okeyish
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Three runtime deps: `pydantic` (config + models), `pyyaml` (config files), `google-genai` (Gemini SDK).

### 3. Set the Gemini API key

Create a key at [AI Studio](https://aistudio.google.com/apikey), then:

```bash
set GEMINI_API_KEY=...            # Windows cmd
$env:GEMINI_API_KEY = "..."       # PowerShell
export GEMINI_API_KEY=...         # macOS / Linux
```

### 4. Download the target repositories

Each repo listed in `configs/` is expected to sit **next to** `S1-T7-Okeyish/`. For example:

```
Desktop/SDP-Okeyish/
├── S1-T7-Okeyish/       # this project
├── seaborn-master/      # target repo (from configs/seaborn.yaml)
├── jackson-core-3.x/    # target repo (from configs/jackson-core.yaml)
└── logstash-main/       # target repo (from configs/logstash.yaml)
```

The `path:` field in each YAML is relative to `S1-T7-Okeyish/`, so `../logstash-main` resolves correctly. Target repos are gitignored.

### Supported languages

Per-file extraction is driven by file extension (so mixed-language repos work):

| Language   | Parser                |
|------------|-----------------------|
| Python     | `ast` (full fidelity) |
| Java       | regex                 |
| C++        | regex                 |
| TypeScript | regex                 |
| Ruby       | regex + `end`-balance |

`repo.language` in the config is only the prompt label (e.g. `"Analyze the following java source code…"`). For mixed repos (e.g. Logstash = Java+Ruby) set it to the dominant language and include all extensions in `file_extensions`.

---

## Configuration files

Each target repo has a YAML in `configs/`. Minimal structure:

```yaml
repo:
  name: "seaborn-master"                 # folder name inside scans/ and reports/
  path: "../seaborn-master"              # relative to this project
  language: "python"                     # prompt label
  source_root: "seaborn"                 # subdirectory to walk
  file_extensions: [".py"]               # files that get extracted
  exclude_patterns:                      # fnmatch against relative path and basename
    - "*/test/*"
    - "*/tests/*"
  max_file_lines: 2000
  min_file_lines: 10

llm:
  primary_provider: "gemini"
  secondary_provider: "gemini"
  temperature_range: [0.2, 0.8]
  max_output_tokens: 16384

scan:
  scans_per_principle: 12
  principles: ["SRP", "OCP", "LSP", "ISP", "DIP"]
  output_dir: "scans"
  reports_dir: "reports"
```

Available configs out of the box: [configs/requests.yaml](configs/requests.yaml) (Python), [configs/gson.yaml](configs/gson.yaml) (Java), [configs/catch2.yaml](configs/catch2.yaml) (C++), [configs/seaborn.yaml](configs/seaborn.yaml) (Python), [configs/jackson-core.yaml](configs/jackson-core.yaml) (Java), and [configs/logstash.yaml](configs/logstash.yaml) (Java+Ruby).

---

## The 12-scan schedule

Each SOLID principle runs **12 scans** covering 4 prompting/context strategies at 3 temperatures:

| Scan | Strategy                                             | Temp |
|-----:|------------------------------------------------------|-----:|
| 1–3  | `full_repo` (baseline whole-repo context)            | 0.2 / 0.5 / 0.8 |
| 4–6  | `smell_two_step` (CoT: smells → SOLID)               | 0.2 / 0.5 / 0.8 |
| 7–9  | `class_centric` (target class + bases + imports)     | 0.2 / 0.5 / 0.8 |
| 10–12| `skeleton` (signatures-only repo view)               | 0.2 / 0.5 / 0.8 |

5 principles × 12 scans = **60 scans total** per repo. Findings are deduplicated across scans by (file, entity, line-range); each unique issue tracks how many scans detected it (`scan_count`), which drives confidence ranking.

---

## Running scans

All commands assume you're at the project root with the venv activated.

### Preview without calling the API

```bash
python run_detection.py --config configs/seaborn.yaml --dry-run
```

Prints discovered files, top classes per file with method counts, class-centric targets, and the 60-scan schedule. No API calls, no quota consumed. Use this to validate a new config or verify language support.

### Run all 60 scans

```bash
python run_detection.py --config configs/seaborn.yaml
```

Pauses 60 seconds between API calls by default (Gemini free tier is 5 RPM per model). Already-completed scans on disk are skipped, so re-running after an interruption just resumes. Reports are regenerated at the end.

### Target a subset

```bash
python run_detection.py --config configs/seaborn.yaml --principle SRP           # 12 scans for SRP
python run_detection.py --config configs/seaborn.yaml --principle SRP --scan 1  # one scan
```

### Regenerate reports without scanning

After you've filled gaps (e.g. reran a previously failed scan), refresh all reports from what's on disk:

```bash
python run_detection.py --config configs/seaborn.yaml --report-only
```

### See what's done / failed / missing

```bash
python run_detection.py --config configs/seaborn.yaml --status
```

Prints a table of every scan with its model, findings count, duration, and any error. The same info is written into `reports/<repo>_registry.json` under the `"scans"` key, so you don't have to open each scan folder to diagnose failures.

---

## Managing models and quota

### Discover which model IDs work with your key

```bash
python run_detection.py --list-models
```

Filters the full API listing down to text-generation models and groups them by family (Gemini 2.5, 2.0, 3-preview, Gemma, other). Use this before `--model` to avoid 404s from stale IDs.

### Override the model

```bash
python run_detection.py --config configs/seaborn.yaml --model gemini-2.5-flash-lite
```

Default is `gemini-2.5-flash`. Free-tier quota is **per-model**, so switching to `gemini-2.5-flash-lite` or `gemini-2.0-flash` gives you a fresh bucket if you exhaust the primary. The model used is recorded per-scan so you can tell later which scans ran on which bucket.

### Pace between calls

```bash
python run_detection.py --config configs/seaborn.yaml --sleep 90       # wait 90s between API calls
python run_detection.py --config configs/seaborn.yaml --sleep 0        # no wait (risky on free tier)
```

Skipped scans (already on disk) don't trigger the wait.

### Stop / continue on error

By default the framework **halts on the first failure** (429 quota, 503 overload, 404 bad model) — this protects remaining quota while the model is busy. To plow through:

```bash
python run_detection.py --config configs/seaborn.yaml --continue-on-error
```

404 errors fail fast (no retry) because a wrong model ID won't fix itself.

### Delete a bad scan and rebuild

If a scan produced garbage and you want to redo it with a different model:

```bash
# 1. Delete the scan folder from disk (e.g. scans/seaborn-master/SRP/scan_04/)
# 2. Rebuild the registry so its findings drop out
python run_detection.py --config configs/seaborn.yaml --rebuild-registry

# 3. Re-run that one scan with a different model
python run_detection.py --config configs/seaborn.yaml --principle SRP --scan 4 --model gemini-2.0-flash
```

---

## Output structure

```
scans/<repo>/
├── <PRINCIPLE>/
│   └── scan_<N>/
│       ├── raw_response.json     # prompt, model, temperature, findings, error (if any)
│       └── parsed_findings.json  # structured Finding objects
└── registry.json                 # running registry (updated each scan)

reports/
├── <repo>_SRP_report.md
├── <repo>_OCP_report.md
├── <repo>_LSP_report.md
├── <repo>_ISP_report.md
├── <repo>_DIP_report.md
├── <repo>_summary.md                  # all principles, ranked by scan_count
├── <repo>_registry.json               # final snapshot: issues + per-scan status
├── <repo>_refactor_shortlist.json     # top 12 × 5 principles = 60 refactor candidates
├── <repo>_refactor_shortlist.md       # same, human-readable
└── <repo>_scan_summary.csv            # one row per scan (for plotting / Excel)
```

The **refactor shortlist** is the deliverable for Phase 2. Ranking per principle: `scan_count` descending (confidence), then severity (high > medium > low), then file + line for determinism.

---

## Quick reference — all CLI flags

| Flag | Purpose |
|------|---------|
| `--config <path>` | Required. Path to YAML config. |
| `--principle {SRP,OCP,LSP,ISP,DIP}` | Run only this principle's 12 scans. |
| `--scan <1–12>` | Run only this scan number (pair with `--principle`). |
| `--dry-run` | Preview discovery / schedule, no API calls. |
| `--report-only` | Rebuild reports from scans on disk. |
| `--model <id>` | Override Gemini model for this run. |
| `--list-models` | Print filtered list of available models and exit. |
| `--sleep <sec>` | Seconds between API calls (default 60). |
| `--rebuild-registry` | Wipe and rebuild the registry from scans on disk. |
| `--continue-on-error` | Don't halt on 429 / 503 / 404. |
| `--status` | Print scan status table and exit. |

---

# Phase 2 - Automated refactoring

Phase 2 consumes `reports/<repo>_refactor_shortlist.json` and tries to refactor each shortlisted SOLID violation with Gemini. The refactoring code lives in [refactoring/](refactoring/), and the CLI entry point is [run_refactoring.py](run_refactoring.py).

Each attempt runs against a separate mutable workspace clone under `refactor_workspaces/<repo>/`. Successful attempts are committed into that clone, so later attempts build on the already-refactored source. Every attempt, successful or not, writes review artifacts under `refactor_attempts/<repo>/<PRINCIPLE>/<issue_id>/` and master summaries under `refactor_reports/`.

The framework is adapter-based:

| Target | Adapter | Verification mode |
|--------|---------|-------------------|
| Python / seaborn, requests | `python` | Applies patches, checks Python syntax, runs pytest, and commits only if tests have no new failures. |
| Java / jackson-core, gson | `java-maven` | Applies patches and commits them as `applied_unverified`; automated Maven tests are intentionally skipped. |
| Java/Ruby / logstash | `java-gradle` | Applies patches and commits them as `applied_unverified`; automated Gradle tests are intentionally skipped. |
| C++ / Catch2 | `c-cpp` | Applies patches, runs lightweight syntax checks where practical, and commits them as `applied_unverified`; full CMake/test execution is intentionally skipped. |

Adapters are not only test runners. They also provide the refactoring pipeline with language/build-system selection, source-file extension rules, sibling-source discovery for prompt context, syntax-check hooks after patch application, and the `supports_testing` flag that decides whether an applied patch becomes `applied_passed` or `applied_unverified`. For Java and C/C++ adapters, full test execution is disabled, but the adapter is still part of the non-test refactoring flow.

## Refactoring inputs

The main input is the detection shortlist:

```text
reports/<repo>_refactor_shortlist.json
```

This file is generated by the detection phase and contains the top refactor candidates per SOLID principle.

Optional manual detection labels can be placed here:

```text
evaluations/<repo>_labels.json
```

The label file is discovered automatically from the repo name in the YAML config. For example, `configs/seaborn.yaml` has `repo.name: seaborn-master`, so the refactoring run checks `evaluations/seaborn-master_labels.json`.

Label behavior:

| Label state | Behavior |
|-------------|----------|
| No labels file | All shortlisted issues are treated as refactorable. |
| Issue missing from labels file | That issue is treated as refactorable. |
| `{ "issue_id": "SRP-001", "label": true }` | The issue is refactored normally. |
| `{ "issue_id": "SRP-001", "label": false }` | The issue is skipped and recorded as `detection_rejected`. |

Use this when you manually evaluate detection results before refactoring. False detections are still represented in the refactoring artifacts, but they do not call Gemini and do not modify the workspace.

## How one attempt works

For each shortlisted issue, the orchestrator:

1. Loads the current issue from the shortlist.
2. Checks `evaluations/<repo>_labels.json`; explicit `false` labels become `detection_rejected`.
3. Prepares or reuses `refactor_workspaces/<repo>/`.
4. Re-locates the target entity in the current workspace source, because previous successful refactors may have shifted line numbers.
5. Builds a prompt containing the violation, the SOLID principle definition, the current source file, sibling source files, and strict SEARCH/REPLACE/CREATE output rules.
6. Calls Gemini using the `refactor:` temperature and max token settings from the YAML config.
7. Saves `prompt.txt`, `raw_response.json`, and parsed `patch_blocks.json`.
8. Rejects the attempt immediately if Gemini finished with `MAX_TOKENS`, because truncated responses can contain incomplete patches.
9. Applies parsed patch blocks programmatically.
10. Writes `applied_diff.patch`, including both modified tracked files and newly-created files.
11. For Python projects, runs pytest and compares failures against the baseline failure set.
12. Commits successful attempts to the workspace git history.
13. Writes `pull_request.json` and `pull_request.md` for manual review.
14. Updates the master reports in `refactor_reports/` at the end of the run, or after a fatal LLM halt.

## Refactor config

Each repo uses the same YAML as detection, with an extra `refactor:` block.

Python example from [configs/seaborn.yaml](configs/seaborn.yaml):

```yaml
refactor:
  python_executable: "C:/Users/User/miniconda3/python.exe"
  install_extras: ".[dev,stats]"
  test_timeout_sec: 1800.0
  full_suite_timeout_sec: 3600.0
  temperature: 0.2
  max_output_tokens: 65536
```

Java/Maven example from [configs/jackson-core.yaml](configs/jackson-core.yaml):

```yaml
refactor:
  build_system: "maven"
  test_timeout_sec: 1800.0
  full_suite_timeout_sec: 3600.0
  temperature: 0.2
  max_output_tokens: 65536
```

Gradle example from [configs/logstash.yaml](configs/logstash.yaml):

```yaml
refactor:
  build_system: "gradle"
  gradle_test_task: ":logstash-core:test"
  gradle_compile_task: ":logstash-core:compileTestJava"
  test_timeout_sec: 2400.0
  full_suite_timeout_sec: 5400.0
  temperature: 0.2
  max_output_tokens: 65536
```

C++ example from [configs/catch2.yaml](configs/catch2.yaml):

```yaml
refactor:
  test_timeout_sec: 1800.0
  full_suite_timeout_sec: 3600.0
  temperature: 0.2
  max_output_tokens: 65536
```

Important settings:

| Setting | Meaning |
|---------|---------|
| `temperature` | Gemini temperature for refactoring calls. Lower values are safer. |
| `max_output_tokens` | Output budget for Gemini. The stock configs use `65536` to reduce truncation on large refactors. |
| `python_executable` | Python interpreter used to create the target repo virtualenv. |
| `install_extras` | Editable install argument for Python target repos. |
| `build_system` | Java build adapter selection: `maven` or `gradle`; omitted for Python and C/C++ configs. |
| `gradle_test_task` / `gradle_compile_task` | Gradle task names for Logstash-style multi-module repos. |
| `test_timeout_sec` | Per-attempt test timeout when tests are enabled. |
| `full_suite_timeout_sec` | Final full-suite timeout for tested adapters. |

## Running refactoring

All commands assume you are in the project root with dependencies installed and `GEMINI_API_KEY` set.

Preview the issues that would be attempted:

```bash
python run_refactoring.py --config configs/seaborn.yaml --dry-run
```

Run one issue:

```bash
python run_refactoring.py --config configs/seaborn.yaml --issue SRP-019 --no-final-suite
```

Run one principle:

```bash
python run_refactoring.py --config configs/seaborn.yaml --principle SRP
```

Run the full shortlist for one repo:

```bash
python run_refactoring.py --config configs/seaborn.yaml
python run_refactoring.py --config configs/jackson-core.yaml
python run_refactoring.py --config configs/logstash.yaml
```

Check current attempt statuses:

```bash
python run_refactoring.py --config configs/seaborn.yaml --status
```

Regenerate master reports from existing attempt artifacts:

```bash
python run_refactoring.py --config configs/seaborn.yaml --report-only
```

Re-render per-attempt PR files and diffs after renderer/parser changes:

```bash
python run_refactoring.py --config configs/seaborn.yaml --rerender-prs
```

Retry failed attempts:

```bash
python run_refactoring.py --config configs/seaborn.yaml --retry-status patch_failed,applied_failed,llm_error
```

Retry a single failed issue:

```bash
python run_refactoring.py --config configs/seaborn.yaml --issue SRP-019 --retry-status patch_failed
```

The default retry set is:

```text
patch_failed,applied_failed,llm_error
```

Successful statuses are skipped on normal resume unless you explicitly include them in `--retry-status`.

## CLI flags for refactoring

| Flag | Purpose |
|------|---------|
| `--config <path>` | Required. Path to the repo YAML config. |
| `--principle {SRP,OCP,LSP,ISP,DIP}` | Limit the run to one SOLID principle. |
| `--issue <id>` | Run only one issue, for example `SRP-001`. |
| `--dry-run` | Print the issues that would be attempted. No LLM call, no patching, no tests. |
| `--status` | Print the status table for the current shortlist and exit. |
| `--model <id>` | Override the Gemini model for this run. |
| `--sleep <sec>` | Seconds between LLM calls. Default is `60`. |
| `--retry-status <list>` | Comma-separated statuses to retry. Default is `patch_failed,applied_failed,llm_error`. |
| `--no-final-suite` | Skip the final full pytest gate. Useful for single-issue smoke tests. |
| `--full-suite-only` | Prepare the workspace and run only the final full suite against the current clone state. |
| `--report-only` | Rebuild master reports from existing per-attempt `pull_request.json` files. |
| `--rerender-prs` | Rebuild every per-attempt `pull_request.json`, `pull_request.md`, and committed diffs where possible. Does not call Gemini. |

## Output locations

Workspace clone:

```text
refactor_workspaces/<repo>/
```

This is a local git clone used by the refactoring pipeline. It is intentionally mutable. Successful refactors are committed here one by one.

Per-attempt artifacts:

```text
refactor_attempts/<repo>/<PRINCIPLE>/<issue_id>/
  prompt.txt
  raw_response.json
  patch_blocks.json
  applied_diff.patch
  test_results.json
  metrics_before.json
  metrics_after.json
  pull_request.json
  pull_request.md
```

Artifact meanings:

| File | Meaning |
|------|---------|
| `prompt.txt` | Full prompt sent to Gemini. |
| `raw_response.json` | Raw Gemini response, model name, latency, token counts, and finish reason. |
| `patch_blocks.json` | Parsed SEARCH/REPLACE/CREATE blocks. Empty when no usable patch was produced. |
| `applied_diff.patch` | Unified diff of applied changes. Includes modified files and newly-created files. Empty when no patch was applied. |
| `test_results.json` | Python pytest result for tested attempts. Not produced for Java patch-only attempts or pre-apply failures. |
| `metrics_before.json` | Code metrics before the attempted change. |
| `metrics_after.json` | Code metrics after successful applied attempts. |
| `pull_request.json` | Structured mock PR for evaluation and downstream analysis. |
| `pull_request.md` | Human-readable mock PR for manual review. |

Master reports:

```text
refactor_reports/
  <repo>_pull_requests.json
  <repo>_refactor_summary.md
  <repo>_refactor_summary.csv
  <repo>_refactor_registry.json
  <repo>_full_suite_final.json
```

Report meanings:

| File | Meaning |
|------|---------|
| `<repo>_pull_requests.json` | All per-attempt PR JSON payloads collected into one file. Good for evaluation scripts. |
| `<repo>_refactor_summary.md` | Human-readable status summary. |
| `<repo>_refactor_summary.csv` | Spreadsheet-friendly summary with status, tests, and metric deltas. |
| `<repo>_refactor_registry.json` | Structured registry of all attempts. |
| `<repo>_full_suite_final.json` | Final full pytest result for tested adapters, when run. |

## Attempt status values

Every issue that the refactoring run reaches gets a `pull_request.json` with one of these statuses:

| Status | Meaning | Tests run? | Commit? |
|--------|---------|------------|---------|
| `applied_passed` | Python patch applied and pytest found no new failures compared with baseline. | Yes | Yes |
| `applied_unverified` | Patch applied and committed in a patch-only adapter such as Java/Maven or Java/Gradle. | No | Yes |
| `applied_failed` | Patch applied, but tests showed new failures. The workspace is reverted. | Yes | No |
| `patch_failed` | No usable patch was applied. Examples: no patch blocks, SEARCH text not found, duplicate/ambiguous match, syntax error, no net diff/no-op replacement, or `MAX_TOKENS` truncation. | No | No |
| `detection_rejected` | The detection was manually labeled false in `evaluations/<repo>_labels.json`. | No | No |
| `obsolete` | The entity could not be found in the current workspace, usually because an earlier refactor changed the source. | No | No |
| `llm_error` | The Gemini call failed or an unexpected orchestration error occurred. | No | No |

For later refactoring-quality evaluation, focus mainly on:

```text
applied_passed
applied_unverified
```

Those are the statuses where refactored code exists in the workspace and a useful `applied_diff.patch` should be present.

## Applied diffs

`applied_diff.patch` is generated by the framework from git state, not written manually by the LLM.

For committed successful attempts, `--rerender-prs` recomputes the diff from git history:

```text
git diff <head_commit>~1 <head_commit>
```

For fresh uncommitted attempts, the workspace diff includes:

- normal `git diff` output for modified tracked files
- synthetic unified diffs for newly-created untracked text files

This matters because plain `git diff` does not show untracked new files. The framework now includes created files with standard `new file mode` and `/dev/null` headers, so manual reviewers can see newly extracted classes/modules in `applied_diff.patch`.

## LLM truncation handling

If Gemini returns a finish reason containing `MAX_TOKENS`, the attempt is treated as `patch_failed` before any patch is applied. The partially-generated response is still saved in `raw_response.json`, but the framework does not commit or test it.

The PR artifacts include the finish reason and token counts, for example:

```json
"llm_response": {
  "finish_reason": "FinishReason.MAX_TOKENS",
  "prompt_tokens": 12000,
  "completion_tokens": 65536
}
```

The stock configs use:

```yaml
max_output_tokens: 65536
```

The prompt also tells Gemini to return zero patch blocks rather than emit a partial large refactor when the change is too big to complete safely.

## Python test behavior

For Python projects, the adapter creates a `.venv` inside the workspace and installs the target package in editable mode. Then it captures baseline failures before applying refactors.

Tests are only run after a patch is successfully applied. The suite is not run for `detection_rejected`, `obsolete`, `llm_error`, or pre-apply `patch_failed` attempts.

The baseline capture runs the full suite once and stores failing pytest node ids. Per-attempt test runs then skip those known failing tests with pytest `--deselect=<nodeid>` and still use fail-fast (`-x`) on the remaining tests. This keeps pre-existing failures from stopping every refactor attempt while preserving the fast failure behavior for new regressions.

When tests fail after a patch, the framework compares the failures to the baseline:

- only pre-existing failures: the attempt may still pass
- new failures: status becomes `applied_failed`, and the workspace is reverted

At the end of a full Python run, unless `--no-final-suite` is used or only one issue was requested, the framework runs a final full-suite regression gate and writes `<repo>_full_suite_final.json`.

## Java patch-only behavior

For jackson-core and logstash, automated test gating is disabled in the current adapters. Successful Java attempts are committed with:

```text
applied_unverified
```

That means the patch applied cleanly and review artifacts were produced, but correctness must be judged manually from `pull_request.md`, `pull_request.json`, and `applied_diff.patch`.

## Re-running cleanly

To rerun a repo from scratch, archive or remove both the attempt artifacts and workspace clone:

```bash
# Archive first if you may need old artifacts later
mkdir refactor_attempts/_archives
mkdir refactor_workspaces/_archives
move refactor_attempts/seaborn-master refactor_attempts/_archives/seaborn-master_old
move refactor_workspaces/seaborn-master refactor_workspaces/_archives/seaborn-master_old

# Then rerun
python run_refactoring.py --config configs/seaborn.yaml
```

If you only changed rendering/reporting code and do not want new LLM calls, use:

```bash
python run_refactoring.py --config configs/seaborn.yaml --rerender-prs
```

If you only want master summaries rebuilt from existing PR JSON files, use:

```bash
python run_refactoring.py --config configs/seaborn.yaml --report-only
```
