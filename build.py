#!/usr/bin/python3

import hashlib
import os
import subprocess
import sys
import yaml


def main() -> None:
    """
    Build script entry point.
    """
    if not os.path.isfile("build-config.yaml"):
        print("Configuration file 'build-config.yaml' is missing.")
        sys.exit(1)

    with open("build-config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    with open(config["base_rom"], "rb") as rom_file:
        rom = bytearray(rom_file.read())

    if hashlib.sha1(rom).hexdigest() != config["base_rom_sha1"]:
        print("Provided ROM does not match the expected hash.")
        sys.exit(1)

    # Prepare gcc and objcopy options
    gcc_command = [config["gcc"]["path"], *config["gcc"]["opts"]]
    objcopy_command = [config["objcopy"]["path"], *config["objcopy"]["opts"]]

    # Build and integrate files
    for patch in config["patches"]:
        compile_source_file(gcc_command, objcopy_command, patch["filename"])
        integrate_binary_file(rom, patch["filename"], patch["address"], patch["size"])

    # Write the resulting ROM to disk
    with open(config["output_rom"], "wb") as output_file:
        output_file.write(rom)


def compile_source_file(
    gcc_command: list[str], objcopy_command: list[str], filename: str
) -> None:
    """
    Compile a source (C) file to a raw binary file.
    """
    subprocess.run(
        [arg.replace("$FILENAME$", filename) for arg in gcc_command], check=True
    )
    subprocess.run(
        [arg.replace("$FILENAME$", filename) for arg in objcopy_command], check=True
    )


def integrate_binary_file(
    rom: bytearray, filename: str, address: int, size: int
) -> None:
    """
    Integrate a raw binary file into the ROM.
    """
    # Load binary
    with open(f"{filename}.bin", "rb") as binary_file:
        binary = binary_file.read()

    # Ensure new code fits into original function range
    new_size = len(binary)
    if len(binary) > size:
        print(
            f"Binary '{filename}' is larger than original function ({len(binary)}>{size})"
        )
        sys.exit(1)

    # Copy newly built function into ROM
    rom[address : address + new_size] = binary

    # Zero remaining bytes
    rom[address + new_size : address + size] = b"\x00" * (size - new_size)


if __name__ == "__main__":
    main()
