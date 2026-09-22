# REST API Schema Guard & Contract Fuzzer

[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API Testing](https://img.shields.io/badge/testing-API%20Contract-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

A declarative REST API contract testing and JSON Schema validation framework with automated edge-case fuzzing and payload type auditing.

---

## Overview

In microservices and API-driven architectures, breaking changes and subtle type drifts can lead to silent downstream service failures. 

`rest-api-schema-guard` provides:
1. **Strict Declarative Validation:** Enforces JSON Schema specifications (types, regex patterns, enum sets, min/max bounds, required properties).
2. **Additional Property Guard:** Prevents undeclared payload parameter pollution (`additionalProperties: false`).
3. **Adversarial Contract Fuzzing:** Automatically generates negative boundary test cases from valid schemas to audit endpoint resilience and ensure 100% violation detection.

---

## Architecture

```
                    Raw REST Request / Response
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │   ContractValidator   │  (Type & Range Invariants)
                     └───────────┬───────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
            Valid Payload             ValidationError List
            (Passed Audit)            - Target Path
                                      - Expected Constraint
                                      - Actual Value

                                 │
                                 ▼
                     ┌───────────────────────┐
                     │    ContractFuzzer     │  (Adversarial Mutations)
                     └───────────────────────┘
```

---

## Quickstart

### Installation
```bash
git clone https://github.com/jacobastorga/rest-api-schema-guard.git
cd rest-api-schema-guard
pip install -r requirements.txt
```

### Running Tests
```bash
pytest tests/ -v
```

### Example Usage
```python
from src.validator import ContractValidator

validator = ContractValidator()
schema = {
    "type": "object",
    "required": ["user_id", "email"],
    "properties": {
        "user_id": {"type": "integer", "minimum": 1},
        "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"}
    }
}

errors = validator.validate(schema, payload)
if not errors:
    print("API Contract Verified!")
```

---

## Author
**Jacob Astorga**  
Software Engineer & Computational Scientist  
Portfolio: [github.com/jacobastorga](https://github.com/jacobastorga)
