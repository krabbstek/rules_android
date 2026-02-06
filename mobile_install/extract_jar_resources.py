#!python

import argparse
import pathlib
import sys
import tempfile
import typing
import zipfile


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Extract resources from .jar")
    parser.add_argument("input_jar")
    parser.add_argument("output_jar")
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    args = parse_args(argv)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)

        with zipfile.ZipFile(args.input_jar, "r") as zip_input:
            zip_input.extractall(temp_dir)

        for class_file in temp_path.rglob(".class"):
            class_file.unlink()

        with zipfile.ZipFile(args.output_jar, "w") as zip_output:
            for absolute_path in temp_path.rglob("*"):
                relative_path = absolute_path.relative_to(temp_dir)
                zip_output.write(absolute_path, relative_path)


if __name__ == "__main__":
    main(sys.argv[1:])
