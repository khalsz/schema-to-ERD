import json
from typing import Any, Dict

from modelling import SchemaModeller
from tabularize import TabularAdapter
from vizualizer import SchemaViz


def build_erd_from_schema(schema: Dict[str, Any], output: str, fmt: str) -> None:
    modeller = SchemaModeller(schema)
    model = modeller.build()

    adapter = TabularAdapter(model)

    dfs = adapter.table_df

    viz = SchemaViz(dfs, model.relationships)

    viz.render_table(outfile=output, fmt=fmt)


def load_json(json_file) -> Dict:
    with open(json_file) as jf:
        schema = json.load(jf)
    return schema
