# Repository Guidelines

This repository is a **documentation-first knowledge base** -- not a source code project. The primary content is structured Markdown maintained with Obsidian. Java/Spring source code lives in external repositories.

## Project Structure

- `README.md` -- Personal profile + open-source project showcase (12 projects).
- `note/` -- Core knowledge base: 14 top-level modules, ~900 Markdown files.
  - Modules follow `{nn}.{english-topic}/` naming (e.g., `01.java/`, `11.ai/`).
  - Each module has a `README.md` entry point with an 8-section index template.
  - Subdirectories: first layer uses `{nn}-{topic}/`; deeper layers use plain names.
- `note/CONTRIBUTING.md` -- Authoritative writing and formatting spec (template, frontmatter, naming, Mermaid diagrams).
- `note/12.story/` -- Narrative chapter format (see `STORY-FORMAT-SPEC.md`).
- `note/13.split-hairs/` -- Interview Q&A format (see `QUESTION-FORMAT-SPEC.md`).
- `.github/workflows/` -- CI: `grs.yml` (daily stats cards), `link-check.yml` (Markdown link validation).
- `profile/` -- GitHub README stat SVGs (auto-generated).

## Build, Test, and Validation Commands

There is no build step. Validate changes with:

- `ls note/` -- Overview of all 14 modules.
- `find note -name "README.md" -exec grep -L "^<!--" {} \;` -- Check frontmatter coverage.
- Markdown link checking runs automatically via CI (`link-check.yml`); config in `.mlc_config.json`.

## Coding Style and Naming Conventions

- **Language**: Chinese for prose content; English for directory/file names and code identifiers.
- **Frontmatter**: Every module `README.md` must include an HTML-comment frontmatter block (`<!--module: ... -->`, `<!--question: ... -->`, or `<!--story: ... -->`).
- **Diagrams**: Use Mermaid for architecture/flow diagrams; avoid PNG unless it is a teaching screenshot.
- **Indentation**: Standard Markdown; 2-space indent for nested lists.
- **Links**: Use relative paths for internal links (e.g., `[Topic](../dir/README.md)`).

## Commit and Pull Request Guidelines

Follow **Conventional Commits** with a module scope:

- `feat(<module>): ...` -- New content (e.g., `feat(11.ai): add RAG evaluation chapter`).
- `fix(<module>): ...` -- Corrections and typo fixes.
- `refactor(<module>): ...` -- Structural reorganization.
- `docs(<scope>): ...` -- Documentation updates.
- `style(<module>): ...` -- Formatting and template cleanup.

PRs should include a concise description, link related issues, and summarize the scope of Markdown changes.

## Agent-Specific Instructions

- When adding a new topic, first scan existing content with `grep`/`find` to avoid duplication.
- New leaf `README.md` files must include a `← [返回: <module>]` back-link.
- Always verify cross-module links and frontmatter after changes.
- Do not hardcode statistics (e.g., article counts) -- use `find` to compute them dynamically.

## Skills Reference

`skills/` is the single source of truth for all 4 project skills. `pre-commit` hook (`scripts/sync-skills.sh`) auto-syncs to `.codex/skills/` and `.claude/skills/`. Never edit `.codex/skills/` directly -- always modify `skills/<skill>/SKILL.md`.

| Skill | Trigger |
|-------|---------|
| `note-precipitation-planning` | User asks "where should topic X go in note/" |
| `note-audit-and-improvement` | User asks "what needs improvement in note/" |
| `note-content-quality` | User asks "how is the quality of this article" |
| `note-knowledge-qa` | User asks a technical question -- retrieve answer from `note/` |

## Precipitation Modes

Three patterns for adding new content, chosen by scope:

- **Single file** (< 150 lines): place directly as a sub-README under the target module.
- **Double layer** (most common): `13.split-hairs/<topic>/` + `11.ai/<module>/<topic>/` with cross-links.
- **Triple layer + story**: double layer + `12.story` chapter with back-references.

## Key Spec References

| Topic | Location |
|-------|----------|
| Module naming / template / frontmatter / section style | `note/CONTRIBUTING.md` |
| Story chapter format | `note/12.story/STORY-FORMAT-SPEC.md` |
| Interview Q&A format | `note/13.split-hairs/QUESTION-FORMAT-SPEC.md` |
| Module README standard structure | `note/CONTRIBUTING.md` §12 |

## Standard Precipitation Workflow

When adding a new topic to `note/`, follow this sequence:

1. **Survey**: `grep`/`find` to scan ≥ 5 related files for overlap.
2. **Depth check**: confirm high-frequency + deep content + real gap (3 signals).
3. **Location decision**: interview Q&A → `13.split-hairs`; deep principle → `11.ai`; narrative → `12.story`.
4. **Layer decision**: single / double / triple based on content depth.
5. **Present options**: give user 2-4 placement choices.
6. **Implement**: create files, add cross-links, use `feat(<slug>)` commit.
7. **Verify**: `git diff --check`, spot-check links, validate counts with `find`.

## Common Pitfalls

- Do not hardcode article counts (e.g., "47 articles") -- always compute with `find`.
- Do not claim file changes in commit messages that `git diff` does not reflect.
- Do not skip the `note/README.md` top-level index -- every new module/topic needs an anchor line there.
- Every new leaf `README.md` must include a `← [返回: <module>]` back-link.