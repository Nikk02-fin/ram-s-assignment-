"""
Pytest configuration and shared fixtures
"""
import sys
import os
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_factory():
    """Sample factory data for testing"""
    return {
        "id": "TEST001",
        "name": "Test Manufacturing Co",
        "product_types": ["consumer_goods", "electronics"],
        "materials": ["plastic", "metal"],
        "moq_min": 1000,
        "geography": "China",
        "certifications": ["ISO9001", "CE"],
        "cost_tier": "medium"
    }


@pytest.fixture
def sample_requirements():
    """Sample requirements for testing"""
    from model.requirements import ManufacturingRequirements
    
    return ManufacturingRequirements(
        product_type="consumer_goods",
        product_description="kitchen organizers",
        materials=["plastic"],
        moq=1500,
        geography="China",
        certifications=["ISO9001"],
        budget_tier="medium"
    )


@pytest.fixture
def minimal_requirements():
    """Minimal requirements with only required fields"""
    from model.requirements import ManufacturingRequirements
    
    return ManufacturingRequirements(
        product_type="electronics",
        materials=["plastic"],
        moq=500
    )


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing extraction"""
    return """
    User: I need to manufacture plastic kitchen organizers
    AI: How many units do you need?
    User: Around 1000 units
    AI: Where would you like them manufactured?
    User: Vietnam would be great
    AI: What certifications do you need?
    User: ISO9001 and looking for medium budget
    """


@pytest.fixture
def unrelated_conversation():
    """Conversation not about manufacturing"""
    return """
    User: What's the weather like today?
    AI: I don't have access to weather information.
    User: Can you tell me a joke?
    AI: Why don't scientists trust atoms? Because they make up everything!
    """


@pytest.fixture
def jeans_factory():
    """Factory specialized in jeans manufacturing"""
    return {
        "id": "JEANS001",
        "name": "Denim Masters Ltd",
        "product_types": ["jeans", "apparel"],
        "materials": ["denim", "cotton"],
        "moq_min": 2000,
        "geography": "Bangladesh",
        "certifications": ["BSCI", "ISO9001"],
        "cost_tier": "low"
    }


@pytest.fixture
def jeans_requirements():
    """Requirements for jeans manufacturing"""
    from model.requirements import ManufacturingRequirements
    
    return ManufacturingRequirements(
        product_type="jeans",
        product_description="denim jeans",
        materials=["denim"],
        moq=2500,
        geography="Bangladesh",
        certifications=["BSCI"],
        budget_tier="low"
    )


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "llm: mark test as requiring LLM API"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
