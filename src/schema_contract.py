from typing import Dict, Any, List, Optional

class SchemaContract:
    """Represents an API endpoint specification and associated request/response JSON schemas."""

    def __init__(self, endpoint: str, method: str, schema_dict: Dict[str, Any]):
        self.endpoint = endpoint
        self.method = method.upper()
        self.schema = schema_dict

    @property
    def required_fields(self) -> List[str]:
        return self.schema.get("required", [])

    @property
    def properties(self) -> Dict[str, Any]:
        return self.schema.get("properties", {})

    def __repr__(self) -> str:
        return f"SchemaContract({self.method} {self.endpoint})"
