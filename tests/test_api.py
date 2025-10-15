import pytest
import requests
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from serve import app
from fastapi.testclient import TestClient

class TestAPI:
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
        
        # Sample request data
        self.valid_request = {
            "features": {
                "amount": 100.0,
                "hour_of_day": 14,
                "day_of_week": 1,
                "avg_monthly_spend": 500.0,
                "customer_tenure_days": 365,
                "num_prev_tx_24h": 3
            }
        }
        
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        
    def test_predict_endpoint_valid_input(self):
        """Test prediction endpoint with valid input."""
        with patch('serve.model') as mock_model, \
             patch('serve.scaler') as mock_scaler, \
             patch('serve.feature_builder') as mock_fb:
            
            # Mock the model and scaler
            mock_scaler.transform.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]]
            mock_model.predict_proba.return_value = [[0.7, 0.3]]
            mock_fb.build_features.return_value = self.valid_request["features"]
            
            response = self.client.post("/predict", json=self.valid_request)
            
            assert response.status_code == 200
            result = response.json()
            assert "fraud_probability" in result
            assert "is_fraud" in result
            assert isinstance(result["fraud_probability"], float)
            assert isinstance(result["is_fraud"], bool)
            
    def test_predict_endpoint_invalid_input(self):
        """Test prediction endpoint with invalid input."""
        invalid_request = {"invalid": "data"}
        
        response = self.client.post("/predict", json=invalid_request)
        assert response.status_code == 422  # Validation error
        
    def test_predict_endpoint_missing_features(self):
        """Test prediction endpoint with missing features."""
        incomplete_request = {
            "features": {
                "amount": 100.0,
                # Missing other required features
            }
        }
        
        response = self.client.post("/predict", json=incomplete_request)
        # Should still work if feature builder handles missing features
        assert response.status_code in [200, 422]
        
    def test_model_prediction_range(self):
        """Test that model predictions are in valid range."""
        with patch('serve.model') as mock_model, \
             patch('serve.scaler') as mock_scaler, \
             patch('serve.feature_builder') as mock_fb:
            
            mock_scaler.transform.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]]
            mock_model.predict_proba.return_value = [[0.8, 0.2]]
            mock_fb.build_features.return_value = self.valid_request["features"]
            
            response = self.client.post("/predict", json=self.valid_request)
            result = response.json()
            
            # Probability should be between 0 and 1
            assert 0.0 <= result["fraud_probability"] <= 1.0
            
    def test_prediction_consistency(self):
        """Test that same input gives same output."""
        with patch('serve.model') as mock_model, \
             patch('serve.scaler') as mock_scaler, \
             patch('serve.feature_builder') as mock_fb:
            
            mock_scaler.transform.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]]
            mock_model.predict_proba.return_value = [[0.6, 0.4]]
            mock_fb.build_features.return_value = self.valid_request["features"]
            
            response1 = self.client.post("/predict", json=self.valid_request)
            response2 = self.client.post("/predict", json=self.valid_request)
            
            assert response1.json() == response2.json()


if __name__ == "__main__":
    pytest.main([__file__])