import json


def read_json(json_file: str):
    with open(json_file) as jf:
        schema = json.load(jf)

    title = get_title(schema)

    required_fields = get_required_fields(schema)

    properties = get_properties(schema)

    for prop, details in properties:
        is_required = prop in properties

        if prop.get("type", '') == "object":

    


def extract_prop_details(properties: dict, required_fields: list):
    table = {}
    required_list = properties.get("requried", [])
    for prop, details in properties.items():
        if prop in required_fields:
            field_name = prop + "*"
        else:
            field_name = prop

        if prop.get("type", "") == "array":
            for 
        if prop.get("type", '') == "object":
            extract_prop_details(prop, required_list)

        
        field_type = details.get("type", "")
        field_desription = details.get("description", "")
        
        table["Field"] = field_name 
        table["Type"] = field_type
        table["Description"] = field_desription


    


def get_required_fields(schema:dict):
    return schema.get("required", [])


def get_properties(schema:dict):
    return schema.get("properties", {})

def get_title(schema:dict):
    return schema.get("title", "")



