CODE=./processor
BUILD=${CODE}/build
JS_CODE=./project/vue-s3-dropzone/frontend

.PHONY: all clean

js-all: js-clean js-build app.js app.css vendor.js manifest.js collectstatic

js-build:
	cd ${JS_CODE} && yarn build install

js-clean:
	/bin/rm -rf ${JS_CODE}/dist
	@echo [js-clean] SUCCESSFUL

app.js:
	cp ${JS_CODE}/dist/static/js/app.*.js project/static/js/app.js
	/bin/rm project/static/js/app.*.js.map
	cp ${JS_CODE}/dist/static/js/app.*.js.map project/static/js/
	@echo [app.js] SUCCESSFUL

app.css:
	cp ${JS_CODE}/dist/static/css/app.*.css project/static/css/app.css
	/bin/rm project/static/css/app.*.css.map
	cp ${JS_CODE}/dist/static/css/app.*.css.map project/static/css/
	@echo [app.css] SUCCESSFUL

vendor.js:
	cp ${JS_CODE}/dist/static/js/vendor.*.js project/static/js/vendor.js
	/bin/rm project/static/js/vendor.*.js.map
	cp ${JS_CODE}/dist/static/js/vendor.*.js.map project/static/js/
	@echo [vendor.js] SUCCESSFUL

manifest.js:
	cp ${JS_CODE}/dist/static/js/manifest.*.js project/static/js/manifest.js
	/bin/rm project/static/js/manifest.*.js.map
	cp ${JS_CODE}/dist/static/js/manifest.*.js.map project/static/js/
	@echo [manifest.js] SUCCESSFUL

collectstatic:
	python project/manage.py collectstatic --pythonpath=project --settings=elektron.settings --noinput
	@echo [collectstatic] SUCCESSFUL

elektron-processor%.zip:
	cd ${CODE} && ./gradlew -PprojVersion=$(VERSION) buildZip
	@echo [photo-processor] BUILD: SUCCESSFUL

processor.zip: elektron-processor%.zip

clean:
	/bin/rm -rf ${BUILD}
	mkdir -p ${BUILD}
	@echo [all] CLEAN: SUCCESSFUL

all: clean processor.zip
