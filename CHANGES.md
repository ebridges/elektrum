Elektron Change Log
================

0.14 (unreleased)
-----------------

- Nothing changed yet.


0.13 (2018-12-16)
-----------------
- Add a single selenium-based integration test to provide basis for further tests.

0.12 (2018-12-16)
-----------------
- Require an email address & first/last names for login, ignoring username field; require unit tests to run and succeed before deploying.

0.11 (2018-12-14)
-----------------
- Ensure the app is on the tag so that `version.txt` has a non-`dev` version number.

0.10 (2018-12-14)
-----------------
- Misc fixes around version number.

0.9 (2018-12-14)
----------------
- [#1]: Add a library to proxy static files in-app, resolving issue where static files were 404 on beanstalk.
- [#2]: After the previous fix it turned out that files were not available to nginx, leading to 404 errors -- explaining the need for a volume LoL.  Also, to better determine what version is running add some logic to rebuild the image each deploy and version it.

0.8 (2018-12-14)
----------------
- Fix bug in condition check in deploy script.

0.7 (2018-12-12)
----------------
- Add test to confirm static files are configured properly.

0.6 (2018-12-12)
----------------
- Correct a bunch of misc errors with running container, document it better, and fail releases if container is not functioning correctly.

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
