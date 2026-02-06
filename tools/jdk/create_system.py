import argparse
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import typing
import zipfile


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Extract resources from .jar")
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    parser.add_argument("--java_home", required=True, type=pathlib.Path)
    parser.add_argument("--module_info", required=True)
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    args = parse_args(argv)

    exe_extension = ".exe" if platform.system() == "Windows" else ""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)

        classes_dir = temp_path / "classes"
        jmod_dir = temp_path / "jmod"
        classes_dir.mkdir(parents=True, exist_ok=True)
        jmod_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(args.input, "r") as zip_input:
            zip_input.extractall(classes_dir)

        shutil.rmtree(args.output)

        javac_command = [
            str(args.java_home / "bin" / f"javac{exe_extension}"),
            "-d", str(classes_dir),
            "--system=none",
            f"--patch-module=java.base={classes_dir}",
            args.module_info,
        ]
        subprocess.run(javac_command, check=True)

        release_contents = (args.java_home / "release").read_text()
        implementor_match = re.search(r'IMPLEMENTOR="(.*)"', release_contents)
        if not implementor_match:
            raise ValueError(f"Failed to file IMPLEMENTOR in {release_contents}")
        implementor = implementor_match.group(1)
        java_runtime_version_match = re.search(r'JAVA_RUNTIME_VERSION="(.*)"', release_contents)
        if not java_runtime_version_match:
            raise ValueError(f"Failed to file JAVA_RUNTIME_VERSION in {release_contents}")
        java_runtime_version = java_runtime_version_match.group(1)
        java_version_date_match = re.search(r'JAVA_VERSION_DATE="(.*)"', release_contents)
        if not java_version_date_match:
            raise ValueError(f"Failed to file JAVA_VERSION_DATE in {release_contents}")
        java_version_date = java_version_date_match.group(1)

        resource_dir = classes_dir / "jdk" / "internal" / "misc" / "resources"
        resource_dir.mkdir(parents=True, exist_ok=True)
        (resource_dir / "release.txt").write_text(f"{implementor}-{java_runtime_version}-{java_version_date}")

        jlink_exe = str(args.java_home / "bin" / f"jlink{exe_extension}")
        jlink_version_result = subprocess.run([jlink_exe, "--version"], stdout=subprocess.PIPE, check=True)
        jlink_version = jlink_version_result.stdout.decode().strip()

        jmod_command = [
            str(args.java_home / "bin" / f"jmod{exe_extension}"), "create",
            "--module-version", jlink_version,
            "--target-platform", "linux-amd64",  # TODO: Should this really be hard-coded?
            "--class-path", str(classes_dir),
            str(temp_path / "jmod" / "java.base.jmod"),
        ]
        subprocess.run(jmod_command, check=True)

        jlink_command = [
            str(args.java_home / "bin" / f"jlink{exe_extension}"),
            "--module-path", str(temp_path / "jmod"),
            "--add-modules", "java.base",
            "--output", str(args.output),
            "--disable-plugin", "system-modules",
            "--disable-plugin", "generate-jli-classes",
        ]
        subprocess.run(jlink_command, check=True)

        shutil.copy(args.java_home / "lib" / "jrt-fs.jar", args.output / "lib")


if __name__ == "__main__":
    main(sys.argv[1:])
