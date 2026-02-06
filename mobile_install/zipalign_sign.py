#!/usr/bin/python3

import argparse
import pathlib
import sys
import subprocess
import tempfile
import typing
import zipfile


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Zipalign and signs the given apk.")
    parser.add_argument("--zipalign", required=True)
    parser.add_argument("--unsigned-apk", required=True)
    parser.add_argument("--jvm", required=True)
    parser.add_argument("--apk-signer", required=True)
    parser.add_argument("--signed-apk", required=True)
    parser.add_argument("signing_params", nargs="+")
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    args = parse_args(argv)
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_apk = str(pathlib.Path(temp_dir, "zipaligned.apk"))
        subprocess.run([args.zipalign, "-P", "16", "4", args.unsigned_apk, tmp_apk], check=True)
        subprocess.run([args.jvm, "-jar", args.apk_signer, "sign"]
                       + args.signing_params
                       + ["--out", args.signed_apk, tmp_apk],
                       check=True)


if __name__ == "__main__":
    main(sys.argv[1:])
