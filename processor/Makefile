VERSION := $(shell cat ../version.txt)
BUILD=./build

.PHONY: all clean

elektrum-processor%.zip:
	./gradlew -PprojVersion=$(VERSION) buildZip
	@echo [photo-processor] BUILD: SUCCESSFUL

processor.zip: elektrum-processor%.zip

clean:
	/bin/rm -rf ${BUILD}
	mkdir -p ${BUILD}
	@echo [all] CLEAN: SUCCESSFUL

all: clean processor.zip
