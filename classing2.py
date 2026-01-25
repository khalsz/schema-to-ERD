from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
from graphviz import Digraph


@dataclass
class SchemaProperty:
    """Represents a single property in the schema"""

    name: str
    type: str
    description: Optional[str] = None
    unit: Optional[str] = None
    format: Optional[str] = None
    parent_table: Optional[str] = None
    enum_values: Optional[List[str]] = None
    is_array: bool = False
    is_object: bool = False
    required: bool = False


@dataclass
class SchemaTable:
    """Represents a table (object) in the ERD"""

    table_name: str
    description: Optional[str]
    title: Optional[str]
    is_root: bool = False
    properties: List[SchemaProperty] = field(default_factory=list)


@dataclass
class SchemaRelationship:
    """Represents a relationship between tables"""

    from_table: str
    to_table: str
    foreign_key: str
    relationship_type: str  # "1:1", "1:N", "N:M"
    description: Optional[str] = None


@dataclass
class SchemaModel:
    table: Dict[str, SchemaTable]
    relationships: List[SchemaRelationship]


class SchemaModeller:
    def __init__(self, schema: Dict[str, Any], enable_ref: bool = False):
        self._schema = schema
        self._tables: Dict[str, SchemaTable] = {}
        self._relationships: List[SchemaRelationship] = []
        self._enable_ref = enable_ref

    def build(self) -> SchemaModel:
        root_title = self.schema.get("title", "Root")
        self._process_schema(root_title, self.schema, parent_table=None, is_root=True)
        return SchemaModel(table=self.tables, relationships=self.relationships)

    @property
    def relationships(self) -> List[SchemaRelationship]:
        return self._relationships

    def _process_schema(
        self,
        table_name: str,
        schema: Dict[str, Any],
        parent_table: Optional[str],
        is_root: bool = False,
    ) -> None:
        if table_name in self.tables and not is_root:
            return

        schema_properties = schema.get("properties", {}) or {}
        required_fields = set(schema.get("required", []))
        properties_list: List[SchemaProperty] = []

        for prop_name, raw_prop_schema in schema_properties.items():
            prop_name = normalize_name(prop_name)
            prop_schema = raw_prop_schema

            # if "$ref" in prop_schema:
            #     prop_schema = self._resolve_ref(prop_schema["$ref"])
            prop_type = raw_prop_schema.get("type", "")
            required = prop_name in required_fields

            prop = SchemaProperty(
                name=prop_name,
                type=prop_type,
                description=prop_schema.get("description", ""),
                required=required,
                unit=prop_schema.get("unit", ""),
                format=prop_schema.get("format", ""),
                parent_table=parent_table,
                enum_values=prop_schema.get("enum", ""),
                is_array=(prop_type == "array"),
                is_object=(prop_type == "object"),
            )

            properties_list.append(prop)

            # Nested array of objects → new table + 1:N relationship
            if prop_type == "array":
                items = raw_prop_schema.get("items") or {}

                if items.get("type") == "object":
                    nested_table_name = items.get(
                        "title", f"{table_name}_{prop_name}_items"
                    )
                    self._process_schema(
                        nested_table_name, items, parent_table=table_name
                    )

                    self.relationships.append(
                        SchemaRelationship(
                            from_table=table_name,
                            to_table=nested_table_name,
                            foreign_key=prop_name,
                            relationship_type="1:N",
                        )
                    )

            # Nested object → new table + 1:1 or 1:N (you chose 1:N)
            if prop_type == "object":
                nested_table_name = prop_schema.get(
                    "title", f"{table_name}_{prop_name}"
                )

                self._process_schema(nested_table_name, prop_schema, table_name)

                self.relationships.append(
                    SchemaRelationship(
                        from_table=table_name,
                        to_table=nested_table_name,
                        foreign_key=prop_name,
                        relationship_type="1:N",
                    )
                )
        self._tables[table_name] = SchemaTable(
            table_name=table_name,
            description=schema.get("description"),
            title=schema.get("title"),
            is_root=is_root,
            properties=properties_list,
        )

    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        if not self._enable_ref:
            raise NotImplementedError("Ref resolution disabled (enable_ref=False)")

        # TODO: implement according to your schema strategy:
        #  - local references in self._schema
        #  - external file references
        raise NotImplementedError(f"Ref resolution not implemented for {ref}")


class TabularAdapter:
    def __init__(self, model: SchemaModel):
        self._model = model

    @property
    def table_df(self) -> Dict[str, pd.DataFrame]:
        """Convert tables to DataFrames"""
        frames: Dict[str, pd.DataFrame] = {}

        for table_name, table in self.tables.items():
            rows = []
            for prop in table.properties:
                rows.append(
                    {
                        "Field": f"* {prop.name}" if prop.required else prop.name,
                        "Type": prop.type,
                        "Unit": prop.unit or "-",
                        "Description": prop.description or "-",
                        "Enum Values": ", ".join(map(str, prop.enum_values))
                        if prop.enum_values
                        else "-",
                    }
                )

            frames[table_name] = pd.DataFrame(rows)
        return frames

    @property
    def relationships_df(self) -> pd.DataFrame:
        """Get relationships as DataFrame"""
        rows = []
        for rel in self.relationships:
            rows.append(
                {
                    "From Table": rel.from_table,
                    "Relationship": rel.relationship_type,
                    "To Table": rel.to_table,
                    "Foreign Key": rel.foreign_key,
                    "Description": rel.description or "-",
                }
            )
        return pd.DataFrame(rows)


def normalize_name(name: str) -> str:
    return name.replace("-", "_").strip()


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

    def render_table(self, filename: str = "schema_erd", fmt: str = "png") -> None:
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
            dot.render(filename, format=fmt, cleanup=True)


def build_erd_from_schema(schema: Dict[str, Any], output: str = "schema_erd") -> None:
    modeller = SchemaModeller(schema)
    model = modeller.build()

    adapter = TabularAdapter(model)

    dfs = adapter.table_df

    viz = SchemaViz(dfs, model.relationships)

    viz.render(output)


# class SchemaToERD:
#     def __init__(self, schema_model: SchemaModeller):
#         self._schema_df = schema_model.to_dataframes()
#         self._schema_relationships = schema_model.relationships
#         # pick some root or pass it in; for now just use first table
#         table_name = next(iter(self._schema_df)) if self._schema_df else "schema"
#         self.schema_viz = SchemaViz(table_name, self._schema_df)

#     def render(self, output_name: str = "schema_erd") -> None:
#         self.schema_viz.render_table(self._schema_relationships)

# OR
# class SchemaToERD:
#     def __init__(self, schema_model: SchemaModeller, schema_viz: SchemaViz):
#         self._schema_df = schema_model.to_dataframes()
#         self._schema_relationships = schema_model.relationships
#         self.schema_viz = schema_viz

#     def render(self, output_name: str = "schema_erd") -> None:
#         # optionally let SchemaViz accept the filename
#         self.schema_viz.render_table(self._schema_relationships)#         self.schema_viz.render_table(self._schema_relationships)#         self.schema_viz.render_table(self._schema_relationships)
