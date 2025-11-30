import json
from collections import defaultdict

import pandas as pd
from graphviz import Digraph
from pandaserd import ERD


def read_json(json_file: str):
    with open(json_file) as jf:
        schema = json.load(jf)

    # title = get_title(schema)

    required_fields = get_required_fields(schema)

    properties = get_properties(schema)

    title = ""

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
                required_array = details.get("items").get("required")
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
    _id = schema.get("$id")
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
    Build a proper Graphviz table label using record shapes with a header row.
    """
    label = f"{{{{ {name} }}|"  # header row

    field_rows = []
    for field in df["Field"]:
        field_rows.append(f"{field}\\l")  # left-aligned, line break

    label += "".join(field_rows) + "}"
    return label


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


dot = Digraph("schema", graph_attr={"rankdir": "LR"})

# Draw tables
for name, df in dfs.items():
    table_label = format_table(name, df)
    dot.node(name, label=table_label, shape="record")

# Draw relationships
for parent, df in dfs.items():
    for _, row in df.iterrows():
        target = row["RefTable"]
        if target and target in dfs:
            dot.edge(parent, target)

dot.render("schema_erd", format="png", cleanup=True)
