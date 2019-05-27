CODE=./processor
BUILD=${CODE}/build

.PHONY: all clean

elektron-processor%.zip:
	cd ${CODE} && ./gradlew -PprojVersion=$(VERSION) buildZip
	@echo [photo-processor] BUILD: SUCCESSFUL

processor.zip: elektron-processor%.zip

clean:
	/bin/rm -rf ${BUILD}
	mkdir -p ${BUILD}
	@echo [all] CLEAN: SUCCESSFUL

all: clean processor.zip
