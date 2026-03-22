import argparse
import os

from .main import build_erd_from_schema


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON schema into an ERD diagram (simple and readable)"
    )

    parser.add_argument("--input", required=True, help="Schema file path")

    parser.add_argument(
        "-o",
        "--out-file",
        help="output file name (defualt: same as input file name)",
        # default="schema_2_erd",
    )
    parser.add_argument("--format", help="output file format", default="png")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        parser.error(f"Input file does not exits: {args.input}")

    schema_file = args.input

    filename = os.path.basename(args.input)
    name = os.path.splitext(filename)[0]
    output = args.out_file or name

    print(output)

    fmt = args.format

    build_erd_from_schema(schema_file, output, fmt)
