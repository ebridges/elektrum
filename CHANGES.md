Elektron Change Log
================

0.6 (unreleased)
----------------
- Nothing changed yet.

0.5 (2018-12-10)
----------------
- Organize Django project files under a subdirectory, and expose some product information to the templates so that we know what version is being displayed.

0.4 (2018-12-09)
----------------
- Run migrations before running server to collect static files and apply any db changes.

0.3 (2018-12-09)
----------------
- Pause before a deploy, and rely on defaults for release bundling.

0.2 (2018-12-09)
----------------
- Health checks are done direct to IP address, which is not in ALLOWED_HOSTS and causing the health check (and deploy) to fail.

0.1 (2018-12-09)
----------------
- Fix stray char in ALLOWED_HOSTS that caused a bad request.
- Fix typo in app name in Dockerfile.

0.0 (2018-12-08)
----------------
- Nothing changed yet.
