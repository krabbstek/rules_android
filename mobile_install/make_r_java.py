#!/usr/bin/python3

""" Remove final qualifiers from R.java.

R classes used during library compilation have only library level
information about app resources, therefore we strip those files but still
need to repackage the final version of the R classes for all packages.

In theory we could implement this as a provider in blaze and use whatever
they create, however their implementation might be suboptimal.
"""

import argparse
import pathlib
import re
import sys
import tempfile
import typing
import zipfile


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Extract resources from .jar")
    parser.add_argument("--resource-src-jar", required=True, type=pathlib.Path)
    parser.add_argument("--main-r-java", required=True)
    parser.add_argument("--out-r-java", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    args = parse_args(argv)

    with tempfile.TemporaryDirectory() as r_java_dir:
        r_java = args.resource_src_jar
        if args.resource_src_jar.suffix != ".java":
            with zipfile.ZipFile(args.resource_src_jar) as jarfile:
                r_java = pathlib.Path(jarfile.extract(args.main_r_java, r_java_dir))

        if r_java.exists():
            r_java_contents = r_java.read_text()
            r_java_contents = r_java_contents.replace("final class", "class")
            r_java_contents = re.sub(r"^package .*;$", "", r_java_contents, flags=re.MULTILINE)
            args.out_r_java.write_text(r_java_contents)
        else:
            args.out_r_java.touch()


if __name__ == "__main__":
    main(sys.argv[1:])
