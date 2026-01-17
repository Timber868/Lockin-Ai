"""Tests for preprocessing modules."""

import unittest
import numpy as np
from focusai.preprocess.processor import FramePreprocessor, create_preprocessor
from focusai.preprocess.features import FeatureExtractor, create_feature_extractor
from focusai.config import PreprocessConfig
from focusai.models import Frame


class TestFramePreprocessor(unittest.TestCase):
    """Test cases for FramePreprocessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PreprocessConfig(
            target_size=(224, 224),
            normalize=True
        )
        self.preprocessor = create_preprocessor(self.config)
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        self.assertIsNotNone(self.preprocessor)
        self.assertEqual(self.preprocessor.config.target_size, (224, 224))
    
    # TODO: Add tests for resize, normalize, face extraction


class TestFeatureExtractor(unittest.TestCase):
    """Test cases for FeatureExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PreprocessConfig(feature_extraction_method="basic")
        self.extractor = create_feature_extractor(self.config)
    
    def test_initialization(self):
        """Test feature extractor initialization."""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.method, "basic")
    
    # TODO: Add tests for feature extraction methods


if __name__ == "__main__":
    unittest.main()
