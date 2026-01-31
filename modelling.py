from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
