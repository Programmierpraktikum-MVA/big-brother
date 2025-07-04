"""
OCR implementation using Keras/TensorFlow and EasyOCR with German language support.

This module provides OCR functionality with support for German special characters
and integrates both custom TensorFlow-based OCR models and EasyOCR backend.
"""

import cv2
import numpy as np
from PIL import Image
import os
from typing import List, Tuple, Optional, Union

# Optional imports for different backends
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    tf = None
    keras = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None


class KerasOCR:
    """
    OCR class that supports both custom Keras/TensorFlow models and EasyOCR backend
    with enhanced support for German language and special characters.
    
    This class provides:
    - Custom TensorFlow-based OCR model with German character support
    - EasyOCR backend integration with German language
    - Character set including German umlauts and eszett
    
    Usage:
    ```python
    # Initialize with both backends
    ocr = KerasOCR(use_easyocr=True, use_keras_model=True)
    
    # Extract text from image
    text = ocr.extract_text(image_path)
    ```
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 use_easyocr: bool = True,
                 use_keras_model: bool = False,
                 languages: List[str] = ['de', 'en']):
        """
        Initialize the KerasOCR instance.
        
        Args:
            model_path: Path to the trained Keras OCR model (optional)
            use_easyocr: Whether to use EasyOCR backend
            use_keras_model: Whether to use custom Keras model
            languages: List of language codes for OCR recognition
        """
        self.model_path = model_path
        self.use_easyocr = use_easyocr
        self.use_keras_model = use_keras_model
        self.languages = languages
        
        # Extended character set with German special characters
        self.characters = [
            ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
            # German special characters (umlauts and eszett)
            'ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß'
        ]
        
        # Create character-to-index mapping
        self.char_to_idx = {char: idx for idx, char in enumerate(self.characters)}
        self.idx_to_char = {idx: char for idx, char in enumerate(self.characters)}
        
        # Initialize backends
        self.easyocr_reader = None
        self.keras_model = None
        
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize the OCR backends based on configuration."""
        
        # Initialize EasyOCR with German language support
        if self.use_easyocr:
            if not EASYOCR_AVAILABLE:
                print("Warning: EasyOCR not available. Install with: pip install easyocr")
                self.use_easyocr = False
            else:
                try:
                    self.easyocr_reader = easyocr.Reader(self.languages)
                    print(f"EasyOCR initialized with languages: {self.languages}")
                except Exception as e:
                    print(f"Warning: Failed to initialize EasyOCR: {e}")
                    self.use_easyocr = False
        
        # Initialize custom Keras model
        if self.use_keras_model:
            if not TF_AVAILABLE:
                print("Warning: TensorFlow not available. Install with: pip install tensorflow")
                self.use_keras_model = False
            elif self.model_path and os.path.exists(self.model_path):
                try:
                    self.keras_model = keras.models.load_model(self.model_path)
                    print(f"Keras OCR model loaded from: {self.model_path}")
                except Exception as e:
                    print(f"Warning: Failed to load Keras model: {e}")
                    self.use_keras_model = False
            else:
                print("Warning: No valid model path provided for Keras backend")
                self.use_keras_model = False
    
    def preprocess_image(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Preprocess image for OCR.
        
        Args:
            image: Input image (file path, numpy array, or PIL Image)
            
        Returns:
            Preprocessed image as numpy array
        """
        # Load image if path is provided
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Could not load image from path: {image}")
        elif isinstance(image, Image.Image):
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            img = image.copy()
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply adaptive thresholding for better text recognition
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return processed
    
    def extract_text_easyocr(self, image: Union[str, np.ndarray, Image.Image]) -> str:
        """
        Extract text using EasyOCR backend.
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if not self.use_easyocr or self.easyocr_reader is None:
            raise RuntimeError("EasyOCR backend not available. Install with: pip install easyocr")
        
        # EasyOCR can handle various image formats directly
        if isinstance(image, str):
            results = self.easyocr_reader.readtext(image)
        else:
            # Convert to RGB for EasyOCR
            if isinstance(image, Image.Image):
                img_array = np.array(image)
            else:
                img_array = image
                
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                # Convert BGR to RGB for EasyOCR
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            
            results = self.easyocr_reader.readtext(img_array)
        
        # Extract text from results
        extracted_text = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Filter out low-confidence detections
                extracted_text.append(text)
        
        return ' '.join(extracted_text)
    
    def extract_text_keras(self, image: Union[str, np.ndarray, Image.Image]) -> str:
        """
        Extract text using custom Keras model.
        
        Args:
            image: Input image
            
        Returns:
            Extracted text
        """
        if not self.use_keras_model or self.keras_model is None:
            raise RuntimeError("Keras model backend not available. Install TensorFlow and provide a model.")
        
        # Preprocess image for Keras model
        processed_img = self.preprocess_image(image)
        
        # Resize to model input size (this would depend on your specific model)
        # This is a placeholder - adjust based on your actual model requirements
        resized = cv2.resize(processed_img, (128, 32))
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_data = np.expand_dims(normalized, axis=0)
        
        # Add channel dimension if needed
        if len(input_data.shape) == 3:
            input_data = np.expand_dims(input_data, axis=-1)
        
        # Predict
        predictions = self.keras_model.predict(input_data)
        
        # Decode predictions (this would depend on your model architecture)
        # This is a simplified placeholder implementation
        decoded_text = self._decode_predictions(predictions)
        
        return decoded_text
    
    def _decode_predictions(self, predictions: np.ndarray) -> str:
        """
        Decode model predictions to text.
        
        Args:
            predictions: Model output predictions
            
        Returns:
            Decoded text string
        """
        # This is a placeholder implementation
        # The actual decoding would depend on your specific model architecture
        # (e.g., CTC decoding for sequence models)
        
        decoded_chars = []
        for pred in predictions[0]:
            char_idx = np.argmax(pred)
            if char_idx < len(self.characters):
                decoded_chars.append(self.characters[char_idx])
        
        return ''.join(decoded_chars).strip()
    
    def extract_text(self, 
                    image: Union[str, np.ndarray, Image.Image],
                    backend: str = 'auto') -> str:
        """
        Extract text from image using the specified backend.
        
        Args:
            image: Input image (file path, numpy array, or PIL Image)
            backend: OCR backend to use ('easyocr', 'keras', 'auto')
            
        Returns:
            Extracted text
        """
        if backend == 'auto':
            # Use EasyOCR if available, otherwise Keras
            if self.use_easyocr:
                backend = 'easyocr'
            elif self.use_keras_model:
                backend = 'keras'
            else:
                raise RuntimeError("No OCR backend available")
        
        if backend == 'easyocr':
            return self.extract_text_easyocr(image)
        elif backend == 'keras':
            return self.extract_text_keras(image)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def extract_text_combined(self, image: Union[str, np.ndarray, Image.Image]) -> str:
        """
        Extract text using both backends and combine results.
        
        Args:
            image: Input image
            
        Returns:
            Combined extracted text
        """
        results = []
        
        if self.use_easyocr:
            try:
                easyocr_text = self.extract_text_easyocr(image)
                results.append(('EasyOCR', easyocr_text))
            except Exception as e:
                print(f"EasyOCR extraction failed: {e}")
        
        if self.use_keras_model:
            try:
                keras_text = self.extract_text_keras(image)
                results.append(('Keras', keras_text))
            except Exception as e:
                print(f"Keras extraction failed: {e}")
        
        if not results:
            raise RuntimeError("No backend successfully extracted text")
        
        # For now, return the first successful result
        # In a more sophisticated implementation, you might combine or validate results
        return results[0][1]
    
    def get_supported_characters(self) -> List[str]:
        """
        Get the list of supported characters including German special characters.
        
        Returns:
            List of supported characters
        """
        return self.characters.copy()
    
    def is_german_text_supported(self) -> bool:
        """
        Check if German text (including special characters) is supported.
        
        Returns:
            True if German characters are supported
        """
        german_chars = {'ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß'}
        return german_chars.issubset(set(self.characters))