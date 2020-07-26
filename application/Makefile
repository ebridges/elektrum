#######################################################################
### Collects static files and publishes them to the correct S3 bucket.
### Depends on the presence of AWS credentials in environment.
###
#######################################################################

APPLICATION_DIR=.
DZ_CODE=${APPLICATION_DIR}/js/vue-s3-dropzone/frontend
JSLI_CODE=${APPLICATION_DIR}/js/javascript-load-image

static: clean index.html load-image.all.min.js app.js app.css vendor.js manifest.js publish

clean:
	/bin/rm -rf ${DZ_CODE}/dist
	@echo [clean] SUCCESSFUL

load-image.all.min.js:
	cp ${JSLI_CODE}/js/load-image.all.min.js ${APPLICATION_DIR}/static/js/load-image.all.min.js
	cp ${JSLI_CODE}/js/load-image.all.min.js.map ${APPLICATION_DIR}/static/js/load-image.all.min.js.map
	# add a trailing newline to fix lint check done by pre-commit-config
	echo >> ${APPLICATION_DIR}/static/js/load-image.all.min.js
	echo >> ${APPLICATION_DIR}/static/js/load-image.all.min.js.map
	@echo [load-image.all.min.js] SUCCESSFUL

index.html:
	cd ${DZ_CODE} && yarn install && yarn build
	@echo [index.html] SUCCESSFUL

app.js:
	cp ${DZ_CODE}/dist/static/js/app.js ${APPLICATION_DIR}/static/js/app.js
	/bin/rm ${APPLICATION_DIR}/static/js/app.js.map
	cp ${DZ_CODE}/dist/static/js/app.js.map ${APPLICATION_DIR}/static/js/
	# add a trailing newline to fix lint check done by pre-commit-config
	echo >> ${APPLICATION_DIR}/static/js/app.js
	echo >> ${APPLICATION_DIR}/static/js/app.js.map
	@echo [app.js] SUCCESSFUL

app.css:
	cp ${DZ_CODE}/dist/static/css/app.css ${APPLICATION_DIR}/static/css/app.css
	/bin/rm ${APPLICATION_DIR}/static/css/app.css.map
	cp ${DZ_CODE}/dist/static/css/app.css.map ${APPLICATION_DIR}/static/css/
	# add a trailing newline to fix lint check done by pre-commit-config
	echo >> ${APPLICATION_DIR}/static/css/app.css
	echo >> ${APPLICATION_DIR}/static/css/app.css.map
	@echo [app.css] SUCCESSFUL

vendor.js:
	cp ${DZ_CODE}/dist/static/js/vendor.js ${APPLICATION_DIR}/static/js/vendor.js
	/bin/rm ${APPLICATION_DIR}/static/js/vendor.js.map
	cp ${DZ_CODE}/dist/static/js/vendor.js.map ${APPLICATION_DIR}/static/js/
	# add a trailing newline to fix lint check done by pre-commit-config
	echo >> ${APPLICATION_DIR}/static/js/vendor.js
	echo >> ${APPLICATION_DIR}/static/js/vendor.js.map
	@echo [vendor.js] SUCCESSFUL

manifest.js:
	cp ${DZ_CODE}/dist/static/js/manifest.js ${APPLICATION_DIR}/static/js/manifest.js
	/bin/rm ${APPLICATION_DIR}/static/js/manifest.js.map
	cp ${DZ_CODE}/dist/static/js/manifest.js.map ${APPLICATION_DIR}/static/js/
	# add a trailing newline to fix lint check done by pre-commit-config
	echo >> ${APPLICATION_DIR}/static/js/manifest.js
	echo >> ${APPLICATION_DIR}/static/js/manifest.js.map
	@echo [manifest.js] SUCCESSFUL

publish:
	python ${APPLICATION_DIR}/manage.py collectstatic \
        --noinput \
        --pythonpath=${APPLICATION_DIR} \
        --settings=elektrum.settings
	@echo [publish] SUCCESSFUL

commit:

# if there are changes, then commit them
	@delta=$(git diff-index --quiet HEAD -- ${APPLICATION_DIR}/static)
	@if [ -z "$$delta" ]; then \
		echo '[commit] No files need committing.' ; \
	else \
		git add ${APPLICATION_DIR}/static/css/app* \
						${APPLICATION_DIR}/static/js/app* \
						${APPLICATION_DIR}/static/js/manifest* \
						${APPLICATION_DIR}/static/js/vendor* \
						${APPLICATION_DIR}/static/js/load-image* && \
		git commit --gpg-sign --message 'Static assets generated.' \
		echo '[commit] SUCCESSFUL' ; \
	fi

	@echo COMPLETED SUCCESSFULLY
