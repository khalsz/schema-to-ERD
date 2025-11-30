import json
from pathlib import Path

from jsonschema import SchemaError


class JSONSchemaInspect:
    def __init__(self, json_file: str):
        with Path(json_file).open("r") as jf:
            self.schema = json.load(jf)

    def __call__(self) -> dict:
        # ValidatorClass = validators.validator_for(self.schema)

        try:
            # ValidatorClass.check_schema(self.schema)
            return self.schema

        except SchemaError as e:
            raise ValueError(f"Invalid Json Schema: {e.message}")


class SchemaMapper:
    def __init__(self, schema: dict, title: None):
        self.schema = schema

    def map_schema_properties(self):
        all_tables = []

        def recursive_mapper(self, title=""):
            properties = self._extract_properties(self.schema)

            schema_title = self.schema.get("title", title)

            required_list = self._extract_required(self.schema)

            for field, details in properties.items():
                table = {}

                if field in required_list:
                    field_name = field + " *"
                else:
                    field_name = field

                field_type = details.get("type", "")
                field_description = details.get("description", "")

                table["Field"] = field_name
                table["Type"] = field_type
                table["Description"] = field_description

            if prop in required_fields:
                field_name = prop + " *"
            else:
                field_name = prop
            field_type = details.get("type", "")
            field_desription = details.get("description", "")

            table["Field"] = field_name
            table["Type"] = field_type
            table["Description"] = field_desription
            table_list.append(table)

            if (
                details.get("type", "") == "array"
                and details.get("items").get("type") == "object"
            ):
                array_prop, required_array = get_array_prop(details)
                recursive(array_prop, required_array)
            if details.get("type", "") == "object":
                object_prop, required_object = get_dict_prop(details)
                recursive(object_prop, required_object)

        all_tables.append(table_list)

    recursive(properties, required_fields)
    return all_tables

    def _extract_properties(self, schema):
        return schema.get("properties", {})

    def _extract_required(self, schema):
        return schema.get("required", [])

    def extract_title(self, schema):
        return schema.get("title", "")
