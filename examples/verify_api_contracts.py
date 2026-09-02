import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.validator import ContractValidator
from src.contract_fuzzer import ContractFuzzer

def main():
    payment_order_schema = {
        "type": "object",
        "required": ["order_id", "amount", "currency", "customer_email"],
        "properties": {
            "order_id": {"type": "string", "pattern": r"^ORD-[0-9]{5}$"},
            "amount": {"type": "number", "minimum": 0.50},
            "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]},
            "customer_email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"}
        }
    }

    valid_order = {
        "order_id": "ORD-49201",
        "amount": 149.99,
        "currency": "USD",
        "customer_email": "billing@cloudsystems.io"
    }

    validator = ContractValidator()
    print("1. Validating Production Payment Contract Payload...")
    errors = validator.validate(payment_order_schema, valid_order)
    print(f"Validation Result: {'PASSED (Zero Errors)' if not errors else 'FAILED'}")

    print("\n2. Running Adversarial Schema Fuzzer...")
    fuzzer = ContractFuzzer()
    resilience_report = fuzzer.audit_fuzz_resilience(payment_order_schema, valid_order)
    print(f"Total Fuzz Mutations Generated: {resilience_report['total_mutations']}")
    print(f"Violations Caught by Validator:  {resilience_report['caught_mutations']}")
    print(f"Catch Rate:                     {resilience_report['catch_rate'] * 100:.1f}%")
    print(f"Contract Resilient:             {resilience_report['resilient']}")

if __name__ == "__main__":
    main()
