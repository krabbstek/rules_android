#!/usr/bin/python3

import argparse
import pathlib
import platform
import subprocess
import sys
import tempfile
import typing
import zipfile

from python.runfiles import runfiles


# TODO: Source stuff

def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Dex and optionally minify supported Java 8 libs using d8/r8.")
    parser.fromfile_prefix_chars = "@"
    parser.add_argument("--rules", type=pathlib.Path)
    parser.add_argument("--binary", dest="binary_jar")
    parser.add_argument("--output", dest="dest")
    parser.add_argument("--output-map", dest="map")
    parser.add_argument("--android-jar")
    parser.add_argument("--min-api")
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    r = runfiles.Create()

    params_txt = r.Rlocation("rules_android/tools/android/build_java8_legacy_dex_params.txt")
    args = parse_args(argv + ["@%s" % params_txt])

    todex = r.Rlocation("rules_android/tools/android/desugared_jdk_libs.jar")

    if args.binary_jar:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            rules = args.rules or temp_path / "rules.pgcfg"
            subprocess.run(
                [r.Rlocation("rules_android/tools/android/tracereferences"),
                 "--map-diagnostics:MissingDefinitionsDiagnostic", "error", "warning",
                 "--keep-rules",
                 "--lib", args.android_jar,
                 "--source", args.binary_jar,
                 "--target", todex,
                 "--output", str(args.rules)],
                check=True,
            )

            if not rules.exists() or not rules.read_text():
                # No keep rules, meaning nothing to keep, so emit an empty zip
                with zipfile.ZipFile(args.dest, mode="w") as zip_output:
                    zip_output.write(args.rules, arcname=args.rules.name)  # TODO: Is this correct??
                if args.map:
                    with open(args.map, "w") as map_file:
                        map_file.write("# No desugared library mapping\n")
            else:
                r8_command = [
                    r.Rlocation("rules_android/tools/android/r8"),
                    "--min-api", args.min_api,
                    "--no-desugaring",
                    "--lib", args.android_jar,
                    "--pg-conf", args.minify_desugar_jdk_libs_pgcfg,
                    "--pg-conf", str(rules),
                    "--output", args.dest,
                ]
                if args.map:
                    r8_command.extend(["--pg-map-output", args.map])
                r8_command.append(todex)
                subprocess.run(r8_command, check=True)

    else:
        # No shrinking just convert to DEX.
        subprocess.run(
            [r.Rlocation("rules_android/tools/android/d8"),
             "--min-api", args.min_api,
             "--no-desugaring",
             "--lib", args.android_jar or "",
             "--output", args.dest,
             todex],
             check=True,
        )


if __name__ == "__main__":
    main(sys.argv[1:])
