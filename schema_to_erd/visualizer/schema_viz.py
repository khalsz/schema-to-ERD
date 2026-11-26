from html import escape

import pandas as pd
from graphviz import Digraph

from ..modelling.schema_modeller import SchemaRelationship


class SchemaViz:
    def __init__(
        self,
        tables: dict[str, pd.DataFrame],
        relationships: list[SchemaRelationship],
    ):
        self._relationship = relationships
        self._tables = tables

    def _format_table(
        self, name: str, df: pd.DataFrame, description: bool = False
    ) -> str:
        """
        Build a Graphviz HTML-like table label with coloured headers,
        required field indicators and coloured data types.
        """

        columns = ["Fields", "Type"]

        if description:
            columns.append("Description")

        # Data type colour palette: background, foreground
        type_colours = {
            "string": ("#DCFCE7", "#15803D"),
            "object": ("#DBEAFE", "#1D4ED8"),
            "integer": ("#EDE9FE", "#6D28D9"),
            "number": ("#FFEDD5", "#C2410C"),
            "array": ("#CCFBF1", "#0F766E"),
        }

        rows = [
            f"<TR><TD COLSPAN='{len(columns)}' BGCOLOR='#263449'>"
            f"<FONT COLOR='white'><B>{escape(str(name))}</B></FONT>"
            "</TD></TR>",
            "<TR>"
            + "".join(
                f"<TD BGCOLOR='#526477'>"
                f"<FONT COLOR='white'><B>{column}</B></FONT>"
                "</TD>"
                for column in columns
            )
            + "</TR>",
        ]

        # Data rows
        for _, row in df.iterrows():
            field = str(row["Field"])
            data_type = str(row["Type"])

            # Identify required fields
            required = field.startswith("*")
            field_name = field.removeprefix("*").strip()

            if required:
                field_content = (
                    "<FONT COLOR='#1D4ED8'><B>*</B></FONT> "
                    f"{escape(field_name)}"
                )
            else:
                field_content = escape(field_name)

            field_background = "white"

            field_cell = (
                f"<TD ALIGN='LEFT' BGCOLOR='{field_background}'>"
                f"{field_content}</TD>"
            )

            # Identify data type, including arrays
            normalized_type = data_type.strip().lower()

            if normalized_type.startswith("array"):
                type_key = "array"
            else:
                type_key = normalized_type

            background, foreground = type_colours.get(
                type_key, ("#F1F5F9", "#475569")
            )

            # Data type cell (no nested table)
            type_cell = (
                f"<TD ALIGN='LEFT' BGCOLOR='{background}'>"
                f"<FONT COLOR='{foreground}' POINT-SIZE='9'>"
                f"<B>{escape(data_type)}</B>"
                "</FONT></TD>"
            )

            cells = field_cell + type_cell

            # Optional description column
            if description:
                desc = row["Description"]
                desc = "" if pd.isna(desc) else desc

                cells += f"<TD ALIGN='LEFT'>{escape(str(desc))}</TD>"

            rows.append(f"<TR>{cells}</TR>")

        table = (
            "<<TABLE BORDER='1' CELLBORDER='1' "
            "CELLSPACING='0' CELLPADDING='6'>" + "".join(rows) + "</TABLE>>"
        )

        return table

    def render_table(self, outfile: str, fmt: str) -> None:
        dot = Digraph(
            "schema",
            graph_attr={
                "rankdir": "TB",
                "ranksep": "2.0",
                "nodesep": "0.5",
                "bgcolor": "transparent",
            },
        )

        for name, df in self._tables.items():
            dot.node(name, label=self._format_table(name, df), shape="plaintext")

        for rel in self._relationship:
            dot.edge(rel.from_table, rel.to_table)
            # if name == rel.from_table:
            #     parent = name
            #     target = rel.to_table
            #     relationship = rel.relationship_type
            #     dot.edge(parent, target)
        dot.render(filename=outfile, format=fmt, cleanup=True)
