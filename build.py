#!/usr/bin/python3

import hashlib
import os
from pathlib import Path
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

    match len(sys.argv):
        case 1:
            build(config)
        case 2:
            if sys.argv[1] == "clean":
                clean(config)
            else:
                print(f"Unknown option '{sys.argv[1]}'")
                sys.exit(1)
        case _:
            print(f"Unknown options '{' '.join(sys.argv[1:])}'")


def build(config: dict) -> None:
    """
    Build and integrate source files and save the result as a new ROM.
    """
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

    print(
        f"Succesfully wrote '{config["output_rom"]}' ({hashlib.sha1(rom).hexdigest()})"
    )


def clean(config: dict) -> None:
    """
    Cleanup build artifacts.
    """
    # Cleanup build files
    for patch in config["patches"]:
        for item in config["clean"]:
            Path(item.replace("$FILENAME$", patch["filename"])).unlink(missing_ok=True)
    # Also remove built ROM
    Path(config["output_rom"]).unlink(missing_ok=True)
    Path(config["output_rom"].replace(".gba", ".sav")).unlink(missing_ok=True)


def compile_source_file(
    gcc_command: list[str], objcopy_command: list[str], filename: str
) -> None:
    """
    Compile a source (C) file to a raw binary file.
    """
    result = subprocess.run(
        [arg.replace("$FILENAME$", filename) for arg in gcc_command],
        capture_output=True,
        universal_newlines=True,
    )
    if result.returncode != 0:
        print(
            f"Error while running gcc:\n"
            f"args: '{result.args}'\n"
            f"stdout: '{result.stdout.rstrip()}'\n"
            f"stderr: '{result.stderr.rstrip()}'"
        )
        sys.exit(1)

    result = subprocess.run(
        [arg.replace("$FILENAME$", filename) for arg in objcopy_command],
        capture_output=True,
        universal_newlines=True,
    )
    if result.returncode != 0:
        print(
            f"Error while running objcopy:\n"
            f"args: '{result.args}'\n"
            f"stdout: '{result.stdout.rstrip()}'\n"
            f"stderr: '{result.stderr.rstrip()}'"
        )
        sys.exit(1)


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
