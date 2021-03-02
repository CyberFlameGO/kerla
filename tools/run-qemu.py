#!/usr/bin/env python3
#
#
import argparse
import shutil
from tempfile import NamedTemporaryFile
import os
import subprocess
import sys

COMMON_ARGS = [
    "-serial", "mon:stdio", "-no-reboot",
]

ARCHS = {
    "x64":  {
        "bin": "qemu-system-x86_64",
        "args": COMMON_ARGS + [
            "-m", "512",
            "-cpu", "Icelake-Server",
            "-device", "isa-debug-exit,iobase=0x501,iosize=2",
            "-d", "guest_errors,unimp",
        ]
    }
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", choices=["x64"])
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("kernel_elf", help="The kernel ELF executable.")
    args = parser.parse_args()

    if args.arch == "x64":
        #  Because QEMU denies a x86_64 multiboot ELF file (GRUB2 accept it, btw),
        #  modify `em_machine` to pretend to be an x86 (32-bit) ELF image,
        #
        #  https://github.com/qemu/qemu/blob/950c4e6c94b15cd0d8b63891dddd7a8dbf458e6a/hw/i386/multiboot.c#L197
        # Set EM_386 (0x0003) to em_machine.
        elf = NamedTemporaryFile()
        shutil.copyfileobj(open(args.kernel_elf, "rb"), elf.file)
        elf.seek(18)
        elf.write(bytes([0x03, 0x00]))
        elf.flush()
        kernel_elf = elf.name
    else:
        kernel_elf = args.kernel_elf

    qemu = ARCHS[args.arch]
    argv = [qemu["bin"]] + qemu["args"] + ["-kernel", kernel_elf]
    if not args.gui:
        argv += ["-nographic"]

    p = subprocess.run(argv, preexec_fn=os.setsid)
    if p.returncode != 33:
        sys.exit(f"\nrun-qemu.py: qemu exited with failue status (status={p.returncode})")

if __name__ == "__main__":
    main()