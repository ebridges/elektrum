# Elektrum Change Log

## v0.7.1 (2020-09-07)

### Fix

- reenable db migration task

## v0.7.0 (2020-09-07)

### Fix

- avoid key error when getting options.

### Feat

- new column: `focal_length` shows formatted view of value, e.g. "f/5.6"
- integration of new metadata-processor, along with HTTP interface for it
- switch to use new version of metadata-processor

### Refactor

- get all the var names straight, conforming them to the other services.
- separate out iam config for different services to facilitate working with them.

## v0.6.2 (2020-08-06)

### Fix

- update component versions.

## v0.6.1 (2020-08-02)

### Fix

- remove automated static deploy, too many issues to bother with
- provide proper datastructure for a Doit action.
- inadvertent reference to self

## v0.6.0 (2020-07-30)

### Feat

- publish a new release to sentry whenever one of the services is deployed

### Refactor

- blend repo and account names when defining repo name

## v0.4.3 (2020-07-27)

### Fix

- wrong package name

## v0.4.2 (2020-07-26)

### Fix

- prognosticate next version.

## v0.4.1 (2020-07-26)

### Refactor

- remove logic for publishing static files out of Makefile, as its much more reliable in deploy script
- update references to map files.
- only publish and commit if files have changed
- append newline explicitly

## v0.4.0 (2020-07-24)

### Fix

- include patch to js module so that deploys of static files dont generate multiple new files even when nothing has changed.

## v0.3.0 (2020-07-24)

### Fix

- Convert to use a versioned dep rather than a git ref.

### Refactor

- update references to build modules and folders
- build scripts now only do deploying

## v0.2.0 (2020-07-22)

### Fix

- use correct name for variable.

### Refactor

- improve logging and comments

### Feat

- switch application service to deploy from a version rather than build it first.

## v0.1.0 (2020-07-20)

### Fix

- do not truncate release notes when gathering them
- include recent changes in the release notes.
- **release**: correct path to archive and initialization of version
- additional incorrect path for version.txt
- incorrect path for version.txt
- workaround issue with hashes on editable deps.  pip does not allow hashes on "editable" deps (i.e. deps on repos like django-storages) cf.: https://github.com/pypa/pip/issues/4995

### Refactor

- convert dependencies to `dev` deps where possible

### Feat

- **release**: add support for automated releases

## v0.0.53 (2020-06-19)

- Add new build/deploy script
- Add Django Admin commnds for configuring remote system.

## v0.0.52 (2020-05-30)

- Minor fixes to configure Sentry release metadata.

## v0.0.51 (2020-05-30)

- Minor fixes to configure Sentry release metadata.

## v0.0.50 (2020-05-30)

- Minor fix in configuration of Org name when publishing release to Sentry.

## v0.0.49 (2020-05-30)

- Add additional metadata when publishing release to Sentry.

## v0.0.48 (2020-05-30)

- Minor fix in format of release URL.

## v0.0.47 (2020-05-30)

- Minor fix for publishing release to Sentry.

## v0.0.46 (2020-05-30)

- Minor fixes in operational notifications.

## v0.0.45 (2020-05-30)

- [#86] Implement security and operational fixes in prep for deployment.

## v0.0.44 (2020-04-21)

- Dev module was unable to be run in a non-local env.

## v0.0.43 (2020-04-21)

- [#77] Fix for bug in sharing.

## v0.0.42 (2020-04-20)


## v0.0.41 (2020-04-19)

- Add capability to share one or more images from a given album.
- Integrate with Github CI

## v0.0.40 (2020-02-01)

- Misc cleanup and consolidation.

## v0.0.39 (2020-02-01)

- Completed migration from Bitbucket to GitHub, including issues.
- Consolidated documentation from bitbucket wiki.
- Fix for 'Access Denied' error when uploading images.

## v0.0.38 (2020-01-05)

- When app is released publish changelog to GitHub as a release.

## v0.0.37 (2020-01-05)

- Rewrite of `elektrum-deploy` script.

## v0.0.36 (2019-12-15)

- Rewrite of `elektrum-release` script.

## v0.0.35 (2019-12-11)

- Introduce automated increment of pyproject version number from version.txt.

## v0.0.34 (2019-12-10)

- [#63] Replace Zappa with LGW for deployment.

## v0.0.33 (2019-10-22)

- [#62] Add API for uploading via CLI.

## v0.0.32 (2019-09-20)

- [#57] Implement media upload via web browser.
- [#58] Automate provisioning of different environments.
- [#60] Rename project from `elektron` to `elektrum`.
- [#61] Fix "Forbidden" error when uploading images.
- Upgrade all dependencies.

## v0.0.31 (2019-07-25)

- [#50] Refactor network into separate, but identical environments.
- [#38] Multistage deployment environments
- [#43] Provide capability to reset a release to previous version.

## v0.0.30 (2019-06-28)

- [#48] Minimize dependency on ELEKTRON_ENV environment variable.

## v0.0.29 (2019-06-27)

- [#45] Switch from Elastic Beanstalk to use Zappa for deployment as a Lambda.
- [#49] Configuration of a NAT instance to allow for DB access from a Lambda.

## v0.0.28 (2019-05-27)

- [#41] Improve robustness of photo processor deployment.

## v0.0.27 (2019-05-27)

- [#36] Eliminate requirement to include create date when requesting image upload.
- [#37] Views and model for date-based views of media (collections, albums, items).
- [#10] Configure CDN, HTTPS, and bucket setup.
- [#40] Populate the date dimension table with a default range from 1/1/1970-12/31/2050.

## v0.0.26 (2019-04-30)

- [#35] Upload lambda binary to S3 before deploy.


## v0.0.25 (2019-04-29)

- [#34] Deploy versioned lambda function for the image processor.


## v0.0.24 (2019-04-29)

- [#24] Enhance internal structure of templates to handle showing authenticated content.
- [#25] Simplify signup/login UX by putting both forms on the home page, rather than two separate pages.
- [#23] Model & test collections
- [#27] Fix syntax error in collection templates.
- [#28] Migration to pytest, add testing coverage.
- [#31] Model & upload media items.
- [#33] Remove 'collection' model.
- Testing of upload signing, upload processing.
- Switch to use Poetry for dependency management.

## v0.0.23 (2019-01-15)

- [#20] Enhance user profile by adding profile image url.
- [#12] Change model to use a UUID for primary key.

## v0.0.22 (2019-01-12)

- [#15]: Configure mandatory email confirmation for new accounts.
- [#16]: Default email backend will print the message to console.
- [#3]: Fix error when trying to send email when signing up.
- [#17]: Add test for email confirmation flow.
- [#18]: Make username a required field when signing up.
- [#19]: Update tests to provide username.

## v0.0.21 (2019-01-08)

- Add a couple of unit tests.

## v0.0.20 (2019-01-06)

- [#4]: Implement Google signup/authentication.
- [#13]: Fix issue where Google signups caused "duplicate username" issue.

## v0.0.19 (2019-01-05)

- Recreate environment to test logging & https config files.

## v0.0.18 (2019-01-05)

- Configure HTTPS.

## v0.0.17 (2019-01-05)

- Clean test.

## v0.0.16 (2019-01-05)

- Clean test.

## v0.0.15 (2019-01-05)

- [#9]: Introduce multi-container config in order to address underlying issues that prevented access to staging DB.

## v0.0.14 (2018-12-20)

- Configured app to use PostgreSQL across multiple environments.

## v0.0.13 (2018-12-16)

- Add a single selenium-based integration test to provide basis for further tests.

## v0.0.12 (2018-12-16)

- Require an email address & first/last names for login, ignoring username field; require unit tests to run and succeed before deploying.

## v0.0.11 (2018-12-14)

- Ensure the app is on the tag so that `version.txt` has a non-`dev` version number.

## v0.0.10 (2018-12-14)

- Misc fixes around version number.

## v0.0.9 (2018-12-14)

- [#1]: Add a library to proxy static files in-app, resolving issue where static files were 404 on beanstalk.
- [#2]: After the previous fix it turned out that files were not available to nginx, leading to 404 errors -- explaining the need for a volume LoL.  Also, to better determine what version is running add some logic to rebuild the image each deploy and version it.

## v0.0.8 (2018-12-14)

- Fix bug in condition check in deploy script.

## v0.0.7 (2018-12-12)

- Add test to confirm static files are configured properly.

## v0.0.6 (2018-12-12)

- Correct a bunch of misc errors with running container, document it better, and fail releases if container is not functioning correctly.

## v0.0.5 (2018-12-10)

- Organize Django project files under a subdirectory, and expose some product information to the templates so that we know what version is being displayed.

## v0.0.4 (2018-12-09)

- Run migrations before running server to collect static files and apply any db changes.

## v0.0.3 (2018-12-09)

- Pause before a deploy, and rely on defaults for release bundling.

## v0.0.2 (2018-12-09)

- Health checks are done direct to IP address, which is not in ALLOWED_HOSTS and causing the health check (and deploy) to fail.

## v0.0.1 (2018-12-09)

- Fix stray char in ALLOWED_HOSTS that caused a bad request.
- Fix typo in app name in Dockerfile.

## v0.0.0 (2018-12-08)

- Nothing changed yet.
