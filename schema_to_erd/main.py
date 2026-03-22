import json
import logging

from .modelling import SchemaModeller
from .tabularize import TabularAdapter
from .vizualizer import SchemaViz

logger = logging.getLogger(__name__)


def build_erd_from_schema(json_file: str, output: str, fmt: str) -> None:
    logger.info(f"Loading schema file: {json_file}")

    with open(json_file) as jf:
        schema = json.load(jf)

    logger.info("Modelling schema into table...")
    modeller = SchemaModeller(schema)
    model = modeller.build()

    adapter = TabularAdapter(model)

    dfs = adapter.table_df

    logger.info("Building ERD diagram for schema table")
    viz = SchemaViz(dfs, model.relationships)

    logger.info("Converting schema table to ERD diagram")
    viz.render_table(outfile=output, fmt=fmt)
