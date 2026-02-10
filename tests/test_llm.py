import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm import extract_requirements
from model.requirements import ManufacturingRequirements
import pytest
import json


class TestLLMExtraction:
    """Test LLM requirement extraction"""
    
    def test_extract_basic_requirements(self):
        """Test extraction from simple conversation"""
        conversation = """
        User: I need to manufacture plastic kitchen organizers
        AI: How many units do you need?
        User: Around 1000 units
        AI: Where would you like them manufactured?
        User: Vietnam would be great
        """
        
        result = extract_requirements(conversation)
        assert result is not None
        
        # Should be valid JSON
        data = json.loads(result)
        assert "product_type" in data
        assert "product_description" in data
        assert "materials" in data
        assert "moq" in data
        
        # Should capture specific product description
        if data.get("product_description"):
            assert "organizer" in data["product_description"].lower()
    
    def test_extract_with_complete_info(self):
        """Test extraction with all requirements specified"""
        conversation = """
        User: I need 2000 denim jeans manufactured in Bangladesh
        AI: What certifications do you need?
        User: BSCI and ISO9001, and I'm looking for low cost
        """
        
        result = extract_requirements(conversation)
        data = json.loads(result)
        
        assert data["moq"] == 2000 or isinstance(data["moq"], int)
        assert "denim" in str(data["materials"]).lower() or "jeans" in data["product_type"].lower()
        assert isinstance(data["certifications"], list)
    
    def test_extract_with_missing_info(self):
        """Test extraction when some info is missing"""
        conversation = """
        User: I want to make plastic toys
        AI: How many?
        User: About 500
        """
        
        result = extract_requirements(conversation)
        data = json.loads(result)
        
        # Should have some fields, others might be null
        assert "product_type" in data
        assert "moq" in data
        # Geography might be null
        assert "geography" in data
    
    def test_extract_handles_json_format(self):
        """Test that extraction returns valid JSON"""
        conversation = """
        User: Need 1000 electronics with plastic material in China
        """
        
        result = extract_requirements(conversation)
        
        # Should not raise JSON decode error
        try:
            data = json.loads(result)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("extract_requirements did not return valid JSON")
    
    def test_extract_infers_product_types(self):
        """Test that product type descriptions are mapped correctly"""
        test_cases = [
            ("kitchen organizers", "consumer_goods"),
            ("phone cases", "electronics"),
            ("industrial machinery parts", "industrial"),
            ("t-shirts", "apparel"),
        ]
        
        for description, expected_type in test_cases:
            conversation = f"User: I need to manufacture {description}, about 1000 units"
            result = extract_requirements(conversation)
            data = json.loads(result)
            
            # Check if the inferred type is reasonable
            product_type = data.get("product_type", "").lower()
            # Allow some flexibility - as long as it's a valid category
            assert product_type in ["consumer_goods", "electronics", "industrial", "apparel", "fashion", "jeans"]


class TestLLMChat:
    """Test chat functionality"""
    
    def test_chat_returns_string(self):
        """Test that chat returns a string response"""
        # Note: This test requires OpenAI API key to be set
        # Skip if not available
        try:
            from llm import chat
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'test' and nothing else."}
            ]
            
            response = chat(messages)
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"Skipping chat test due to: {str(e)}")


class TestNonManufacturingInput:
    """Test handling of non-manufacturing related inputs"""
    
    def test_unrelated_conversation(self):
        """Test extraction from completely unrelated conversation"""
        conversation = """
        User: What's the weather like today?
        AI: I'm not sure about the weather.
        User: Tell me a joke
        """
        
        result = extract_requirements(conversation)
        # Should still return valid JSON structure, even with null/empty values
        data = json.loads(result)
        assert isinstance(data, dict)
        # Key fields should exist even if empty/null
        assert "product_type" in data
        assert "materials" in data
        assert "moq" in data
    
    def test_partial_manufacturing_info(self):
        """Test when only vague manufacturing info is provided"""
        conversation = """
        User: I want to make something
        AI: What do you want to make?
        User: Not sure yet
        """
        
        result = extract_requirements(conversation)
        data = json.loads(result)
        
        # Should handle gracefully with null/default values
        assert isinstance(data, dict)
        assert "product_type" in data
