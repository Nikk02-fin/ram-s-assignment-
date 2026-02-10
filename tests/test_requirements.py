import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.requirements import ManufacturingRequirements
import pytest
from pydantic import ValidationError


class TestRequirementsModel:
    """Test ManufacturingRequirements data model"""
    
    def test_create_valid_requirements(self):
        """Test creating requirements with valid data"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            product_description="kitchen organizers",
            materials=["plastic", "metal"],
            moq=1000,
            geography="China",
            certifications=["ISO9001"],
            budget_tier="low"
        )
        
        assert req.product_type == "consumer_goods"
        assert req.product_description == "kitchen organizers"
        assert req.materials == ["plastic", "metal"]
        assert req.moq == 1000
        assert req.geography == "China"
        assert req.certifications == ["ISO9001"]
        assert req.budget_tier == "low"
    
    def test_product_description_field(self):
        """Test product_description field"""
        # With product description
        req1 = ManufacturingRequirements(
            product_type="apparel",
            product_description="winter jackets",
            materials=["cotton"],
            moq=500
        )
        assert req1.product_description == "winter jackets"
        
        # Without product description (should default to None)
        req2 = ManufacturingRequirements(
            product_type="electronics",
            materials=["plastic"],
            moq=1000
        )
        assert req2.product_description is None
    
    def test_create_with_minimal_fields(self):
        """Test creating requirements with only required fields"""
        req = ManufacturingRequirements(
            product_type="electronics",
            materials=["plastic"],
            moq=500
        )
        
        assert req.product_type == "electronics"
        assert req.materials == ["plastic"]
        assert req.moq == 500
        assert req.geography is None
        assert req.certifications == []
        assert req.budget_tier is None
    
    def test_optional_fields_default_values(self):
        """Test that optional fields have correct defaults"""
        req = ManufacturingRequirements(
            product_type="apparel",
            moq=1000
        )
        
        assert req.geography is None
        assert req.budget_tier is None
        assert req.certifications == []
        assert req.materials == []
    
    def test_invalid_moq_type(self):
        """Test that non-integer MOQ raises error"""
        with pytest.raises(ValidationError):
            ManufacturingRequirements(
                product_type="consumer_goods",
                materials=["plastic"],
                moq="not a number"  # Should be int
            )
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise error"""
        with pytest.raises(ValidationError):
            ManufacturingRequirements(
                materials=["plastic"],
                moq=1000
                # Missing product_type
            )
    
    def test_empty_lists_allowed(self):
        """Test that empty lists are valid for list fields"""
        req = ManufacturingRequirements(
            product_type="industrial",
            materials=[],
            moq=100,
            certifications=[]
        )
        
        assert req.materials == []
        assert req.certifications == []
    
    def test_materials_as_list(self):
        """Test materials field accepts list"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic", "metal", "abs"],
            moq=1000
        )
        
        assert isinstance(req.materials, list)
        assert len(req.materials) == 3
    
    def test_certifications_as_list(self):
        """Test certifications field accepts list"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            certifications=["ISO9001", "BSCI", "CE"]
        )
        
        assert isinstance(req.certifications, list)
        assert len(req.certifications) == 3
    
    def test_moq_edge_cases(self):
        """Test MOQ with edge case values"""
        # Very small MOQ
        req1 = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1
        )
        assert req1.moq == 1
        
        # Very large MOQ
        req2 = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000000
        )
        assert req2.moq == 1000000
    
    def test_serialization(self):
        """Test that requirements can be serialized to dict"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="Vietnam",
            certifications=["ISO9001"],
            budget_tier="medium"
        )
        
        data = req.model_dump()  # Pydantic v2
        
        assert isinstance(data, dict)
        assert data["product_type"] == "consumer_goods"
        assert data["materials"] == ["plastic"]
        assert data["moq"] == 1000
    
    def test_geography_variations(self):
        """Test various geography inputs"""
        geographies = ["China", "Vietnam", "Bangladesh", "India", "Europe", None]
        
        for geo in geographies:
            req = ManufacturingRequirements(
                product_type="consumer_goods",
                materials=["plastic"],
                moq=1000,
                geography=geo
            )
            assert req.geography == geo
    
    def test_budget_tier_variations(self):
        """Test various budget tier inputs"""
        tiers = ["low", "medium", "high", None]
        
        for tier in tiers:
            req = ManufacturingRequirements(
                product_type="consumer_goods",
                materials=["plastic"],
                moq=1000,
                budget_tier=tier
            )
            assert req.budget_tier == tier
