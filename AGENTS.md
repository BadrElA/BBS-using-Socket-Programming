# AGENTS.md

Operating instructions for coding agents working in `BadrElA/BBS-using-Socket-Programming`.

## Repository scope

- Repository: `BadrElA/BBS-using-Socket-Programming`
- Project type: `unknown`
- Monorepo: no
- Purpose (from docs): BBS-using-Socket-Programming
Project 2 of Computer Networks

Group Members: Badr El Amri | Jason Galanie | Colin Hill

Required dependencies:

    WSL (windows only)
    g++
    make

How to install dependencies:

    Windows users only:
    open Terminal
    install WSL (first time only)
        wsl --install   
    Run all commands from WSL bash

    open Terminal (WSL bash fo



## Required inspection before changing code

1. Read this file and `PROJECT.md`.
2. Inspect relevant source files for the requested change.
3. Prefer existing scripts in package manifests / Makefiles / CI over invented commands.
4. Do not invent deployment or infrastructure steps without repository evidence.

## Allowed changes

- Source, tests, and configuration required to implement the requested task.
- Documentation when the task explicitly asks for docs, or when updating operating docs via an approved docs PR.

## Restricted changes

- Do **not** commit secrets, tokens, private keys, or production credentials.
- Do **not** create placeholder implementation files (`AUTOMATION_NOTES.md`, `RETRY_*.md`, task-description copies).
- Do **not** skip required validation when scripts exist.
- Do **not** open a pull request without meaningful repository changes.
- Do **not** deploy or merge to protected/default branches without explicit approval.
- Do **not** modify generated build artifacts unless the task requires it.

## Coding conventions

- Languages: Unknown — requires repository owner confirmation.
- Frameworks: none detected
- Package managers: Unknown — requires repository owner confirmation.

## Required validation

- Tests: Unknown — requires repository owner confirmation.
- Typecheck: Unknown — requires repository owner confirmation.
- Lint: Unknown — requires repository owner confirmation.
- Build: Unknown — requires repository owner confirmation.

## Branch / PR expectations

- Use a dedicated feature/fix/docs branch — never commit directly to the default branch.
- PR descriptions must summarize real changes and validation performed.
- Documentation-only PRs must not modify runtime source unless requested.

## Deployment restrictions

- Unknown — requires repository owner confirmation.


---

## Evidence & review

- Project type: `unknown`
- Languages: Unknown — requires repository owner confirmation.
- Generated from repository inspection (not guessed from external context).
- Evidence paths:
  - `README.md`
- Last review: automated ARTI repository intelligence
