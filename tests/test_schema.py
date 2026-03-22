import json
import os
import tempfile

from schema_to_erd import build_erd_from_schema


def test_json_schema_object_to_erd():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Product",
        "type": "object",
        "properties": {
            "productId": {"type": "integer"},
            "productName": {"type": "string"},
        },
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "product.schema.json")
        output_base = os.path.join(tmpdir, "product")

        # write schema file
        with open(input_file, "w") as f:
            json.dump(schema, f)

        # run function
        build_erd_from_schema(input_file, output_base, "png")

        # verify output exists
        expected_output = f"{output_base}.png"
        assert os.path.exists(expected_output)
