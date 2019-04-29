Elektron Change Log
================

0.24 (2019-04-29)
-----------------
- [#24] Enhance internal structure of templates to handle showing authenticated content.
- [#25] Simplify signup/login UX by putting both forms on the home page, rather than two separate pages.
- [#23] Model & test collections
- [#27] Fix syntax error in collection templates.
- [#28] Migration to pytest, add testing coverage.
- [#31] Model & upload media items.
- [#33] Remove 'collection' model.
- Testing of upload signing, upload processing.
- Switch to use Poetry for dependency management.

0.23 (2019-01-15)
-----------------
- [#20] Enhance user profile by adding profile image url.
- [#12] Change model to use a UUID for primary key.

0.22 (2019-01-12)
-----------------
- [#15]: Configure mandatory email confirmation for new accounts.
- [#16]: Default email backend will print the message to console.
- [#3]: Fix error when trying to send email when signing up.
- [#17]: Add test for email confirmation flow.
- [#18]: Make username a required field when signing up.
- [#19]: Update tests to provide username.

0.21 (2019-01-08)
-----------------
- Add a couple of unit tests.

0.20 (2019-01-06)
-----------------
- [#4]: Implement Google signup/authentication.
- [#13]: Fix issue where Google signups caused "duplicate username" issue.

0.19 (2019-01-05)
-----------------
- Recreate environment to test logging & https config files.

0.18 (2019-01-05)
-----------------
- Configure HTTPS.

0.17 (2019-01-05)
-----------------
- Clean test.

0.16 (2019-01-05)
-----------------
- Clean test.

0.15 (2019-01-05)
-----------------
- [#9]: Introduce multi-container config in order to address underlying issues that prevented access to staging DB.

0.14 (2018-12-20)
-----------------
- Configured app to use PostgreSQL across multiple environments.

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
