# Test Suite Documentation

## Overview

Comprehensive test suite covering all components of the Glass Factory Manufacturing Concierge application.

## Setup

Install testing dependencies:
```bash
pip install pytest pytest-cov
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_scoring.py          # Factory scoring tests
pytest tests/test_requirements.py     # Requirements model tests
pytest tests/test_llm.py              # LLM extraction tests
pytest tests/test_actions.py          # RFQ generation tests
pytest tests/test_integration.py      # Integration tests
```

### Run Specific Test Classes
```bash
pytest tests/test_scoring.py::TestFactoryScoring
pytest tests/test_integration.py::TestEndToEndWorkflow
```

### Run Specific Test Methods
```bash
pytest tests/test_scoring.py::TestFactoryScoring::test_perfect_match
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Skip Slow/LLM Tests
```bash
pytest -m "not llm"      # Skip tests requiring OpenAI API
pytest -m "not slow"     # Skip slow tests
```

## Test Files

### test_scoring.py
Tests for factory scoring and recommendation logic.

**Classes:**
- `TestFactoryScoring`: Tests individual factory scoring
- `TestFactoryRecommendations`: Tests recommendation system
- `TestFactoryDataLoading`: Tests data loading

**Coverage:**
- ✅ Perfect matches
- ✅ Partial matches
- ✅ Product type mismatches
- ✅ MOQ edge cases (below minimum, at minimum, above minimum)
- ✅ Geography matching (case-insensitive)
- ✅ Material compatibility
- ✅ Certification display
- ✅ No matches scenario
- ✅ Recommendation sorting

**Example:**
```bash
pytest tests/test_scoring.py -v
```

### test_requirements.py
Tests for the ManufacturingRequirements data model.

**Classes:**
- `TestRequirementsModel`: Pydantic model validation

**Coverage:**
- ✅ Valid data creation
- ✅ Required vs optional fields
- ✅ Default values
- ✅ Data type validation
- ✅ Invalid inputs
- ✅ Empty lists
- ✅ Edge case values
- ✅ Serialization

**Example:**
```bash
pytest tests/test_requirements.py -v
```

### test_llm.py
Tests for LLM extraction and chat functionality.

**Classes:**
- `TestLLMExtraction`: Requirement extraction from conversations
- `TestLLMChat`: Chat functionality
- `TestNonManufacturingInput`: Handling irrelevant input

**Coverage:**
- ✅ Basic requirement extraction
- ✅ Complete information extraction
- ✅ Missing information handling
- ✅ JSON format validation
- ✅ Product type inference
- ✅ Non-manufacturing conversation handling
- ✅ Partial manufacturing info

**Note:** Some tests require OpenAI API key in `.env` file. They will be skipped if unavailable.

**Example:**
```bash
pytest tests/test_llm.py -v -m "not llm"  # Skip API-dependent tests
```

### test_actions.py
Tests for RFQ email generation.

**Classes:**
- `TestRFQGeneration`: RFQ email generation

**Coverage:**
- ✅ Email format validation
- ✅ Factory name inclusion
- ✅ Requirements inclusion
- ✅ Professional format
- ✅ Minimal requirements
- ✅ Complete requirements
- ✅ Empty certifications
- ✅ None values handling

**Note:** Tests require OpenAI API key in `.env` file.

**Example:**
```bash
pytest tests/test_actions.py -v
```

### test_integration.py
Integration tests for end-to-end workflows.

**Classes:**
- `TestEndToEndWorkflow`: Complete user workflows
- `TestEdgeCases`: Edge case handling
- `TestDataValidation`: Data integrity checks

**Coverage:**
- ✅ Happy path: requirements → recommendations
- ✅ No matches workflow
- ✅ Partial match workflow
- ✅ Conversation → recommendations workflow
- ✅ Multiple materials
- ✅ High MOQ requirements
- ✅ Database integrity
- ✅ Case-insensitive matching
- ✅ Consistency checks
- ✅ Factory data validation
- ✅ Unique IDs
- ✅ Valid cost tiers

**Example:**
```bash
pytest tests/test_integration.py -v
```

## Test Fixtures

Located in `conftest.py`, shared across all tests:

- `sample_factory`: Standard factory data
- `sample_requirements`: Standard requirements
- `minimal_requirements`: Minimum required fields
- `sample_conversation`: Manufacturing conversation
- `unrelated_conversation`: Non-manufacturing conversation
- `jeans_factory`: Jeans-specific factory
- `jeans_requirements`: Jeans-specific requirements

## Coverage Goals

| Component | Target | Status |
|-----------|--------|--------|
| factories.py | 90%+ | ✅ |
| requirements.py | 100% | ✅ |
| llm.py | 80%+ | ✅ |
| actions.py | 80%+ | ✅ |
| Integration | 70%+ | ✅ |

## Test Scenarios Covered

### Happy Path
- ✅ User provides complete requirements
- ✅ System finds matching factories
- ✅ Top 3 factories recommended with reasoning
- ✅ RFQ generated successfully

### Edge Cases
- ✅ No factories match requirements
- ✅ Only partial matches available
- ✅ User MOQ below factory minimum
- ✅ Empty materials/certifications lists
- ✅ None/null values in requirements
- ✅ Very high or very low MOQ
- ✅ Case-insensitive geography matching

### Error Handling
- ✅ Non-manufacturing conversation input
- ✅ Invalid data types
- ✅ Missing required fields
- ✅ Malformed data
- ✅ Database loading errors

### Data Validation
- ✅ Factory database integrity
- ✅ Unique factory IDs
- ✅ Valid cost tiers
- ✅ Positive MOQ values
- ✅ Required field presence
- ✅ Correct data types

## Continuous Integration

To run tests in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=src --cov-report=xml
```

## Troubleshooting

### Tests Failing Due to Missing Dependencies
```bash
pip install -r requirements.txt
```

### Tests Failing Due to Missing API Key
Set the OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=your-key-here
```

Or skip LLM tests:
```bash
pytest -m "not llm"
```

### Import Errors
Make sure you're running from the project root:
```bash
cd /path/to/glass-factory
pytest
```

### Module Not Found
Install in development mode:
```bash
pip install -e .
```

## Adding New Tests

1. Create test file in `tests/` directory with `test_` prefix
2. Use test classes with `Test` prefix
3. Use test methods with `test_` prefix
4. Use fixtures from `conftest.py` or create new ones
5. Add appropriate markers (`@pytest.mark.llm`, etc.)
6. Update this documentation

Example:
```python
import pytest
from conftest import sample_factory

class TestNewFeature:
    def test_new_functionality(self, sample_factory):
        # Arrange
        ...
        
        # Act
        ...
        
        # Assert
        assert result == expected
```
