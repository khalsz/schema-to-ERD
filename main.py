import argparse

from pipeline import build_erd_from_schema, load_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--schema", required=True, help="schema file to vizualize", type=load_json
    )

    args = parser.parse_args()

    schema = args.schema

    build_erd_from_schema(schema)
