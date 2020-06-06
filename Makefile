#######################################################################
### Collects static files and publishes them to the correct S3 bucket.
### Depends on the presence of AWS credentials in environment.
###
#######################################################################

DZ_CODE=./project/js/vue-s3-dropzone/frontend
JSLI_CODE=./project/js/javascript-load-image

static: clean index.html load-image.all.min.js app.js app.css vendor.js manifest.js publish commit

clean:
	/bin/rm -rf ${DZ_CODE}/dist
	@echo [clean] SUCCESSFUL

load-image.all.min.js:
	cp ${JSLI_CODE}/js/load-image.all.min.js project/static/js/load-image.all.min.js
	cp ${JSLI_CODE}/js/load-image.all.min.js.map project/static/js/load-image.all.min.js.map
	@echo [load-image.all.min.js] SUCCESSFUL

index.html:
	cd ${DZ_CODE} && yarn install && yarn build
	@echo [index.html] SUCCESSFUL

app.js:
	cp ${DZ_CODE}/dist/static/js/app.*.js project/static/js/app.js
	/bin/rm project/static/js/app.*.js.map
	cp ${DZ_CODE}/dist/static/js/app.*.js.map project/static/js/
	@echo [app.js] SUCCESSFUL

app.css:
	cp ${DZ_CODE}/dist/static/css/app.*.css project/static/css/app.css
	/bin/rm project/static/css/app.*.css.map
	cp ${DZ_CODE}/dist/static/css/app.*.css.map project/static/css/
	@echo [app.css] SUCCESSFUL

vendor.js:
	cp ${DZ_CODE}/dist/static/js/vendor.*.js project/static/js/vendor.js
	/bin/rm project/static/js/vendor.*.js.map
	cp ${DZ_CODE}/dist/static/js/vendor.*.js.map project/static/js/
	@echo [vendor.js] SUCCESSFUL

manifest.js:
	cp ${DZ_CODE}/dist/static/js/manifest.*.js project/static/js/manifest.js
	/bin/rm project/static/js/manifest.*.js.map
	cp ${DZ_CODE}/dist/static/js/manifest.*.js.map project/static/js/
	@echo [manifest.js] SUCCESSFUL

publish:
	python project/manage.py collectstatic \
        --noinput \
        --pythonpath=project \
        --settings=elektrum.settings
	@echo [publish] SUCCESSFUL

commit:
# add a newline to all files to fix lint check done by pre-commit-config
	@for file in project/static/css/app* project/static/js/app* project/static/js/manifest* project/static/js/vendor* project/static/js/load-image* ; do \
		echo >> $${file} ; \
	done

# if there are changes, then commit them
	@delta=$(git diff-index --quiet HEAD -- project/static)
	@if [ -z "$$delta" ]; then \
		echo '[commit] No files need committing.' ; \
	else \
		git add project/static/css/app* \
						project/static/js/app* \
						project/static/js/manifest* \
						project/static/js/vendor* \
						project/static/js/load-image* && \
		git commit --gpg-sign --message 'Static assets generated.' \
		echo '[commit] SUCCESSFUL' ; \
	fi

	@echo COMPLETED SUCCESSFULLY
