# Glass Factory

AI-powered manufacturing concierge that helps you find the perfect factory for your product.

## Setup

1. **Create virtual environment and install dependencies:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Run the application:**
```bash
streamlit run src/app.py
```

## How It Works

1. **Conversational Interface**: Chat with the AI to describe your manufacturing needs
2. **Smart Requirements Gathering**: The AI asks follow-up questions to collect all necessary details
3. **Automatic Recommendations**: Once enough information is gathered, the system suggests matching factories
4. **RFQ Generation**: Generate professional Request for Quote emails for selected factories

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_scoring.py
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

### Test Structure

The test suite includes comprehensive coverage:

- **`test_scoring.py`**: Factory scoring and recommendation logic
  - Perfect match scenarios
  - Partial matches
  - MOQ edge cases
  - Geography matching
  - Material compatibility

- **`test_requirements.py`**: Requirements data model validation
  - Valid data structures
  - Required vs optional fields
  - Data type validation
  - Edge cases

- **`test_llm.py`**: LLM extraction and chat functionality
  - Requirement extraction from conversations
  - Handling missing information
  - Non-manufacturing input handling
  - JSON format validation

- **`test_actions.py`**: RFQ email generation
  - Professional format validation
  - Content inclusion tests
  - Edge case handling

- **`test_integration.py`**: End-to-end workflows
  - Happy path testing
  - No matches scenario
  - Partial matches
  - Data validation

### Test Coverage

The tests cover:
- ✅ Happy path workflows
- ✅ Edge cases (zero MOQ, empty lists, None values)
- ✅ Error handling (invalid data, missing fields)
- ✅ Non-manufacturing input handling
- ✅ No factory matches scenario
- ✅ Data validation and integrity
- ✅ Case-insensitive matching
- ✅ Multiple materials and certifications

### Notes on LLM Tests

Tests marked with `@pytest.mark.llm` require an OpenAI API key. These tests will be skipped if:
- No API key is set in `.env`
- API is unavailable
- Rate limits are reached

Run only non-LLM tests:
```bash
pytest -m "not llm"
```

## Project Structure

```
glass-factory/
├── src/                          # Source code
│   ├── app.py                   # Streamlit application (main entry point)
│   ├── llm.py                   # LLM chat and requirement extraction
│   ├── factories.py             # Factory scoring and recommendation logic
│   ├── actions.py               # RFQ email generation
│   └── model/
│       └── requirements.py      # ManufacturingRequirements data model
├── data/
│   └── factories.json           # Factory database (50 manufacturers mock data)
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Shared test fixtures
│   ├── test_scoring.py          # Factory scoring tests
│   ├── test_requirements.py     # Data model tests
│   ├── test_llm.py              # LLM extraction tests
│   ├── test_actions.py          # RFQ generation tests
│   ├── test_integration.py      # End-to-end workflow tests
│   └── README.md                # Test documentation
├── .env                          # Environment variables (API keys)
├── .gitignore                   # Git ignore rules
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
├── run_tests.sh                 # Test runner script
└── README.md                    # This file
```
