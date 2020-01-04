#######################################################################
### Collects static files and publishes them to the correct S3 bucket.
### Depends on the presence of AWS credentials in environment.
###
#######################################################################

CODE=./project/vue-s3-dropzone/frontend

static: clean index.html app.js app.css vendor.js manifest.js publish

clean:
	/bin/rm -rf ${CODE}/dist
	@echo [clean] SUCCESSFUL

index.html:
	cd ${CODE} && yarn install && yarn build
	@echo [index.html] SUCCESSFUL

app.js:
	cp ${CODE}/dist/static/js/app.*.js project/static/js/app.js
	/bin/rm project/static/js/app.*.js.map
	cp ${CODE}/dist/static/js/app.*.js.map project/static/js/
	@echo [app.js] SUCCESSFUL

app.css:
	cp ${CODE}/dist/static/css/app.*.css project/static/css/app.css
	/bin/rm project/static/css/app.*.css.map
	cp ${CODE}/dist/static/css/app.*.css.map project/static/css/
	@echo [app.css] SUCCESSFUL

vendor.js:
	cp ${CODE}/dist/static/js/vendor.*.js project/static/js/vendor.js
	/bin/rm project/static/js/vendor.*.js.map
	cp ${CODE}/dist/static/js/vendor.*.js.map project/static/js/
	@echo [vendor.js] SUCCESSFUL

manifest.js:
	cp ${CODE}/dist/static/js/manifest.*.js project/static/js/manifest.js
	/bin/rm project/static/js/manifest.*.js.map
	cp ${CODE}/dist/static/js/manifest.*.js.map project/static/js/
	@echo [manifest.js] SUCCESSFUL

publish:
	python project/manage.py collectstatic \
    --noinput \
    --pythonpath=project \
    --settings=elektrum.settings
	@echo [publish] SUCCESSFUL
