VENV ?= venv
ifeq ($(OS),Windows_NT)
DEFAULT_PYTHON := $(VENV)/Scripts/python.exe
else
DEFAULT_PYTHON := $(VENV)/bin/python
endif
PYTHON ?= $(DEFAULT_PYTHON)
BOOTSTRAP_PYTHON ?= python
HOST = $(shell ifconfig | grep "inet " | tail -1 | cut -d\  -f2)
TAG = v$(shell grep -E '__version__ = ".*"' pyrogram/__init__.py | cut -d\" -f2)

RM := rm -rf

.PHONY: venv clean-build clean-api clean api build tag dtag clean-docs docs docs-live

all: clean venv build
	echo Done

venv:
	$(RM) $(VENV)
	$(BOOTSTRAP_PYTHON) -m venv $(VENV)
	$(PYTHON) -m pip install -U pip wheel setuptools
	$(PYTHON) -m pip install -U -e .[docs]
	@echo "Created venv with $$($(PYTHON) --version)"

clean-build:
	$(RM) *.egg-info build dist

clean-docs:
	$(RM) docs/build
	$(RM) docs/build docs/source/api/bound-methods docs/source/api/methods docs/source/api/types docs/source/api/enums docs/source/telegram

clean-api:
	$(RM) pyrogram/errors/exceptions pyrogram/raw/all.py pyrogram/raw/base pyrogram/raw/functions pyrogram/raw/types

clean:
	make clean-build
	make clean-api

api:
	cd compiler/api && ../../$(PYTHON) compiler.py
	cd compiler/errors && ../../$(PYTHON) compiler.py

docs-live:
	$(MAKE) -C docs api
	$(PYTHON) -m sphinx_autobuild \
		--watch pyrogram --watch docs/resources \
		-b html "docs/source" "docs/build/html" -j auto

docs:
	$(MAKE) -C docs api
	$(PYTHON) -m sphinx \
		-b dirhtml "docs/source" "docs/build" -j auto

build: clean api docs
	echo Build

tag:
	git tag $(TAG)
	git push origin $(TAG)

dtag:
	git tag -d $(TAG)
	git push origin -d $(TAG)
