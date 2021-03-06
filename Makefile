CC := g++
CFLAGS := -Wall -pedantic -Os
JS_ERRNO := src/js_errno.cc
JS_SOURCE := $(shell git ls-files js/)
PRECOMPILE := scripts/precompile
SRCFILES := $(shell git ls-files src/)
TESTFILES := $(shell git ls-files tests/)
TARGET := build/out/Default/e
OPT_TARGET := build/out/Default/opt
TEST_TARGET := build/out/Default/test
TEMPLATES := $(shell echo scripts/templates/*.html)
BUNDLED_JS = src/.bundled_core
REAL_BUNDLED_JS = src/bundled_core.cc src/bundled_core.h
KEYCODE_FILES = src/keycode.cc src/keycode.h

all: docs/jsdoc.html

clean:
	rm -rf build/out/ build/src/ docs/
	rm -f $(BUNDLED_JS) $(REAL_BUNDLED_JS) scripts/precompile
	rm -f $(KEYCODE_FILES)
	rm -f e opt test

docs:
	@mkdir -p docs

docs/jsdoc.html: scripts/gen_js_docs.py e docs
	@echo -n "Updating $@..."
	@python scripts/gen_js_docs.py -o $@ $(SRCFILES) $(KEYCODE_FILES)
	@echo " done!"

$(PRECOMPILE): $(PRECOMPILE).cc
	$(CC) $(CFLAGS) -lv8 $< -o $@
	@strip -s $@

$(BUNDLED_JS): scripts/gen_bundled_core.py scripts/precompile $(JS_SOURCE)
	python $< js/core.js

$(KEYCODE_FILES): scripts/gen_key_sources.py third_party/Caps
	python $^

$(JS_ERRNO): scripts/gen_js_errno.py
	python $^ > $@

build:
	./configure

lint:
	python third_party/cpplint.py $(SRCFILES)

$(TARGET): $(SRCFILES) $(KEYCODE_FILES) $(JS_ERRNO) build
	make -C build e

$(OPT_TARGET): $(SRCFILES) $(BUNDLED_JS) $(KEYCODE_FILES) $(JS_ERRNO) build
	make -C build opt

$(TEST_TARGET): $(SRCFILES) $(TESTFILES) $(KEYCODE_FILES) $(JS_ERRNO) build
	make -C build test

test: $(TEST_TARGET)

e: $(TARGET)
	@if [ ! -e "$@" ]; then echo -n "Creating ./$@ symlink..."; ln -sf $(TARGET) $@; echo " done!"; fi

opt: $(OPT_TARGET)
	@strip -s $(OPT_TARGET)
	@if [ ! -e "$@" ]; then echo -n "Creating ./$@ symlink..."; ln -sf $(OPT_TARGET) $@; echo " done!"; fi

test: $(TEST_TARGET)
	@if [ ! -e "$@" ]; then echo -n "Creating ./$@ symlink..."; ln -sf $(TEST_TARGET) $@; echo " done!"; fi

.PHONY: all clean lint test
