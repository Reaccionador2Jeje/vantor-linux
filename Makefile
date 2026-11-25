SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help info check check-shell check-config check-sources sources-ready fetch-sources toolchain clean

help:
	@printf '%s\n' 'VANTOR Linux — Genesis' '' \
	  'Targets:' \
	  '  make info          Show project configuration' \
	  '  make check         Run repository validation' \
	  '  make check-shell   Validate shell scripts' \
	  '  make check-config  Validate build configuration' \
	  '  make check-sources Validate source manifest structure' \
	  '  make sources-ready Require verified source checksums' \
	  '  make fetch-sources Download and verify pinned archives' \
	  '  make clean         Remove generated build output'

info:
	@set -a; source build/config/vantor.conf; set +a; \
	printf '%s %s (%s)\nTarget: %s\n' \
	  "$$VANTOR_NAME" "$$VANTOR_VERSION" "$$VANTOR_CODENAME" "$$VANTOR_TARGET"

check: check-config check-shell check-sources
	@echo "[OK] VANTOR repository checks passed."

check-config:
	@bash -n build/config/vantor.conf
	@set -a; source build/config/vantor.conf; set +a; \
	test "$$VANTOR_ARCH" = "x86_64"; \
	test -n "$$VANTOR_VERSION"; \
	test -n "$$VANTOR_TARGET"
	@echo "[OK] Build configuration is valid."

check-shell:
	@find build/scripts tools tests -type f -name '*.sh' -exec bash -n {} +
	@echo "[OK] Shell syntax is valid."

check-sources:
	@python3 tools/validate-sources.py

sources-ready:
	@python3 tools/validate-sources.py --require-pinned

fetch-sources: sources-ready
	@python3 tools/fetch-sources.py

toolchain:
	@bash build/scripts/build-toolchain.sh

clean:
	rm -rf -- build/work build/distfiles output
