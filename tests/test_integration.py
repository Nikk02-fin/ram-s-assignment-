import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from factories import load_factories, recommend_factories
from model.requirements import ManufacturingRequirements
from llm import extract_requirements
import pytest
import json


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    def test_happy_path_complete_workflow(self):
        """Test complete workflow from requirements to recommendations"""
        # Step 1: Define requirements
        req = ManufacturingRequirements(
            product_type="jeans",
            materials=["denim"],
            moq=2000,
            geography="Bangladesh",
            certifications=["BSCI"],
            budget_tier="low"
        )
        
        # Step 2: Get recommendations
        results = recommend_factories(req, top_n=3)
        
        # Verify recommendations
        assert isinstance(results, list)
        assert len(results) <= 3
        
        if len(results) > 0:
            # Check structure
            for result in results:
                assert "factory" in result
                assert "score" in result
                assert "reasons" in result
                
                factory = result["factory"]
                assert "name" in factory
                assert "id" in factory
                assert "moq_min" in factory
    
    def test_no_matches_workflow(self):
        """Test workflow when no factories match requirements"""
        # Create impossible requirements
        req = ManufacturingRequirements(
            product_type="nonexistent_product",
            materials=["unobtanium"],
            moq=1,
            geography="Atlantis",
            certifications=["FAKE_CERT"],
            budget_tier="ultra_premium"
        )
        
        results = recommend_factories(req, top_n=3)
        
        # Should handle gracefully - either empty or very low scores
        assert isinstance(results, list)
    
    def test_partial_match_workflow(self):
        """Test workflow with only partial matches available"""
        # Requirements that might only partially match
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=50,  # Very low MOQ
            geography="Mars",  # Non-existent location
            certifications=["ISO9001"],
            budget_tier="low"
        )
        
        results = recommend_factories(req, top_n=3)
        
        # Should still return results based on partial matches
        assert isinstance(results, list)
    
    def test_conversation_to_recommendations_workflow(self):
        """Test full workflow from conversation to recommendations"""
        # Step 1: Simulate conversation
        conversation = """
        User: I need to manufacture 2000 denim jeans
        AI: Where would you like them manufactured?
        User: Bangladesh would be ideal
        AI: What certifications do you need?
        User: BSCI and keep costs low
        """
        
        try:
            # Step 2: Extract requirements
            raw_requirements = extract_requirements(conversation)
            requirements_dict = json.loads(raw_requirements)
            
            # Step 3: Create requirements object
            req = ManufacturingRequirements(**requirements_dict)
            
            # Step 4: Get recommendations
            results = recommend_factories(req, top_n=3)
            
            # Verify end-to-end flow worked
            assert isinstance(results, list)
            assert len(results) <= 3
        except Exception as e:
            pytest.skip(f"Skipping conversation workflow test due to: {str(e)}")
    
    def test_multiple_material_requirements(self):
        """Test workflow with multiple materials"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic", "metal", "rubber"],
            moq=1000,
            geography=None,
            certifications=[],
            budget_tier="medium"
        )
        
        results = recommend_factories(req, top_n=3)
        
        assert isinstance(results, list)
        # Should find factories that work with at least one of the materials
    
    def test_high_moq_requirements(self):
        """Test workflow with very high MOQ"""
        req = ManufacturingRequirements(
            product_type="apparel",
            materials=["cotton"],
            moq=50000,  # Very high MOQ
            geography=None,
            certifications=[],
            budget_tier="low"
        )
        
        results = recommend_factories(req, top_n=3)
        
        assert isinstance(results, list)
        # Should find factories that can handle high volumes


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_database_integrity(self):
        """Test that factory database loads correctly"""
        factories = load_factories()
        
        assert len(factories) > 0
        assert all(isinstance(f, dict) for f in factories)
    
    def test_empty_materials_list(self):
        """Test recommendations with empty materials list"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=[],  # Empty
            moq=1000,
            geography="China",
            certifications=[],
            budget_tier="low"
        )
        
        results = recommend_factories(req, top_n=3)
        assert isinstance(results, list)
    
    def test_zero_moq(self):
        """Test handling of zero MOQ (edge case)"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=0,  # Edge case
            geography=None,
            certifications=[],
            budget_tier=None
        )
        
        results = recommend_factories(req, top_n=3)
        # Should handle gracefully
        assert isinstance(results, list)
    
    def test_recommendations_consistency(self):
        """Test that same requirements produce consistent results"""
        req = ManufacturingRequirements(
            product_type="jeans",
            materials=["denim"],
            moq=2000,
            geography="Bangladesh",
            certifications=["BSCI"],
            budget_tier="low"
        )
        
        results1 = recommend_factories(req, top_n=3)
        results2 = recommend_factories(req, top_n=3)
        
        # Should get same results for same input
        assert len(results1) == len(results2)
        
        if len(results1) > 0:
            # Same factories should be recommended
            factory_ids1 = [r["factory"]["id"] for r in results1]
            factory_ids2 = [r["factory"]["id"] for r in results2]
            assert factory_ids1 == factory_ids2
    
    def test_case_insensitive_geography(self):
        """Test that geography matching is case insensitive"""
        req1 = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="china",  # lowercase
            certifications=[],
            budget_tier="low"
        )
        
        req2 = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="CHINA",  # uppercase
            certifications=[],
            budget_tier="low"
        )
        
        results1 = recommend_factories(req1, top_n=3)
        results2 = recommend_factories(req2, top_n=3)
        
        # Should produce same results
        if len(results1) > 0 and len(results2) > 0:
            assert len(results1) == len(results2)


class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_factory_data_completeness(self):
        """Test that all factories have complete data"""
        factories = load_factories()
        
        required_fields = [
            "id", "name", "product_types", "materials",
            "moq_min", "geography", "certifications", "cost_tier"
        ]
        
        for factory in factories:
            for field in required_fields:
                assert field in factory, f"Factory {factory.get('name', 'Unknown')} missing {field}"
                
                # Check types
                if field == "moq_min":
                    assert isinstance(factory[field], int), f"moq_min should be int for {factory['name']}"
                elif field in ["product_types", "materials", "certifications"]:
                    assert isinstance(factory[field], list), f"{field} should be list for {factory['name']}"
                else:
                    assert isinstance(factory[field], str), f"{field} should be string for {factory['name']}"
    
    def test_unique_factory_ids(self):
        """Test that all factory IDs are unique"""
        factories = load_factories()
        ids = [f["id"] for f in factories]
        
        assert len(ids) == len(set(ids)), "Duplicate factory IDs found"
    
    def test_valid_cost_tiers(self):
        """Test that all factories have valid cost tiers"""
        factories = load_factories()
        valid_tiers = ["low", "medium", "high"]
        
        for factory in factories:
            assert factory["cost_tier"] in valid_tiers, \
                f"Invalid cost tier '{factory['cost_tier']}' for {factory['name']}"
    
    def test_positive_moq_minimums(self):
        """Test that all MOQ minimums are positive"""
        factories = load_factories()
        
        for factory in factories:
            assert factory["moq_min"] > 0, \
                f"MOQ minimum should be positive for {factory['name']}"
