import json
from typing import Any, Dict

from modelling import SchemaModeller
from tabular import TabularAdapter
from vizualizer import SchemaViz


def build_erd_from_schema(schema: Dict[str, Any], output: str = "schema_erd") -> None:
    modeller = SchemaModeller(schema)
    model = modeller.build()

    adapter = TabularAdapter(model)

    dfs = adapter.table_df

    viz = SchemaViz(dfs, model.relationships)

    viz.render_table(output)


def load_json(json_file):
    with open(json_file) as jf:
        return json.load(jf)
