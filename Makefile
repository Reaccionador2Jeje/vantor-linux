SHELL := /usr/bin/env bash
.DEFAULT_GOAL := help

.PHONY: help info check check-shell check-config clean

help:
	@printf '%s\n' 'VANTOR Linux — Genesis' '' \
	  'Targets:' \
	  '  make info         Show project configuration' \
	  '  make check        Run repository validation' \
	  '  make check-shell  Validate shell scripts' \
	  '  make check-config Validate build configuration' \
	  '  make clean        Remove generated build output'

info:
	@set -a; source build/config/vantor.conf; set +a; \
	printf '%s %s (%s)\nTarget: %s\n' \
	  "$$VANTOR_NAME" "$$VANTOR_VERSION" "$$VANTOR_CODENAME" "$$VANTOR_TARGET"

check: check-config check-shell
	@echo "[OK] VANTOR repository checks passed."

check-config:
	@bash -n build/config/vantor.conf
	@set -a; source build/config/vantor.conf; set +a; \
	test "$$VANTOR_ARCH" = "x86_64"; \
	test -n "$$VANTOR_VERSION"; \
	test -n "$$VANTOR_TARGET"
	@echo "[OK] Build configuration is valid."

check-shell:
	@find build/scripts tools tests -type f -name '*.sh' -print0 | \
	  while IFS= read -r -d '' file; do bash -n "$$file"; done
	@echo "[OK] Shell syntax is valid."

clean:
	rm -rf -- build/work build/sources output
