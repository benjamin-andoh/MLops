import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from features import FeatureBuilder

class TestFeatureBuilder:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.feature_builder = FeatureBuilder()
        
        # Sample transaction data
        self.sample_data = pd.DataFrame({
            'amount': [100.0, 50.0, 200.0, 25.0],
            'timestamp': ['2023-01-01 10:00:00', '2023-01-01 14:00:00', 
                         '2023-01-01 22:00:00', '2023-01-02 08:00:00'],
            'customer_id': [1, 2, 1, 1],
            'merchant_category': ['grocery', 'gas', 'restaurant', 'grocery']
        })
        
    def test_build_features_basic(self):
        """Test basic feature building functionality."""
        features = self.feature_builder.build_features(self.sample_data.iloc[0])
        
        assert isinstance(features, dict)
        assert 'amount' in features
        assert 'hour_of_day' in features
        assert 'day_of_week' in features
        
    def test_build_features_with_history(self):
        """Test feature building with transaction history."""
        # Mock historical data
        with patch.object(self.feature_builder, 'get_customer_history') as mock_history:
            mock_history.return_value = self.sample_data[self.sample_data['customer_id'] == 1]
            
            features = self.feature_builder.build_features(self.sample_data.iloc[0])
            
            assert 'avg_monthly_spend' in features
            assert 'customer_tenure_days' in features
            assert 'num_prev_tx_24h' in features
            
    def test_hour_of_day_extraction(self):
        """Test hour of day extraction from timestamp."""
        test_row = pd.Series({
            'timestamp': '2023-01-01 15:30:00',
            'amount': 100.0
        })
        
        features = self.feature_builder.build_features(test_row)
        assert features['hour_of_day'] == 15
        
    def test_day_of_week_extraction(self):
        """Test day of week extraction from timestamp."""
        test_row = pd.Series({
            'timestamp': '2023-01-01 15:30:00',  # Sunday = 6
            'amount': 100.0
        })
        
        features = self.feature_builder.build_features(test_row)
        assert features['day_of_week'] == 6
        
    def test_feature_values_are_numeric(self):
        """Test that all feature values are numeric."""
        features = self.feature_builder.build_features(self.sample_data.iloc[0])
        
        for key, value in features.items():
            assert isinstance(value, (int, float, np.number)), f"Feature {key} is not numeric: {type(value)}"
            
    def test_missing_data_handling(self):
        """Test handling of missing data."""
        test_row = pd.Series({
            'amount': None,
            'timestamp': '2023-01-01 15:30:00'
        })
        
        # Should not raise an exception
        features = self.feature_builder.build_features(test_row)
        assert isinstance(features, dict)


if __name__ == "__main__":
    pytest.main([__file__])