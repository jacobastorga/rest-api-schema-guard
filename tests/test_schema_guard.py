import unittest
from src.validator import ContractValidator
from src.contract_fuzzer import ContractFuzzer

class TestSchemaGuard(unittest.TestCase):

    def setUp(self):
        self.validator = ContractValidator()
        self.fuzzer = ContractFuzzer()
        self.user_schema = {
            "type": "object",
            "required": ["id", "username", "email", "age"],
            "additionalProperties": False,
            "properties": {
                "id": {"type": "integer", "minimum": 1},
                "username": {"type": "string", "minLength": 3, "pattern": r"^[a-zA-Z0-9_]+$"},
                "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
                "age": {"type": "integer", "minimum": 18, "maximum": 120},
                "role": {"type": "string", "enum": ["user", "admin", "analyst"]}
            }
        }
        self.valid_user = {
            "id": 101,
            "username": "j_astorga",
            "email": "jacob@example.com",
            "age": 28,
            "role": "admin"
        }

    def test_valid_payload_passes(self):
        errors = self.validator.validate(self.user_schema, self.valid_user)
        self.assertEqual(len(errors), 0)

    def test_missing_required_property(self):
        bad_payload = dict(self.valid_user)
        del bad_payload["email"]
        errors = self.validator.validate(self.user_schema, bad_payload)
        self.assertTrue(any(e.path == "$.email" for e in errors))

    def test_type_mismatch_int_as_str(self):
        bad_payload = dict(self.valid_user, age="twenty_eight")
        errors = self.validator.validate(self.user_schema, bad_payload)
        self.assertTrue(any(e.path == "$.age" for e in errors))

    def test_numeric_boundary_violation(self):
        bad_payload = dict(self.valid_user, age=16)
        errors = self.validator.validate(self.user_schema, bad_payload)
        self.assertTrue(any(e.path == "$.age" for e in errors))

    def test_additional_property_disallowed(self):
        bad_payload = dict(self.valid_user, unauthorized_token="root")
        errors = self.validator.validate(self.user_schema, bad_payload)
        self.assertTrue(any("unauthorized_token" in e.path for e in errors))

    def test_fuzzer_catches_all_negative_cases(self):
        audit = self.fuzzer.audit_fuzz_resilience(self.user_schema, self.valid_user)
        self.assertTrue(audit["resilient"])
        self.assertEqual(audit["catch_rate"], 1.0)

if __name__ == "__main__":
    unittest.main()
