SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help info check check-shell check-config check-sources check-python check-nyan sources-ready fetch-sources toolchain kernel busybox initramfs rootfs boot-files iso clean kernel-files initramfs-files

help:
	@printf '%s\n' 'VANTOR Linux — Genesis' '' \
	  'Targets:' '  make info          Show project configuration' \
	  '  make check         Run all repository checks and tests' \
	  '  make check-shell   Validate shell scripts' '  make check-config  Validate build configuration' \
	  '  make check-sources Validate source manifest structure' '  make check-python  Compile and test Python tools' '  make check-nyan    Validate Nyan package manager syntax' \
	  '  make sources-ready Require verified source checksums' '  make fetch-sources Download and verify pinned archives' \
	  '  make toolchain      Build Binutils and GCC pass 1' '  make kernel         Build VANTOR x86_64 Linux kernel' \
	  '  make busybox        Build static BusyBox userspace' '  make initramfs      Assemble VANTOR early userspace' \
	  '  make rootfs         Assemble the VANTOR rootfs skeleton' \
	  '  make boot-files     Check bootloader configuration and builder' \
	  '  make iso            Build a GRUB ISO after kernel and initramfs exist' \
	  '  make clean         Remove generated build output'

info:
	@set -a; source build/config/vantor.conf; set +a; \
	printf '%s %s (%s)\nTarget: %s\nKernel: Linux %s (%s)\n' \
	  "$$VANTOR_NAME" "$$VANTOR_VERSION" "$$VANTOR_CODENAME" "$$VANTOR_TARGET" "$$VANTOR_KERNEL_VERSION" "$$VANTOR_KERNEL_ARCH"

check: check-config check-shell check-sources check-python check-nyan core-files kernel-files initramfs-files boot-files
	@python3 -m json.tool assets/branding/theme.json > /dev/null
	@echo "[OK] VANTOR repository checks passed."

check-config:
	@bash -n build/config/vantor.conf
	@set -a; source build/config/vantor.conf; set +a; \
	test "$$VANTOR_ARCH" = "x86_64"; test -n "$$VANTOR_VERSION"; test -n "$$VANTOR_TARGET"; \
	test "$$VANTOR_KERNEL_VERSION" = "6.18.65"
	@echo "[OK] Build configuration is valid."

check-shell:
	@find build/scripts tools tests -type f -name '*.sh' -exec bash -n {} +
	@echo "[OK] Shell syntax is valid."

check-sources:
	@python3 tools/validate-sources.py

check-python:
	@python3 -m compileall -q tools tests
	@python3 -m unittest discover -s tests -p 'test_*.py' -v

core-files:
	@test -s docs/vantor-core.md
	@grep -q 'VANTOR Init' tools/prepare-rootfs.py
	@grep -q 'VANTOR Control' tools/prepare-rootfs.py
	@test -s core/hardware/vantor-hw
	@grep -q 'VANTOR Hardware' core/hardware/vantor-hw
	@sh -n core/hardware/vantor-hw
	@echo "[OK] VANTOR Core bootstrap components are present."

kernel-files:
	@test -s build/scripts/build-kernel.sh
	@test -s kernel/configs/README.md
	@test -s docs/kernel.md
	@echo "[OK] VANTOR kernel build files are present."


check-nyan:
	@sh -n packages/nyan/nyan
	@grep -q 'VANTOR-PACKAGES 1' packages/repository/x86_64/Packages
	@grep -q 'languages)' packages/nyan/nyan
	@grep -q 'Language:' docs/nyan.md
	@test -s tests/test_nyan.py
	@grep -Fq 'archive-types-$$' packages/nyan/nyan
	@grep -q 'refusing to overwrite existing system path' packages/nyan/nyan
	@echo "[OK] Nyan client and repository index are valid."

sources-ready:
	@python3 tools/validate-sources.py --require-pinned

fetch-sources: sources-ready
	@python3 tools/fetch-sources.py

toolchain:
	@bash build/scripts/build-toolchain.sh

kernel:
	@bash build/scripts/build-kernel.sh

busybox:
	@bash build/scripts/build-busybox.sh

initramfs:
	@bash build/scripts/build-initramfs.sh

initramfs-files:
	@test -s build/scripts/build-busybox.sh
	@test -s build/scripts/build-initramfs.sh
	@test -s docs/initramfs.md
	@test -s tests/test_initramfs_build.py
	@echo "[OK] BusyBox and initramfs build files are present."

rootfs:
	@python3 tools/prepare-rootfs.py --output build/work/rootfs

boot-files:
	@test -s boot/grub/grub.cfg
	@test -s build/scripts/build-iso.sh
	@echo "[OK] GRUB configuration and ISO builder are present."

iso:
	@bash build/scripts/build-iso.sh

clean:
	rm -rf -- build/work build/distfiles output
