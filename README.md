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

Available configs out of the box: [configs/seaborn.yaml](configs/seaborn.yaml) (Python), [configs/jackson-core.yaml](configs/jackson-core.yaml) (Java), [configs/logstash.yaml](configs/logstash.yaml) (Java+Ruby).

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
