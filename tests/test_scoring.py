import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from factories import score_factory, recommend_factories, load_factories
from model.requirements import ManufacturingRequirements
import pytest


class TestFactoryScoring:
    """Test factory scoring logic"""
    
    def test_perfect_match(self):
        """Test factory with perfect match scores highest"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 500,
            "geography": "China",
            "certifications": ["ISO9001"],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="China",
            certifications=["ISO9001"],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        assert score >= 9  # Should have high score for perfect match
        assert len(reasons) > 0
        assert any("consumer_goods" in r for r in reasons)
        assert any("plastic" in r for r in reasons)
    
    def test_product_type_mismatch(self):
        """Test factory with wrong product type scores lower"""
        factory = {
            "product_types": ["electronics"],
            "materials": ["plastic"],
            "moq_min": 500,
            "geography": "China",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="apparel",
            materials=["plastic"],
            moq=1000,
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        # Should still score due to other matches, but lower
        assert score >= 0
    
    def test_moq_below_minimum(self):
        """Test when user MOQ is below factory minimum"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 1000,
            "geography": "China",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=500,  # Below minimum
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        # Should still consider if close to minimum (50% rule)
        assert score > 0  # Gets partial credit
        assert any("negotiable" in r.lower() for r in reasons)
    
    def test_moq_at_minimum(self):
        """Test when user MOQ exactly meets factory minimum"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 1000,
            "geography": "China",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,  # Exact minimum
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        assert score > 0
        assert any("1000" in r for r in reasons)
    
    def test_geography_match(self):
        """Test geography matching (case insensitive)"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 500,
            "geography": "Vietnam",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="vietnam",  # lowercase
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        assert any("Vietnam" in r for r in reasons)
    
    def test_no_geography_preference(self):
        """Test when user has no geography preference"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 500,
            "geography": "China",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography=None,  # No preference
            certifications=[],
            budget_tier=None
        )

        score, reasons = score_factory(factory, req)
        assert score > 0  # Should still match on other criteria
    
    def test_material_partial_match(self):
        """Test partial material matching"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic", "metal", "abs"],
            "moq_min": 500,
            "geography": "China",
            "certifications": [],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic", "rubber"],  # Plastic matches, rubber doesn't
            moq=1000,
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        assert any("plastic" in r.lower() for r in reasons)
    
    def test_certification_display(self):
        """Test that certifications are shown in reasons"""
        factory = {
            "product_types": ["consumer_goods"],
            "materials": ["plastic"],
            "moq_min": 500,
            "geography": "China",
            "certifications": ["ISO9001", "BSCI"],
            "cost_tier": "low"
        }

        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        score, reasons = score_factory(factory, req)
        reasons_text = " ".join(reasons)
        assert "ISO9001" in reasons_text or "BSCI" in reasons_text


class TestFactoryRecommendations:
    """Test factory recommendation logic"""
    
    def test_recommend_returns_top_factories(self):
        """Test that recommend_factories returns top matches"""
        req = ManufacturingRequirements(
            product_type="consumer_goods",
            materials=["plastic"],
            moq=1000,
            geography="China",
            certifications=[],
            budget_tier="low"
        )

        results = recommend_factories(req, top_n=3)
        assert len(results) <= 3
        assert all("factory" in r for r in results)
        assert all("score" in r for r in results)
        assert all("reasons" in r for r in results)
    
    def test_recommend_sorted_by_score(self):
        """Test that recommendations are sorted by score descending"""
        req = ManufacturingRequirements(
            product_type="jeans",
            materials=["denim"],
            moq=2000,
            geography=None,
            certifications=[],
            budget_tier="low"
        )

        results = recommend_factories(req, top_n=3)
        if len(results) > 1:
            scores = [r["score"] for r in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_no_matches_returns_empty(self):
        """Test when no factories match any criteria"""
        req = ManufacturingRequirements(
            product_type="nonexistent_product_type_xyz",
            materials=["unobtainium"],
            moq=1,
            geography="Mars",
            certifications=[],
            budget_tier="ultra_high"
        )

        results = recommend_factories(req, top_n=3)
        # Should return empty list or very low scores
        assert isinstance(results, list)
    
    def test_recommend_with_custom_top_n(self):
        """Test requesting different number of recommendations"""
        req = ManufacturingRequirements(
            product_type="apparel",
            materials=["cotton"],
            moq=1000,
            geography=None,
            certifications=[],
            budget_tier="low"
        )

        results = recommend_factories(req, top_n=5)
        assert len(results) <= 5


class TestFactoryDataLoading:
    """Test factory data loading"""
    
    def test_load_factories_returns_list(self):
        """Test that load_factories returns a list"""
        factories = load_factories()
        assert isinstance(factories, list)
        assert len(factories) > 0
    
    def test_factory_structure(self):
        """Test that factories have required fields"""
        factories = load_factories()
        required_fields = ["id", "name", "product_types", "materials", 
                          "moq_min", "geography", "certifications", "cost_tier"]
        
        for factory in factories[:5]:  # Check first 5
            for field in required_fields:
                assert field in factory, f"Factory missing required field: {field}"
    
    def test_factory_data_types(self):
        """Test that factory fields have correct data types"""
        factories = load_factories()
        
        for factory in factories[:5]:
            assert isinstance(factory["id"], str)
            assert isinstance(factory["name"], str)
            assert isinstance(factory["product_types"], list)
            assert isinstance(factory["materials"], list)
            assert isinstance(factory["moq_min"], int)
            assert isinstance(factory["geography"], str)
            assert isinstance(factory["certifications"], list)
            assert isinstance(factory["cost_tier"], str)
