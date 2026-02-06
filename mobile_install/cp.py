#!/usr/bin/python3

import argparse
import shutil
import sys
import typing


def parse_args(argv: typing.Optional[typing.List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser("Copy file")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args(argv)
    return args


def main(argv: typing.Optional[typing.List[str]] = None):
    args = parse_args(argv)
    shutil.copy(args.input, args.output)


if __name__ == "__main__":
    main(sys.argv[1:])
