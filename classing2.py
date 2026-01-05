from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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


class SchemaModeller:
    def __init__(self, schema: Dict[str, Any], enable_ref: bool = False):
        self.schema = schema
        self.tables: Dict[str, SchemaTable] = {}
        self.relationships: List[SchemaRelationship] = []
        self.enable_ref = enable_ref

    def __call__(self) -> tuple[Dict[str, SchemaTable], List[SchemaRelationship]]:
        """Main conversion method"""
        root_title = self.schema.get("title", "Root")
        self._process_schema(root_title, self.schema, parent_table=None, is_root=True)
        return self.tables, self.relationships

    def _process_schema(
        self,
        table_name: str,
        schema: Dict[str, Any],
        parent_table: Optional[str],
        is_root: bool = False,
    ):
        if table_name in self.tables and not is_root:
            return

        schema_properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        is_required = False
        properties_list = []

        for prop_name, prop_schema in schema_properties.items():
            prop_type = prop_schema.get("type", "any")
            prop_name = prop_name.replace("-", "_").strip()

            if "$ref" in prop_schema:
                prop_schema = self._resolve_ref(prop_schema["$ref"])

            if prop_name in required_fields:
                is_required = True

            prop = SchemaProperty(
                name=prop_name,
                type=prop_schema.get("type"),
                description=prop_schema.get("description"),
                required=is_required,
                unit=prop_schema.get("unit"),
                format=prop_schema.get("format", ""),
                parent_table=parent_table,
                enum_values=prop_schema.get("enum"),
            )

            properties_list.append(prop)

            if prop_type == "array":
                items = prop_schema.get("items")

                if items.get("type") == "object":
                    nested_table_name = items.get(
                        "title", f"{table_name}_{prop_name}_item"
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
        self.tables[table_name] = SchemaTable(
            table_name=table_name,
            description=schema.get("description"),
            title=schema.get("title"),
            is_root=is_root,
            properties=properties_list,
        )

    def _resolve_ref(self, ref: str):
        if not self.enable_ref:
            ref
        raise NotImplementedError("Ref resolve not ready")

    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert tables to DataFrames"""
        dataframes = {}

        for table_name, table in self.tables.items():
            data = []
            for prop in table.properties:
                data.append(
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

            dataframes[table_name] = pd.DataFrame(data)

        return dataframes

    def get_relationships_df(self) -> pd.DataFrame:
        """Get relationships as DataFrame"""
        data = []
        for rel in self.relationships:
            data.append(
                {
                    "From Table": rel.from_table,
                    "Relationship": rel.relationship_type,
                    "To Table": rel.to_table,
                    "Foreign Key": rel.foreign_key,
                    "Description": rel.description or "-",
                }
            )


class SchemaToERD:
    def __init__(self, schema_model: SchemaModeller, schema_viz: Any):
        self._schema_df = schema_model.to_dataframes()
        self._schema_reltionship = schema_model.get_relationships_df()
        self.schema_viz = schema_viz

    def format_table(self, name: str, data: pd.DataFrame) -> str:
        """
        Build a Graphviz HTML-like table label with proper column alignment.
        """
        rows = []

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


def extract_prop_details(properties: dict, required_fields: list, title):
    all_tables = []

    def recursive(properties, required_fields, title):
        table_list = defaultdict(list)
        for prop, details in properties.items():
            table = {}
            if prop in required_fields:
                field_name = prop + " *"
            else:
                field_name = prop
            field_type = details.get("type", "")
            field_desription = details.get("description", "")

            table["Field"] = field_name
            table["Type"] = field_type
            table["Description"] = field_desription
            table_list[title].append(table)

            if (
                details.get("type", "") == "array"
                and details.get("items").get("type") == "object"
            ):
                array_prop = details.get("items").get("properties")
                required_array = details.get("items").get("required", [])
                recursive(array_prop, required_array, prop)
            if details.get("type", "") == "object":
                required_object = details.get("required", [])
                object_prop = details.get("properties")
                recursive(object_prop, required_object, prop)

        all_tables.append(dict(table_list))

    recursive(properties, required_fields, title)
    return all_tables


def get_array_vals(prop: dict):
    if prop.get("type", "") == "array" and prop.get("items").get("type") == "object":
        items = prop.get("items")
        array_prop = get_properties(items)
        required_array = get_required_fields(items)
        return array_prop, required_array


def get_required_fields(schema: dict):
    return schema.get("required", [])


def get_properties(schema: dict):
    return schema.get("properties", {})


def get_title_from_id(schema: dict):
    _id = schema.get("$id", "Root Table")
    return _id.split("/")[-1] if _id else None


def get_title(schema: dict):
    return schema.get("title", get_title_from_id(schema))


data = read_json(
    "/Users/ds2718/ukaea/ukaea-metadata/ukaea-schema/equipment/pyrometer.schema.json"
)


def normalize(name: str) -> str:
    return name.replace("-", "_").strip()


def format_table(name: str, df: pd.DataFrame) -> str:
    """
    Build a Graphviz HTML-like table label with proper column alignment.
    """
    rows = []

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


tables = {normalize(list(d.keys())[0]): list(d.values())[0] for d in data}


dfs = {name: pd.DataFrame(value) for name, value in tables.items()}


def add_relationship_metadata(data_df: pd.DataFrame) -> pd.DataFrame:
    data_df = data_df.copy()

    data_df["RefTable"] = data_df.apply(
        lambda row: normalize(row["Field"].replace("*", "").strip())
        if row["Type"] == "object"
        else None,
        axis=1,
    )
    return data_df


dfs = {name: add_relationship_metadata(df) for name, df in dfs.items()}


erd = ERD()


dot = Digraph(
    "schema",
    graph_attr={
        "rankdir": "TB",
        "ranksep": "2.0",  # Increase vertical spacing
        "nodesep": "0.5",  # Decrease horizontal spacing
    },
)

for name, df in dfs.items():
    dot.node(name, label=format_table(name, df), shape="plaintext")

# Draw edges from specific field cells
for parent, df in dfs.items():
    for i, row in df.iterrows():
        target = row["RefTable"]
        if target and target in dfs:
            dot.edge(parent, target)

# Render ERD
dot.render("schema_erd", format="png", cleanup=True)


class SchemaViz:
    def __init__(self, table_name: str, dfs: Dict[str, pd.DataFrame]):
        self.table_name = table_name
        self.data = dfs

    def _format_table(name: str, df: pd.DataFrame) -> str:
        """
        Build a Graphviz HTML-like table label with proper column alignment.
        """
        rows = []

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

    def render_table(self, relationships: list[SchemaRelationship]):
        erd = ERD()

        dot = Digraph(
            "schema",
            graph_attr={
                "rankdir": "TB",
                "ranksep": "2.0",  # Increase vertical spacing
                "nodesep": "0.5",  # Decrease horizontal spacing
            },
        )

        for name, df in self.data.items():
            dot.node(name, label=self._format_table(name, df), shape="plaintext")

            for rel in relationships:
                if name == rel.from_table:
                    parent = name
                    target = rel.to_table
                    relationship = rel.relationship_type
                    dot.edge(parent, target)
        dot.render("schema_name", format="png", cleanup=True)
