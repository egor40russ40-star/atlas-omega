# ATLAS Mobile Android RC0

Thin Android shell for the ATLAS Mobile Super-App.

- package: `omega.atlas.mobile.debug` for debug RC0
- minimum Android: 8.0 (API 26)
- release mode: HTTPS only
- debug mode: HTTPS plus localhost HTTP for ADB reverse testing
- backend URL is configurable inside the app and persists locally

This module does not contain the ATLAS backend. It securely displays and controls the separately deployed ATLAS Mobile Control Gateway.
