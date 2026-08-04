import copy
from typing import Dict, Any, List
from .validator import ContractValidator

class ContractFuzzer:
    """Automated negative test case generator for verifying API contract enforcement."""

    def __init__(self):
        self.validator = ContractValidator()

    def generate_mutations(self, schema: Dict[str, Any], valid_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates adversarial payload mutations violating schema bounds."""
        mutations = []

        # 1. Missing required field mutations
        for req in schema.get("required", []):
            if req in valid_payload:
                mutated = copy.deepcopy(valid_payload)
                del mutated[req]
                mutations.append({
                    "description": f"Omit required field: {req}",
                    "payload": mutated,
                    "target_field": req
                })

        # 2. Type mutation (injecting string into numeric fields, etc.)
        props = schema.get("properties", {})
        for key, prop_schema in props.items():
            if key in valid_payload:
                expected_type = prop_schema.get("type")
                if expected_type in ("integer", "number"):
                    mutated = copy.deepcopy(valid_payload)
                    mutated[key] = "NOT_A_NUMBER"
                    mutations.append({
                        "description": f"Type corruption in numeric field: {key}",
                        "payload": mutated,
                        "target_field": key
                    })
                elif expected_type == "string":
                    mutated = copy.deepcopy(valid_payload)
                    mutated[key] = 12345
                    mutations.append({
                        "description": f"Type corruption in string field: {key}",
                        "payload": mutated,
                        "target_field": key
                    })

        # 3. Numeric boundary violation
        for key, prop_schema in props.items():
            if key in valid_payload and "minimum" in prop_schema:
                mutated = copy.deepcopy(valid_payload)
                mutated[key] = prop_schema["minimum"] - 1
                mutations.append({
                    "description": f"Violate minimum bound on: {key}",
                    "payload": mutated,
                    "target_field": key
                })

        return mutations

    def audit_fuzz_resilience(self, schema: Dict[str, Any], valid_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Runs fuzzed mutations through validator and verifies 100% rejection rate."""
        mutations = self.generate_mutations(schema, valid_payload)
        caught = 0

        for m in mutations:
            errs = self.validator.validate(schema, m["payload"])
            if len(errs) > 0:
                caught += 1

        return {
            "total_mutations": len(mutations),
            "caught_mutations": caught,
            "catch_rate": (caught / len(mutations)) if mutations else 1.0,
            "resilient": caught == len(mutations)
        }
