"""Command-line interface for the LEAF benchmark tool."""

import argparse
import platform
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import leaf
from leaf.core.config import load_config, validate_config_file
from leaf.core.exceptions import ConfigError
from leaf.core.logging import get_logger, setup_logging


def get_compiler_info(binary_name: str) -> str | None:
    """Check if a binary exists and attempt to query its version."""
    path = shutil.which(binary_name)
    if not path:
        return None
    try:
        res = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
        first_line = (res.stdout or res.stderr).splitlines()
        return first_line[0].strip() if first_line else path
    except (subprocess.SubprocessError, OSError):
        return path


def cmd_info(args: argparse.Namespace) -> int:
    """Display environment details, detected runtimes, compilers, and hardware meters."""
    logger = get_logger("cli")
    logger.info("Gathering environment information...")

    print("=" * 60)
    print(f"LEAF Benchmark Framework v{leaf.__version__}")
    print("=" * 60)
    print(f"OS / Platform     : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Runtime    : {platform.python_implementation()} {platform.python_version()}")
    print(f"Python Executable : {sys.executable}")

    # Toolchains
    print("\nDetected Toolchains:")
    gpp = get_compiler_info("g++")
    print(f"  C++ (g++)       : {gpp if gpp else 'Not found'}")

    java_path = shutil.which("java")
    javac_path = shutil.which("javac")
    if java_path and javac_path:
        try:
            j_res = subprocess.run(
                [javac_path, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=3,
            )
            j_ver = (j_res.stdout or j_res.stderr).strip()
            print(f"  Java (javac)    : {j_ver}")
        except (subprocess.SubprocessError, OSError):
            print(f"  Java (javac)    : Found at {javac_path}")
    else:
        print("  Java (javac)    : Not found")

    # Containers
    docker_path = shutil.which("docker")
    podman_path = shutil.which("podman")
    print("\nContainer Runtimes:")
    print(f"  Docker          : {docker_path if docker_path else 'Not found'}")
    print(f"  Podman          : {podman_path if podman_path else 'Not found'}")

    # GPU
    nvidia_smi = shutil.which("nvidia-smi")
    print("\nHardware Telemetry:")
    if nvidia_smi:
        try:
            gpu_res = subprocess.run(
                [
                    nvidia_smi,
                    "--query-gpu=gpu_name,driver_version,power.draw",
                    "--format=csv,noheader",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=3,
            )
            gpu_info = gpu_res.stdout.strip()
            print(f"  NVIDIA GPU      : {gpu_info if gpu_info else 'Available'}")
        except (subprocess.SubprocessError, OSError):
            print("  NVIDIA GPU      : Available (nvidia-smi found)")
    else:
        print("  NVIDIA GPU      : Not found")
    print("=" * 60)
    return 0


def cmd_validate_config(args: argparse.Namespace) -> int:
    """Validate a given YAML configuration file."""
    config_path = Path(args.config)
    logger = get_logger("cli")
    logger.info("Validating configuration file: %s", config_path)

    is_valid, errors = validate_config_file(config_path)
    if not is_valid:
        print(f"ERROR: Configuration validation failed for '{config_path}':", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    try:
        cfg = load_config(config_path)
        print(f"SUCCESS: Configuration '{config_path}' is valid.")
        print(f"  - Experiment Name      : {cfg.experiment.name}")
        print(f"  - Dry-run Mode         : {cfg.experiment.dry_run}")
        print(f"  - Allow Cloud Calls    : {cfg.experiment.allow_cloud_calls}")
        print(f"  - Sandbox Mode         : {cfg.sandbox.mode}")
        print(f"  - Supported Languages  : {', '.join(cfg.supported_languages)}")
        return 0
    except ConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="leaf",
        description="LEAF: Low Energy AI Framework & Benchmark",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"leaf {leaf.__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging output.",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # subcommand: info
    parser_info = subparsers.add_parser(
        "info",
        help="Display detected environment, toolchains, and hardware meters.",
    )
    parser_info.set_defaults(func=cmd_info)

    # subcommand: validate-config
    parser_val = subparsers.add_parser(
        "validate-config",
        help="Validate a benchmark YAML configuration file.",
    )
    parser_val.add_argument(
        "config",
        nargs="?",
        default="config/default_config.yaml",
        help="Path to configuration file (default: config/default_config.yaml)",
    )
    parser_val.set_defaults(func=cmd_validate_config)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI execution entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    log_level = "DEBUG" if getattr(args, "verbose", False) else "INFO"
    setup_logging(level=log_level)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
