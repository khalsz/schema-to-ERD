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


@dataclass
class SchemaModel:
    tables: List[SchemaTable]
    relationships: List[SchemaRelationship]


class SchemaModeller:
    def __init__(self, schema: Dict[str, Any], enable_ref: bool = False):
        self._schema = schema
        self._tables: List[SchemaTable] = []
        self._relationships: List[SchemaRelationship] = []
        self._enable_ref = enable_ref

    def build(self) -> SchemaModel:
        root_title = self._schema.get("title", "Root")
        self._process_schema(root_title, self._schema, parent_table=None, is_root=True)
        return SchemaModel(tables=self._tables, relationships=self._relationships)

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
        if table_name in self._tables and not is_root:
            return

        schema_properties = schema.get("properties", {}) or {}
        required_fields = set(schema.get("required", []))
        properties_list: List[SchemaProperty] = []

        properties_list = self._build_properties(
            table_name=table_name,
            schema_properties=schema_properties,
            required_fields=required_fields,
            parent_table=parent_table,
        )
        self._tables.append(
            SchemaTable(
                table_name=table_name,
                description=schema.get("description"),
                title=schema.get("title"),
                is_root=is_root,
                properties=properties_list,
            )
        )

    def _build_properties(
        self,
        table_name: str,
        schema_properties: Dict[str, Any],
        required_fields: set[str],
        parent_table: Optional[str],
    ) -> List[SchemaProperty]:
        property_list: List[SchemaProperty] = []

        for prop_name, raw_prop_schema in schema_properties.items():
            prop_name = normalize_name(prop_name)
            prop_schema = raw_prop_schema

            # if "$ref" in prop_schema:
            #     resolved = self._resolve_ref(prop_schema["$ref"])
            # prop_schema.update(resolved)
            prop_type = prop_schema.get("type", "")
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
            property_list.append(prop)

            if prop_type == "array":
                self._handle_array_property(table_name, prop_name, prop_schema)
            if prop_type == "object":
                self._handle_object_property(table_name, prop_name, prop_schema)

        return property_list

    # Nested array of objects → new table + 1:N relationship
    def _handle_array_property(
        self, table_name: str, prop_name: str, prop_schema: Dict[str, Any]
    ) -> None:
        items = prop_schema.get("items") or {}

        if items.get("type") == "object":
            nested_table_name = items.get("title", f"{table_name}_{prop_name}_items")
            self._process_schema(nested_table_name, items, parent_table=table_name)
            # if items.get("type") == "array":
            #     nested_table_name = items.get(
            #         "title", f"{table_name}_{prop_name}_items"
            #     )
            #     nested_item = items.get("items")

            self._relationships.append(
                SchemaRelationship(
                    from_table=table_name,
                    to_table=nested_table_name,
                    foreign_key=prop_name,
                    relationship_type="1:N",
                )
            )

    def _handle_object_property(
        self, table_name: str, prop_name: str, prop_schema: Dict[str, Any]
    ) -> None:
        nested_table_name = prop_schema.get("title", f"{prop_name}")

        self._process_schema(nested_table_name, prop_schema, parent_table=prop_name)

        self._relationships.append(
            SchemaRelationship(
                from_table=table_name,
                to_table=nested_table_name,
                foreign_key=prop_name,
                relationship_type="1:N",
            )
        )

    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        if not self._enable_ref:
            raise NotImplementedError("Ref resolution disabled (enable_ref=False)")

        # TODO: implement according to your schema strategy:
        #  - local references in self._schema
        #  - external file references
        raise NotImplementedError(f"Ref resolution not implemented for {ref}")


def normalize_name(name: str) -> str:
    replacement = str.maketrans({"-": "_", " ": "_"})
    return name.translate(replacement).strip()
