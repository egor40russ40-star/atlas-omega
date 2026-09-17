# 13. CODE GENERATION, CONTRACTS AND SCAFFOLDING

Status: ARCHITECTURE ONLY
APK build: FORBIDDEN until explicit user command

## Goal

Reduce manual boilerplate, prevent drift between backend and Android, and make creation of new features predictable.

## Principle

Generate repetitive structure; hand-write behavior that carries product or security meaning.

Do not generate opaque business logic.

## Gateway contract generation

Target: define Gateway request/response contracts once and generate typed Android models/client stubs from that contract where practical.

Preferred flow:

Gateway API schema
  -> validation
  -> generated DTO/client layer
  -> hand-written repository/domain layer
  -> UI

Benefits:
- fewer spelling/type mismatches
- automatic detection of incompatible backend changes
- less handwritten serialization

Generated code must remain outside hand-written domain logic.

## Contract compatibility gate

CI must compare expected API contract to backend fixtures.

Breaking changes must fail before APK packaging.

RC2-compatible endpoints remain frozen unless an additive versioned change is explicitly approved.

## Feature scaffolding

Provide a project generator/template for new features that creates:

- feature module
- route
- screen state
- ViewModel contract
- repository interface dependency
- Russian strings placeholders
- unit test skeleton
- preview/fixture

Example command concept:

create-feature machines

Result must follow the architecture automatically instead of copying old screens manually.

## Terminal key specification as data

The programmable terminal keyboard should be described by a declarative model rather than dozens of hard-coded buttons.

Example concepts:
- key id
- Russian label
- emitted bytes/action
- modifier behavior
- repeat behavior
- category

The same specification can drive:
- UI
- tests
- default layouts
- settings editor

## Localization source of truth

User-facing text must come from Android resources/string catalogs, not hard-coded Compose strings.

Automation should detect:
- missing Russian strings
- accidental hard-coded user-facing English
- unused keys
- format placeholder mismatch

Technical terminal output is excluded from translation checks.

## Error catalog

Create structured error identifiers rather than ad-hoc error text.

Example domains:
- SSH_AUTH_FAILED
- SSH_HOST_KEY_CHANGED
- TAILSCALE_UNREACHABLE
- TMUX_ATTACH_FAILED
- SFTP_CONFLICT
- GATEWAY_UNAVAILABLE

Each error id maps to:
- Russian user message
- recovery action
- optional technical details
- telemetry category

This reduces repeated error-handling code.

## Screen state contracts

Standardize asynchronous screen state:

- Idle
- Loading
- Ready
- RecoverableError
- BlockingError

Avoid inventing different state handling in each feature.

## Fake generation

For every public repository/transport interface, provide deterministic fake implementations or builders for tests/previews.

Examples:
- FakeTerminalTransport
- FakeGatewayClient
- FakeFileRepository
- FakeSessionRegistry

This accelerates UI development without a live NucBox.

## Golden fixtures

Store small versioned fixtures for:
- /version
- machines
- jobs
- connection states
- terminal ANSI sequences
- SFTP conflicts

Fixtures must contain no secrets or real credentials.

## Dependency version source

Use one version catalog/lock source for:
- Compose
- terminal library
- SSH library
- AndroidX
- test libraries

Avoid scattered dependency versions in multiple Gradle files.

## Architectural code templates

Templates should enforce:
- interface-first design
- no direct secret persistence
- no direct cross-feature dependencies
- Russian resource keys
- test skeleton presence

## What must remain hand-written

Do not auto-generate without review:
- trust decisions
- key handling
- host-key verification policy
- reconnect semantics
- command execution semantics
- destructive file operations
- safety capability policy

## Expected acceleration

This layer should remove a significant amount of repetitive Android work and, more importantly, reduce rework caused by interface drift. Speed benefit must be measured from implementation metrics rather than assumed.

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
