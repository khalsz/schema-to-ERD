import json
import logging
from pathlib import Path

from .adapters.tabular_adapter import TabularAdapter
from .modelling.schema_modeller import SchemaModeller
from .visualizer.schema_viz import SchemaViz

logger = logging.getLogger(__name__)


def build_erd_from_schema(
    json_file: str, output: str | None = None, fmt: str = "png"
) -> None:
    logger.info(f"Loading schema file: {json_file}")

    schema_path = Path(json_file)

    with schema_path.open(encoding="utf-8") as jf:
        schema = json.load(jf)

    if output is None:
        output = schema_path.stem

    logger.info("Modelling schema into table...")
    modeller = SchemaModeller(schema)
    model = modeller.build()

    adapter = TabularAdapter(model)
    dfs = adapter.table_df

    logger.info("Building ERD diagram for schema table")
    viz = SchemaViz(dfs, model.relationships)

    logger.info("Converting schema table to ERD diagram")
    viz.render_table(outfile=output, fmt=fmt)
