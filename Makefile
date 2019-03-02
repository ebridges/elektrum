CODE=./processor
BUILD=${CODE}/out/production

.PHONY: all clean

all: zip-all deploy-all

clean:
	/bin/rm -rf ${BUILD}
	cd ${CODE} && ./gradlew clean
	mkdir -p ${BUILD}
	@echo [all] CLEAN: SUCCESSFUL

${BUILD}/archive/photo-processor.zip:
	cd ${CODE} && ./gradlew build
	@echo [photo-processor] BUILD: SUCCESSFUL

zip-all: ${BUILD}/archive/photo-processor.zip

deploy-photo-processor: ${BUILD}/archive/photo-processor.zip
	$(shell python3 etc/photo-processor-deploy.py ${BUILD}/archive/photo-processor.zip)
	@echo [photo-processor] DEPLOY: SUCCESSFUL

deploy-all: deploy-photo-processor
