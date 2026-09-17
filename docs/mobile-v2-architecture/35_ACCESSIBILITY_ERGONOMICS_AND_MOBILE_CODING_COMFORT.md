# 35 — Accessibility, Ergonomics and Mobile Coding Comfort

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Make long coding sessions on a phone physically usable, not merely technically possible.

## Core ergonomics
- terminal content gets maximum screen area;
- connection/setup UI never occupies the normal terminal screen;
- bottom controls remain reachable one-handed;
- landscape mode is first-class, not a stretched portrait layout;
- keyboard toolbar may collapse to one row and expand on demand;
- user can hide navigation chrome for true fullscreen terminal.

## Text and terminal
User-adjustable:
- terminal font size;
- line height;
- cursor style;
- cursor blink;
- terminal contrast;
- editor font size;
- toolbar density;
- scroll sensitivity.

Pinch-to-zoom changes terminal font/PTY geometry coherently.

## Touch targets
Interactive controls should target at least comfortable Android touch dimensions. Dense terminal shortcut rows may use compact visual cells but must preserve reliable hit boxes.

## Modifier ergonomics
CTRL/ALT/SHIFT support:
- momentary tap;
- lock/double-tap;
- visible active state;
- clear cancel gesture;
- physical keyboard parity.

## Haptics
Optional light haptic feedback for:
- modifier activation;
- shortcut execution;
- tab change;
- destructive confirmation.

Haptics are configurable and disabled for continuous terminal typing.

## Accessibility
- TalkBack labels for app controls;
- scalable app UI text independent from terminal grid when needed;
- high-contrast mode;
- no meaning encoded by color alone;
- status icons paired with text;
- focus order defined for connection/settings screens.

Raw terminal screen-reader behavior is treated separately from native app chrome to avoid corrupting terminal semantics.

## Orientation
Portrait priorities:
1. terminal/editor;
2. keyboard toolbar;
3. compact navigation.

Landscape priorities:
1. terminal/editor split or larger terminal;
2. optional files/code side pane;
3. minimal persistent chrome.

## Long-session safeguards
- optional keep-screen-awake per active session;
- explicit user control over screen-awake behavior;
- no forced maximum brightness;
- reconnect does not steal keyboard focus unexpectedly;
- notification only for meaningful session state changes.

## Productivity metric
Track locally (opt-in or non-identifying aggregate only):
- taps to open active terminal;
- taps to execute common shortcut;
- time from app launch to terminal ready;
- accidental navigation rate in usability tests;
- successful one-handed use for critical actions.

## Acceptance
TERMINAL_FULLSCREEN = REQUIRED
LANDSCAPE_FIRST_CLASS = YES
KEYBOARD_TOOLBAR_COLLAPSIBLE = YES
ACCESSIBILITY_LABELS = REQUIRED
COLOR_ONLY_STATUS = FORBIDDEN
