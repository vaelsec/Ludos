# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

**Ludos** is a project by vaelsec (dev@vael.ie), currently in its initial stages. The repository contains only a skeleton `README.md` and no application code yet.

- **Primary branch:** `main`
- **Remote:** `http://local_proxy@127.0.0.1:46599/git/vaelsec/Ludos`

## Current State

The repository is freshly initialized with a single commit. There is no:
- Application code
- Build system
- Test framework
- Dependency manifest
- CI/CD configuration

All development context below represents conventions to establish as the project grows.

## Development Workflow

### Branch Strategy

- Develop features on short-lived branches off `main`
- Branch naming: `<type>/<short-description>` (e.g., `feat/game-engine`, `fix/input-handling`)
- Push with tracking: `git push -u origin <branch-name>`
- Open a PR to merge into `main`

### Commits

- Write commit messages in the imperative mood: "Add X", "Fix Y", "Remove Z"
- Keep the subject line under 72 characters
- Reference issues when relevant: `Fix input lag (#42)`

## Code Conventions

No language or framework has been chosen yet. When the stack is established, update this section with:
- Language version and runtime
- Formatting tool and configuration
- Linting rules
- File/directory naming conventions

## Testing

No test framework is configured. When one is added, document here:
- How to run the full test suite
- How to run a single test
- Where tests live relative to source files

## Key Files and Directories

| Path | Purpose |
|------|---------|
| `README.md` | Project introduction (stub) |
| `CLAUDE.md` | This file — AI assistant guidance |

## Notes for AI Assistants

- The project is in its earliest stage; avoid assuming any particular language or framework.
- Do not add features, abstractions, or tooling beyond what the task explicitly requires.
- Prefer editing existing files over creating new ones.
- Do not commit secrets, credentials, or environment files.
- Update this file whenever significant project structure or conventions are established.
