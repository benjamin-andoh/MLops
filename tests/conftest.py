# Test configuration file
import os
import sys

# Add src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test configuration
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'run_local')

# Create test fixtures directory if it doesn't exist
os.makedirs(TEST_DATA_PATH, exist_ok=True)