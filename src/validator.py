import re
from typing import Dict, Any, List, Tuple

class ValidationError:
    def __init__(self, path: str, message: str, expected: str, actual: Any):
        self.path = path
        self.message = message
        self.expected = expected
        self.actual = actual

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "message": self.message,
            "expected": self.expected,
            "actual": str(self.actual)
        }

    def __repr__(self) -> str:
        return f"ValidationError(path={self.path!r}, msg={self.message!r})"

class ContractValidator:
    """Validates runtime JSON payloads against declarative schema contracts."""

    TYPE_MAP = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict
    }

    def validate(self, schema: Dict[str, Any], payload: Any, path: str = "$") -> List[ValidationError]:
        errors: List[ValidationError] = []

        # 1. Type validation
        expected_type_str = schema.get("type")
        if expected_type_str:
            py_type = self.TYPE_MAP.get(expected_type_str)
            if py_type:
                # Disallow booleans being treated as ints in Python
                if expected_type_str == "integer" and isinstance(payload, bool):
                    errors.append(ValidationError(path, f"Expected integer, got boolean", "integer", type(payload).__name__))
                    return errors
                if expected_type_str == "number" and isinstance(payload, bool):
                    errors.append(ValidationError(path, f"Expected number, got boolean", "number", type(payload).__name__))
                    return errors
                if not isinstance(payload, py_type):
                    errors.append(ValidationError(path, f"Expected {expected_type_str}, got {type(payload).__name__}", expected_type_str, type(payload).__name__))
                    return errors

        # 2. Object validation
        if isinstance(payload, dict):
            required = schema.get("required", [])
            for req in required:
                if req not in payload:
                    errors.append(ValidationError(f"{path}.{req}", f"Missing required property {req!r}", "present", "missing"))

            props = schema.get("properties", {})
            for key, val in payload.items():
                if key in props:
                    errors.extend(self.validate(props[key], val, f"{path}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(ValidationError(f"{path}.{key}", f"Undeclared property {key!r} not allowed", "undefined", key))

        # 3. Numeric constraints
        if isinstance(payload, (int, float)) and not isinstance(payload, bool):
            if "minimum" in schema and payload < schema["minimum"]:
                errors.append(ValidationError(path, f"Value {payload} < minimum {schema['minimum']}", f">= {schema['minimum']}", payload))
            if "maximum" in schema and payload > schema["maximum"]:
                errors.append(ValidationError(path, f"Value {payload} > maximum {schema['maximum']}", f"<= {schema['maximum']}", payload))

        # 4. String constraints
        if isinstance(payload, str):
            if "minLength" in schema and len(payload) < schema["minLength"]:
                errors.append(ValidationError(path, f"Length {len(payload)} < minLength {schema['minLength']}", f"len >= {schema['minLength']}", len(payload)))
            if "pattern" in schema and not re.search(schema["pattern"], payload):
                errors.append(ValidationError(path, f"String does not match pattern {schema['pattern']}", schema["pattern"], payload))
            if "enum" in schema and payload not in schema["enum"]:
                errors.append(ValidationError(path, f"Value {payload!r} not in enum {schema['enum']}", f"one of {schema['enum']}", payload))

        return errors
