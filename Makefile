CODE=./processor
BUILD=${CODE}/out/production

.PHONY: all clean

all: zip-all deploy-all

clean:
	/bin/rm -rf ${BUILD}
	cd ${CODE} && ./gradlew clean
	mkdir -p ${BUILD}
	@echo [all] CLEAN: SUCCESSFUL

%.zip:
	cd ${CODE} && ./gradlew -PprojVersion=$(VERSION) buildZip
	@echo [photo-processor] BUILD: SUCCESSFUL

zip-all: processor.zip

processor.zip: $(shell find $(BUILD) -name elektron-processor*.zip)

deploy-photo-processor: processor.zip
	$(shell python3 scripts/photo-processor-deploy.py ${BUILD}/archive/elektron-processor*.zip)
	@echo [photo-processor] DEPLOY: SUCCESSFUL

deploy-all: deploy-photo-processor
