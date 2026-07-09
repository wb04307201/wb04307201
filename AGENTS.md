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