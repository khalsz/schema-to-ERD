from typing import Dict

import pandas as pd

from modelling import SchemaModel


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
