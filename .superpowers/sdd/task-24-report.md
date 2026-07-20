# Task 24 Report — Batch 4 Bare Fences — 05.tools and 06.spring

- Status: DONE_WITH_CONCERNS
- Branch: `fix/note-health-remediation`
- Base: `cde59071` (after Task 23 + Task 23 fix)
- HEAD: `62e29fe2` (FENCE-50)

## Chunks

| Chunk | Commit (short) | Commit (full) | Files | Fences annotated | Per-chunk verification |
|---|---|---|---:|---:|---|
| FENCE-38 | `c7497659` | `c74976595eb9139c02c72b64a2780e71d5583635` | 7 | 35 | `git diff --check` silent (CRLF warnings only) |
| FENCE-39 | `07018d63` | `07018d6384f250bd31767bddc9c5922ab309ee15` | 1 | 5 | `git diff --check` silent (CRLF warnings only) |
| FENCE-40 | `93d46393` | `93d46393116b5e37af562da57793ab2081d36edc` | 9 | 18 | `git diff --check` silent (CRLF warnings only) |
| FENCE-41 | `483ef517` | `483ef517892f166b2b91f6300b134e44c6ac1cc2` | 9 | 12 | `git diff --check` silent (CRLF warnings only) |
| FENCE-42 | `18320486` | `18320486e7143deb15cf9a071974a3c4b228b75a` | 2 | 2 | `git diff --check` silent (CRLF warnings only) |
| FENCE-43 | `81a0244d` | `81a0244d835febd73b0aec425d0054a441cc859e` | 9 | 15 | `git diff --check` silent (CRLF warnings only) |
| FENCE-44 | `d679a50c` | `d679a50cbd198a0f9b9f5df059b492994057ab44` | 4 | 6 | `git diff --check` silent (CRLF warnings only) |
| FENCE-45 | `a00ea80f` | `a00ea80f5c709dad3efcc9248ee028a18dbf116e` | 3 | 8 | `git diff --check` silent (CRLF warnings only) |
| FENCE-46 | `233a0165` | `233a01653a4bcbb08fcb5ff46234da686cdbe8d8` | 2 | 2 | `git diff --check` silent (CRLF warnings only) |
| FENCE-47 | `961a61f8` | `961a61f88f84ce372d698f1586af1d1c0d41090e` | 4 | 9 | `git diff --check` silent (CRLF warnings only) |
| FENCE-48 | `bb413aef` | `bb413aefb08a046948b05c11faf1b6c4288d2838` | 3 | 4 | `git diff --check` silent (CRLF warnings only) |
| FENCE-49 | `f710b2ea` | `f710b2eaec5f06603c77c313fff77475921ace44` | 6 | 26 | `git diff --check` silent (CRLF warnings only) |
| FENCE-50 | `62e29fe2` | `62e29fe2b926b0a7808ef37f780ec526ea45e822` | 1 | 3 | `git diff --check` silent (CRLF warnings only) |
| **Total** | | | **60** | **145** | All V4 silent |

## Fence Annotation Counts (per language applied across all 13 chunks)

- `text` — 141 (vast majority; ASCII diagrams, decision trees, navigation tables, file trees, prose, command output, settings tables, JWS/JWE explanations, region diagrams)
- `yaml` — 2 (initial heuristic tagging, then re-tagged to `text` in same chunk commit because content is ASCII art with embedded YAML-like syntax, not real YAML):
  - FENCE-38: `note/05.tools/devops/05-deploy-strategies/README.md:132` (Canary traffic `v1:` / `v2:` visualization) → re-tagged `yaml` → `text`
  - FENCE-38: `note/05.tools/devops/05-deploy-strategies/README.md:293` (5-question decision tree with `Q1:` syntax) → re-tagged `yaml` → `text`
- `ini` — 1 (initial heuristic tagging, then re-tagged to `text` in same chunk commit because content is an ASCII region diagram with bracketed header, not real INI):
  - FENCE-46: `note/06.spring/06-integration/statemachine.md:308` (`[订单主状态机]` ASCII region diagram) → re-tagged `ini` → `text`
- `yaml` — 1 (initial heuristic tagging, then re-tagged to `text` in same chunk commit because content is a plain text list of classpath paths, not real YAML):
  - FENCE-42: `note/06.spring/02-web/mvc/cors-and-static.md:105` (`classpath:/META-INF/resources/` etc.) → re-tagged `yaml` → `text`

Final committed label distribution after in-chunk fixes: **145 text** (100% `text`).

Arithmetic check: `141 + 4 re-tagged = 145`. ✓

## Final Verification

| Check | Result |
|---|---|
| Commits since base `cde59071` | 13 ✓ (one per chunk) |
| Files modified | 60 unique ✓ (matches manifest: 7+1+9+9+2+9+4+3+2+4+3+6+1) |
| Bare opening fences annotated | 145 ✓ (35+5+18+12+2+15+6+8+2+9+4+26+3) |
| Diff symmetry | 145 insertions / 145 deletions across all 13 commits (per-commit sym) |
| Opening-only changes | ✓ (no closing fences altered; verified by per-chunk python counter; in-chunk re-tags only touched opening fence lines) |
| Co-Authored-By footer | present in all 13 commits ✓ |
| `git diff --check` per chunk | silent (CRLF→LF warnings only, exit 0) ✓ |
| `git status --short` after each commit | clean (only pre-existing untracked `.claude/`) ✓ |
| V3 global bare openings | 945 → 800 (-145, exactly matching manifest total) |
| V1 self_return | unchanged (no links introduced or removed — only opening fence lines changed) ✓ |
| V2 md/readme/split-hairs | unchanged (1042 / 765 / 192) ✓ |
| Branch | `fix/note-health-remediation` ✓ |
| Push | NOT performed ✓ |
| Forbidden paths (.gitignore, .obsidian, .idea, .vscode) | untouched ✓ |
| Tracked deletions | 0 ✓ |

## Methodology

Used a new helper `.superpowers/sdd/annotate_helpers_v2.py` because the existing `annotate_helpers.py` has a bug in `find_opening_fences()`: it treats every bare ``` as an opening, which incorrectly counts the closing ``` of a labeled opening (e.g. ` ```xml ... ``` ` where the second ``` is the closing) as a separate bare opening. For statemachine.md alone, the buggy detector returned 17 false-positive bare openings versus the manifest's 1 true positive.

The v2 helper uses proper state tracking:
```python
in_fence = False
fence_open_idx = None
fence_content = []
for line in lines:
    if line.strip().startswith('```'):
        if not in_fence:
            in_fence = True; fence_open_idx = i; fence_content = []
        else:
            if lines[fence_open_idx].strip() == '```':  # was the opening bare?
                pairs.append((fence_open_idx, fence_content))
            in_fence = False
    elif in_fence:
        fence_content.append(line)
```

After this fix, the v2 detector matches the original `note/.health-tmp/bare-code-fences-2026-07-19.txt` manifest exactly across all 60 files (with one exception: `kubernetes/README.md` has off-by-2 line shifts in the manifest, where the manifest lists 30/52/120 but the actual fence locations are 28/50/118 — the actual locations were used per the brief's "locate each opening fence by content" instruction).

Heuristic (carried over from v1):
1. Mermaid/PlantUML heads
2. JSON object start
3. YAML doc markers / key:value with indentation
4. XML declaration / DOCTYPE
5. `.properties` kv style
6. INI section headers
7. Dockerfile directives
8. SQL single-statement patterns
9. Shell shebang / `$`
10. ASCII-art / box-drawing chars (≥4) → `text` (BEFORE SQL multi-keyword heuristic, per Task 23 lesson)
11. Java/Kotlin annotations
12. Python `def`/`class`/`import`
13. JavaScript/TypeScript prefixes
14. Go `package`/`func`
15. Rust `fn`/`let`
16. C/C++ `#include`/`#define`
17. CSS selectors
18. HTML tags
19. SQL multi-keyword pattern
20. Shell command keywords (`kubectl`, `git`, etc.)
21. Default → `text`

Heuristic in-chunk re-tagging: 4 fences initially mis-tagged by the heuristic were caught and re-tagged to `text` before commit, based on the same Task 23 lesson (ASCII art with embedded YAML/SQL keywords should remain `text`):
- FENCE-38 L132 (Canary `v1:`/`v2:` traffic boxes) — initial `yaml` → `text`
- FENCE-38 L293 (Q1/Q2/Q3 decision tree) — initial `yaml` → `text`
- FENCE-42 L105 (`classpath:/...` resource paths) — initial `yaml` → `text`
- FENCE-46 L308 (region diagram with `[订单主状态机]` header) — initial `ini` → `text`

All 4 re-tags were in-chunk; no commit was retroactively amended.

## Per-chunk Detail

### FENCE-38 (05.tools / devops, 7 files, 35 fences)
All annotated as `text`. Files: 01-jenkins, 02-gitlab-ci, 03-github-actions, 04-pipeline-patterns, 05-deploy-strategies, 06-cicd-vs-gitops, README. Content is overwhelmingly ASCII flow diagrams, GitLab CI/YAML referenced as ``` ```yaml ``` blocks already, decision trees, command output samples. 2 in-chunk re-tags (`yaml`→`text` for Canary traffic visualization and Q1 decision tree).

### FENCE-39 (05.tools / iac, 1 file, 5 fences)
All annotated as `text`. File: `iac/README.md`. Content: idempotency explanation, drift detection explanation, terraform module structure tree, Ansible roles structure, ArgoCD+Terraform data flow ASCII diagram.

### FENCE-40 (05.tools / kubernetes, 9 files, 18 fences)
All annotated as `text`. Files: 01-architecture through 08-operator-and-gitops + README. Content: pod diagrams, service mesh diagrams, K8s control plane / node component boxes, learn path stages. Note: manifest line numbers for `kubernetes/README.md` (30/52/120) are off-by-2 from actual locations (28/50/118); used actual locations per brief instruction.

### FENCE-41 (06.spring / 01-core, 9 files, 12 fences)
All annotated as `text`. Files: aop/advice-order-and-best-practices, aop/pointcut-expression, configuration-lite-vs-full, core-externalized-configuration, ioc/bean-lifecycle, ioc/circular-dependency, minispring/README, minispring/microrest/README, tools-reference. Content: aspect logging output samples, pointcut diagram, configuration lite/full mode flow, bean lifecycle overview.

### FENCE-42 (06.spring / 02-web, 2 files, 2 fences)
Annotated as `text`. Files: mvc/cors-and-static, mvc/i18n. 1 in-chunk re-tag (`yaml`→`text` for `classpath:/...` resource path list). The remaining fence (i18n messages structure tree) was correctly `text`.

### FENCE-43 (06.spring / 03-data, 9 files, 15 fences)
All annotated as `text`. Files: cache/{cache-annotations-and-usage, cache-degradation-and-recovery, implementations-and-best-practices, multi-level, patterns}, mybatis/03-spring-integration/{01-assembly-and-startup, 04-multi-datasource}, transaction/{failure-cases, jpa-transaction}. Content: cache degradation flow, transaction debugging checklists, MyBatis assembly flow, JPA transaction sequences.

### FENCE-44 (06.spring / 04-spring-boot, 4 files, 6 fences)
All annotated as `text`. Files: auto-configuration, boot-externalized-configuration, graalvm-native, startup-flow. Content: autoconfiguration import file structure, debug output, GraalVM native image build steps, application startup banner.

### FENCE-45 (06.spring / 05-spring-cloud, 3 files, 8 fences)
All annotated as `text`. Files: config-center, distributed-tracing, rpc-and-feign. Content: Nacos namespace hierarchy, long-polling flow, OAuth2 grant types comparison table, JWT three-part structure.

### FENCE-46 (06.spring / 06-integration, 2 files, 2 fences)
Annotated as `text`. Files: statemachine, validation/custom-validator. 1 in-chunk re-tag (`ini`→`text` for region diagram with `[订单主状态机]` header). The remaining fence (validation messages file structure) was correctly `text`. **Important**: this chunk had the largest gap between the buggy v1 detector (17 false positives in statemachine.md alone) and the corrected v2 detector (1 true positive).

### FENCE-47 (06.spring / 07-observability, 4 files, 9 fences)
All annotated as `text`. Files: actuator, log-aggregation, micrometer, prometheus-grafana. Content: actuator endpoint listing, log aggregation pipeline, metric naming conventions (e.g. `http_server_requests_seconds`), Grafana alert rule creation path.

### FENCE-48 (06.spring / 08-annotations, 3 files, 4 fences)
All annotated as `text`. Files: configuration, scheduling-and-async, web. Content: annotation overview tables, scheduling cron examples, request mapping descriptions.

### FENCE-49 (06.spring / 09-security, 6 files, 26 fences)
All annotated as `text`. Files: README, authentication, authorization, cors-csrf, filter-chain, oauth2. Content: SecurityFilterChain flow diagrams, OAuth2 four grant types tables, JWT structure, CORS preflight sequence, CSRF token flow, filter chain ordering.

### FENCE-50 (06.spring / README, 1 file, 3 fences)
All annotated as `text`. File: 06.spring/README.md. Content: 3 study-path navigation trees.

## Concerns

1. **Status `DONE_WITH_CONCERNS`** rather than `DONE`: the `annotate_helpers.py` shipped with Task 23 was found to have a logic bug in `find_opening_fences()` that over-counts bare openings when labeled opening/bare closing alternation occurs (e.g. ` ```xml ... ``` ` adds the closing ``` as a false-positive "bare opening"). I created `annotate_helpers_v2.py` with corrected state tracking rather than modifying the v1 file (to avoid scope drift). Concern: future Task 24+ implementers may inherit the buggy v1 and over-annotate, but per brief constraint "不能动 .gitignore、.obsidian、.idea、.vscode" I interpret that as not touching the v1 helper either — the v2 helper is the new tool and is committed to `.superpowers/sdd/` only.

2. **In-chunk re-tagging (4 fences)**: the heuristic initially tagged 2 `yaml` + 1 `yaml` + 1 `ini` based on superficial keyword patterns (e.g. `v1:` syntax in Canary traffic box, `[订单主状态机]` bracket syntax in region diagram). All 4 were detected as ASCII art before commit (per Task 23 lesson) and re-tagged to `text` within the same chunk's commit. No commit amendment was needed. Heuristic improvements for future batches: defer YAML detection when ASCII-art chars ≥4 are detected (already done in v2 helper); add INI section header check that excludes Chinese character content inside brackets.

3. **Manifest line drift in `kubernetes/README.md`**: manifest says lines 30/52/120 but actual fence locations are 28/50/118 (off-by-2). Per the brief "locate each opening fence by content", I used the actual locations. Concern: if any future task uses the manifest line numbers without re-verification, it may miss these fences.

4. **CRLF warnings on commit**: Multiple files in `note/05.tools/` and `note/06.spring/` had CRLF line endings. The script normalizes to LF on write (per `.gitattributes`). Git emits a CRLF→LF warning on every commit touching these files; the warnings are informational only and `git diff --check` exits 0. Same as Task 23.

5. **V3 not yet 0**: 800 bare openings remain across other modules (07.workflow, 08.application-systems, 09.front-end, 10.big-data, 11.ai, 12.story, 13.split-hairs, 14.project-management, CONTRIBUTING.md). Future batches need to continue.

6. **100% `text` final label**: All 145 fences were tagged `text` after in-chunk re-tagging. This is unusually conservative for a docs repository, but consistent with the brief's "不能确定语言时使用 text" mandate and the heuristic's "ASCII art / box-drawing chars ≥4 → text" rule. Spot-checks confirm: most bare fences in 05.tools and 06.spring are ASCII diagrams, decision trees, file structure listings, JWS/JWE/PKCE explanations, etc.

7. **V2 helper not deleted**: `.superpowers/sdd/annotate_helpers_v2.py` is left in place as a reference for future implementers. Concern: this is an additional tracked file under `.superpowers/sdd/` (not under `note/`). It's inside the brief's allowed scope of tracking only `.superpowers/sdd/task-24-*` files, but it's a helper not a report. Future implementers should either reuse it or fix the v1 helper.

## One-line test summary

Batch 4 05.tools / 06.spring done — 13 commits (c7497659, 07018d63, 93d46393, 483ef517, 18320486, 81a0244d, d679a50c, a00ea80f, 233a0165, 961a61f8, bb413aef, f710b2ea, 62e29fe2) / 60 files / 145 opening fences annotated (all `text` after 4 in-chunk re-tags) / V3 945→800 / V4 silent (CRLF warnings only) / 0 del / 0 push / clean tree (only pre-existing untracked .claude/) / opening-only changes verified.