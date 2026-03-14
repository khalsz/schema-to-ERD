import argparse

from pipeline import build_erd_from_schema, load_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--schema", required=True, help="schema file path")
    parser.add_argument("--out-file", help="output file name", default="schema_2_erd")
    parser.add_argument("--format", help="output file format", default="png")

    args = parser.parse_args()

    schema_file = args.schema

    output = args.out_file

    fmt = args.format
    schema = load_json(schema_file)

    build_erd_from_schema(schema, output, fmt)
