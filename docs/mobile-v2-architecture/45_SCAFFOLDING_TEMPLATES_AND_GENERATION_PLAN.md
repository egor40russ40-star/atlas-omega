# 45 — Scaffolding Templates and Generation Plan

## Status
PRE-IMPLEMENTATION EXECUTION SPEC

## Goal
Avoid spending implementation time on repetitive Gradle/module/feature boilerplate.

## Generated artifacts
Templates may generate:
- module `build.gradle` skeletons;
- package directories;
- feature contract/interface shells;
- fake implementations;
- baseline unit-test classes;
- Compose screen/view-model state shells;
- localization resource placeholders;
- benchmark/test fixture shells;
- typed error/result wrappers where contract permits.

## Never auto-generate without review
- security-sensitive credential code;
- host identity verification logic;
- shell command execution semantics;
- file overwrite/conflict rules;
- authorization/trust decisions;
- release signing logic.

## Feature template
Every feature module starts with:
1. contract;
2. model/state;
3. fake implementation;
4. unit-test fixture;
5. UI entry point if applicable;
6. Russian strings placeholder;
7. module README with ownership and dependency rules.

## Transport template
Every transport module starts with:
- transport contract implementation;
- deterministic fake endpoint/client;
- lifecycle tests;
- failure mapping tests;
- timeout/retry policy declaration;
- no UI dependency.

## Code generation rules
- generated files carry a generated marker;
- source-of-truth schema/template is versioned;
- manual edits to generated sections are blocked or overwritten intentionally;
- generated output must compile independently before integration;
- generation must be deterministic.

## Localization generation
Central catalog generates/checks:
- required Russian keys;
- missing translation report;
- duplicate/inconsistent status labels;
- allowed technical-English exceptions.

## Terminal keyboard generation
Keyboard layout is declarative and may generate:
- button rows;
- key-sequence mappings;
- modifier metadata;
- accessibility labels;
- test vectors.

## Speed metric
Measure scaffold generation time and first successful module compile. Repetitive manual file creation should approach zero for standard modules.

## Acceptance
DETERMINISTIC_SCAFFOLDING = REQUIRED
FAKE_FIRST = REQUIRED
SECURITY_LOGIC_AUTOGENERATION = FORBIDDEN
RUSSIAN_RESOURCE_CHECK = REQUIRED
