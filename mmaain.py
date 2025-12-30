import json
from collections import defaultdict

import pandas as pd
from graphviz import Digraph
from pandaserd import ERD


def read_json(json_file: str):
    with open(json_file) as jf:
        schema = json.load(jf)

    title = get_title(schema)

    required_fields = get_required_fields(schema)

    properties = get_properties(schema)

    schema_dict = extract_prop_details(properties, required_fields, title)
    return schema_dict


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
        "<TD><B>Field</B></TD>"
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
dot.render("schema_erd", format="png", cleanup=True)
dot.render("schema_erd", format="png", cleanup=True)
