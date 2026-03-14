from typing import Dict, List

import pandas as pd
from graphviz import Digraph

from modelling import SchemaRelationship


class SchemaViz:
    def __init__(
        self, tables: Dict[str, pd.DataFrame], relationships: List[SchemaRelationship]
    ):
        self._relationship = relationships
        self._tables = tables

    def _format_table(self, name: str, df: pd.DataFrame) -> str:
        """
        Build a Graphviz HTML-like table label with proper column alignment.
        """
        rows: List[str] = []

        # Header row
        rows.append("<TR>" f"<TD COLSPAN='3'><B>{name}</B></TD>" "</TR>")

        rows.append(
            "<TR>"
            "<TD><B>Fields</B></TD>"
            "<TD><B>Type</B></TD>"
            "<TD><B>Description</B></TD>"
            "</TR>"
        )

        # Data rows
        for _, row in df.iterrows():
            field = row["Field"]
            dtype = row["Type"]
            desc = row["Description"] or ""

            rows.append(
                "<TR>"
                f"<TD ALIGN='LEFT'>{field}</TD>"
                f"<TD ALIGN='LEFT'>{dtype}</TD>"
                f"<TD ALIGN='LEFT'>{desc}</TD>"
                "</TR>"
            )

        table = (
            "<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0' CELLPADDING='6'>"
            + "".join(rows)
            + "</TABLE>>"
        )

        return table

    def render_table(self, outfile: str = "scheman", fmt: str = "png") -> None:
        dot = Digraph(
            "schema",
            graph_attr={
                "rankdir": "TB",
                "ranksep": "2.0",  # Increase vertical spacing
                "nodesep": "0.5",  # Decrease horizontal spacing
            },
        )

        for name, df in self._tables.items():
            dot.node(name, label=self._format_table(name, df), shape="plaintext")

        for rel in self._relationship:
            dot.edge(rel.from_table, rel.to_table, label=rel.relationship_type)
            # if name == rel.from_table:
            #     parent = name
            #     target = rel.to_table
            #     relationship = rel.relationship_type
            #     dot.edge(parent, target)
        dot.render(filename=outfile, format=fmt, cleanup=True)
