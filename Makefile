CODE=./project/vue-s3-dropzone/frontend

all: clean build app.js app.css vendor.js manifest.js

build:
	cd ${CODE} && yarn install && yarn build

clean:
	/bin/rm -rf ${CODE}/dist
	@echo [js-clean] SUCCESSFUL

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
