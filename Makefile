SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help info check desktop-files check-shell check-config check-sources check-python check-nyan sources-ready fetch-sources toolchain kernel kernel-legacy busybox busybox-legacy initramfs initramfs-legacy rootfs rootfs-legacy boot-files iso iso-legacy image-legacy clean kernel-files initramfs-files

help:
	@printf '%s\n' 'VANTOR Linux — Genesis' '' \
	  'Targets:' '  make info          Show project configuration' \
	  '  make check         Run all repository checks and tests' '  make desktop-files Validate VANTOR Desktop Genesis files' \
	  '  make check-shell   Validate shell scripts' '  make check-config  Validate build configuration' \
	  '  make check-sources Validate source manifest structure' '  make check-python  Compile and test Python tools' '  make check-nyan    Validate Nyan package manager syntax' \
	  '  make sources-ready Require verified source checksums' '  make fetch-sources Download and verify pinned archives' \
	  '  make toolchain      Build Binutils and GCC pass 1' '  make kernel         Build VANTOR x86_64 Linux kernel' '  make kernel-legacy  Build 486SX-compatible 32-bit legacy kernel' \
	  '  make busybox        Build static x86_64 BusyBox userspace' '  make busybox-legacy Build static i486 BusyBox userspace' '  make initramfs      Assemble x86_64 early userspace' '  make initramfs-legacy Assemble i486 early userspace' \
	  '  make rootfs         Assemble the x86_64 VANTOR rootfs skeleton' '  make rootfs-legacy  Assemble the i486 VANTOR rootfs skeleton' \
	  '  make boot-files     Check bootloader configuration and builder' \
	  '  make iso            Build the x86_64 GRUB ISO' '  make iso-legacy     Build the 486 BIOS GRUB ISO' '  make image-legacy   Build the complete i486 ISO pipeline' \
	  '  make clean         Remove generated build output'

info:
	@set -a; source build/config/vantor.conf; set +a; \
	printf '%s %s (%s)\nTarget: %s\nKernel: Linux %s (%s)\n' \
	  "$$VANTOR_NAME" "$$VANTOR_VERSION" "$$VANTOR_CODENAME" "$$VANTOR_TARGET" "$$VANTOR_KERNEL_VERSION" "$$VANTOR_KERNEL_ARCH"

check: check-config check-shell check-sources check-python check-nyan desktop-files core-files kernel-files initramfs-files boot-files
	@python3 -m json.tool assets/branding/theme.json > /dev/null
	@echo "[OK] VANTOR repository checks passed."

desktop-files:
	@test -x desktop/bin/vantor-session
	@test -s desktop/openbox/rc.xml
	@test -s desktop/openbox/menu.xml
	@test -s desktop/tint2/tint2rc
	@test -s desktop/themes/VANTOR/openbox-3/themerc
	@test -s desktop/README.md
	@test -s desktop/xsessions/vantor.desktop
	@test -s tests/test_desktop.py
	@sh -n desktop/bin/vantor-session
	@echo "[OK] VANTOR Desktop Genesis files are present."

check-config:
	@bash -n build/config/vantor.conf
	@set -a; source build/config/vantor.conf; set +a; \
	test "$$VANTOR_ARCH" = "x86_64"; test -n "$$VANTOR_VERSION"; test -n "$$VANTOR_TARGET"; \
	test "$$VANTOR_KERNEL_VERSION" = "6.18.65"; test "$$VANTOR_LEGACY_KERNEL_VERSION" = "6.1.193"; test "$$VANTOR_LEGACY_KERNEL_ARCH" = "i386"
	@echo "[OK] Build configuration is valid."

check-shell:
	@find build/scripts tools tests -type f -name '*.sh' -exec bash -n {} +
	@sh -n installer/vantor-install
	@echo "[OK] Shell syntax is valid."

check-sources:
	@python3 tools/validate-sources.py

check-python:
	@python3 -m compileall -q tools tests
	@python3 -m unittest discover -s tests -p 'test_*.py' -v

core-files:
	@test -s docs/vantor-core.md
	@test -s installer/vantor-install
	@test -s docs/installer.md
	@test -s .github/workflows/build-nyan-minimal.yml
	@test -s .github/workflows/build-legacy-minimal.yml
	@test -s .github/workflows/build-legacy-image.yml
	@test -s packages/repository/i486/Packages
	@test -s packages/profiles/minimal/PROFILE.txt
	@grep -q 'root:x:0:0:root' tools/prepare-rootfs.py
	@grep -q 'live:x:1000:1000' tools/prepare-rootfs.py
	@grep -q 'VANTOR Init' tools/prepare-rootfs.py
	@grep -q 'VANTOR Control' tools/prepare-rootfs.py
	@grep -q 'etc/inittab' tools/prepare-rootfs.py
	@grep -q 'vantor-live-session' tools/prepare-rootfs.py
	@grep -q 'udhcpc' tools/prepare-rootfs.py
	@test -s core/hardware/vantor-hw
	@test -s core/boot/vantor-fb-splash.c
	@grep -q 'VANTOR Hardware' core/hardware/vantor-hw
	@sh -n core/hardware/vantor-hw
	@echo "[OK] VANTOR Core bootstrap components are present."

kernel-files:
	@test -s build/scripts/build-kernel.sh
	@test -s kernel/configs/README.md
	@test -s docs/kernel.md
	@test -s build/scripts/build-kernel-legacy.sh
	@test -s build/scripts/build-busybox-legacy.sh
	@grep -q 'i486' build/scripts/build-busybox-legacy.sh
	@grep -q 'M486SX' build/scripts/build-kernel-legacy.sh
	@grep -q 'linux-legacy' build/sources/sources.json
	@test -s docs/hardware-compatibility.md
	@echo "[OK] VANTOR x86_64 and i486 kernel build files are present."


check-nyan:
	@sh -n packages/nyan/nyan
	@grep -q 'VANTOR-PACKAGES 1' packages/repository/x86_64/Packages
	@grep -q 'VANTOR-PACKAGES 1' packages/repository/i486/Packages
	@grep -q 'languages)' packages/nyan/nyan
	@grep -q 'install-profile)' packages/nyan/nyan
	@grep -q 'dependency cycle detected' packages/nyan/nyan
	@grep -q 'install-profile' packages/nyan/nyan
	@grep -q 'minimal' packages/nyan/nyan
	@grep -q 'catalog)' packages/nyan/nyan
	@test -s packages/catalog.tsv
	@test -s packages/profiles/development/PROFILE.txt
	@test -s .github/workflows/build-nyan-profiles.yml
	@test -s .github/workflows/build-nyan-minimal.yml
	@bash -n tools/publish-package.sh
	@grep -q 'dependency-first installation' docs/nyan.md
	@grep -q 'Lua 5.4.9' docs/nyan.md
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

kernel-legacy:
	@bash build/scripts/build-kernel-legacy.sh

busybox:
	@bash build/scripts/build-busybox.sh

busybox-legacy:
	@bash build/scripts/build-busybox-legacy.sh

initramfs:
	@bash build/scripts/build-initramfs.sh

initramfs-legacy: rootfs-legacy busybox-legacy
	@VANTOR_ROOTFS_DIR=build/work/rootfs-legacy VANTOR_INITRAMFS_DIR=build/work/initramfs-legacy VANTOR_INITRAMFS_NAME=vantor-legacy-initramfs.cpio.gz bash build/scripts/build-initramfs.sh

initramfs-files:
	@test -s build/scripts/build-busybox.sh
	@test -s build/scripts/build-initramfs.sh
	@test -s docs/initramfs.md
	@test -s tests/test_initramfs_build.py
	@test -s build/scripts/build-iso-legacy.sh
	@test -s boot/grub/grub-legacy.cfg
	@echo "[OK] BusyBox and initramfs build files are present."

rootfs:
	@python3 tools/prepare-rootfs.py --output build/work/rootfs --arch x86_64

rootfs-legacy:
	@python3 tools/prepare-rootfs.py --output build/work/rootfs-legacy --arch i486

boot-files:
	@test -s boot/grub/grub.cfg
	@test -s boot/grub/grub-legacy.cfg
	@test -s build/scripts/build-iso.sh
	@test -s build/scripts/build-iso-legacy.sh
	@echo "[OK] GRUB configuration and ISO builder are present."

iso:
	@bash build/scripts/build-iso.sh

iso-legacy: kernel-legacy initramfs-legacy
	@bash build/scripts/build-iso-legacy.sh

image-legacy: iso-legacy

clean:
	rm -rf -- build/work build/distfiles output
