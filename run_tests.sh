#!/bin/bash

# Test runner script for Glass Factory

echo "🧪 Glass Factory Test Suite"
echo "============================"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Parse arguments
ARGS="$@"

if [ -z "$ARGS" ]; then
    echo "Running all tests..."
    python3 -m pytest tests/ -v
elif [ "$ARGS" = "coverage" ]; then
    echo "Running tests with coverage report..."
    python3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
elif [ "$ARGS" = "fast" ]; then
    echo "Running fast tests (skipping LLM tests)..."
    python3 -m pytest tests/ -v -m "not llm"
elif [ "$ARGS" = "integration" ]; then
    echo "Running integration tests..."
    python3 -m pytest tests/test_integration.py -v
elif [ "$ARGS" = "scoring" ]; then
    echo "Running scoring tests..."
    python3 -m pytest tests/test_scoring.py -v
elif [ "$ARGS" = "llm" ]; then
    echo "Running LLM tests..."
    python3 -m pytest tests/test_llm.py -v
elif [ "$ARGS" = "actions" ]; then
    echo "Running action tests..."
    python3 -m pytest tests/test_actions.py -v
elif [ "$ARGS" = "requirements" ]; then
    echo "Running requirements tests..."
    python3 -m pytest tests/test_requirements.py -v
else
    echo "Running tests with custom arguments: $ARGS"
    python3 -m pytest tests/ $ARGS
fi

exit $?
