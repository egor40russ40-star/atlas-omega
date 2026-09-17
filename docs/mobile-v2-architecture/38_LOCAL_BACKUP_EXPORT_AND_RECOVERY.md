# 38 — Local Backup, Export and Recovery

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Allow recovery of user configuration and workflow context without exporting credentials or creating a second secret store.

## Exportable data
May include:
- workspace definitions;
- connection labels and non-secret host metadata;
- UI preferences;
- terminal font/keyboard layout;
- snippets/macros that do not contain secrets;
- navigation/editor preferences;
- local draft metadata where explicitly selected;
- feature settings;
- schema/version metadata.

## Never export by default
- private keys;
- passwords/passphrases;
- bearer/session tokens;
- Android Keystore material;
- raw credential blobs;
- terminal scrollback;
- clipboard;
- arbitrary remote file contents.

## Recovery model
The recovery archive restores configuration, not trust.

After import:
1. validate archive schema/version;
2. show import preview;
3. restore non-secret configuration;
4. mark protected connections as `ТРЕБУЕТ ПОВТОРНОЙ ПРОВЕРКИ`;
5. perform host/device trust verification again;
6. generate/re-enroll credentials when needed.

## Archive format
- versioned manifest;
- structured JSON/config entries;
- optional user-selected local artifacts;
- checksums;
- no executable content;
- strict parser and size limits.

## Conflict handling
Import never silently overwrites newer local state. User chooses merge/replace per category where meaningful.

## Automatic local recovery
The app keeps bounded transactional snapshots of its own non-secret local database before schema migration. On failed migration, rollback to previous local schema state is allowed.

## Disaster recovery
Loss/reinstall of Android device must not threaten remote source code or tmux processes because authoritative work lives on remote nodes/repos. New app install re-enrolls and reconnects.

## Acceptance
CONFIG_EXPORT = YES
SECRET_EXPORT_DEFAULT = NO
TRUST_RESTORED_FROM_ARCHIVE = NO
IMPORT_PREVIEW = REQUIRED
SCHEMA_ROLLBACK = REQUIRED
