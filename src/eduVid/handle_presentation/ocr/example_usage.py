#!/usr/bin/env python3
"""
Example usage of OCRKeras with German language support.

This example demonstrates how to use the OCRKeras class for extracting text
from images with support for German special characters.
"""

import os
from OCRKeras import KerasOCR


def example_basic_usage():
    """Basic usage example with EasyOCR backend."""
    print("=== Basic Usage Example ===")
    
    # Initialize OCR with German language support
    ocr = KerasOCR(
        use_easyocr=True,
        use_keras_model=False,  # No custom model in this example
        languages=['de', 'en']  # German and English support
    )
    
    print(f"Supported languages: {ocr.languages}")
    print(f"German text support: {ocr.is_german_text_supported()}")
    print(f"Total supported characters: {len(ocr.get_supported_characters())}")
    
    # Show German characters
    german_chars = [c for c in ocr.get_supported_characters() if c in 'äöüÄÖÜß']
    print(f"Supported German special characters: {german_chars}")


def example_text_extraction(image_path):
    """Example of extracting text from an image file."""
    print(f"\n=== Text Extraction Example ===")
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Skipping text extraction example.")
        return
    
    try:
        # Initialize OCR
        ocr = KerasOCR(use_easyocr=True, languages=['de', 'en'])
        
        # Extract text using EasyOCR backend
        extracted_text = ocr.extract_text(image_path, backend='easyocr')
        
        print(f"Image: {image_path}")
        print(f"Extracted text: {extracted_text}")
        
        # Check if German characters were found
        german_chars_found = any(char in extracted_text for char in 'äöüÄÖÜß')
        print(f"German characters detected: {german_chars_found}")
        
    except Exception as e:
        print(f"Text extraction failed: {e}")


def example_custom_model_usage(model_path):
    """Example using a custom Keras model (if available)."""
    print(f"\n=== Custom Keras Model Example ===")
    
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Skipping custom model example.")
        return
    
    try:
        # Initialize OCR with custom Keras model
        ocr = KerasOCR(
            model_path=model_path,
            use_easyocr=False,
            use_keras_model=True,
            languages=['de', 'en']
        )
        
        print(f"Custom model loaded from: {model_path}")
        print(f"Model available: {ocr.keras_model is not None}")
        
    except Exception as e:
        print(f"Custom model initialization failed: {e}")


def example_combined_backends(image_path):
    """Example using both EasyOCR and custom model backends."""
    print(f"\n=== Combined Backends Example ===")
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Skipping combined backends example.")
        return
    
    try:
        # Initialize OCR with both backends
        ocr = KerasOCR(
            use_easyocr=True,
            use_keras_model=False,  # Would need actual model file
            languages=['de', 'en']
        )
        
        # Use automatic backend selection
        text_auto = ocr.extract_text(image_path, backend='auto')
        print(f"Text (auto backend): {text_auto}")
        
        # Try combined extraction (if both backends available)
        if ocr.use_easyocr:
            text_combined = ocr.extract_text_combined(image_path)
            print(f"Text (combined): {text_combined}")
        
    except Exception as e:
        print(f"Combined backends extraction failed: {e}")


def example_preprocessing():
    """Example of image preprocessing functionality."""
    print(f"\n=== Image Preprocessing Example ===")
    
    try:
        # Initialize OCR
        ocr = KerasOCR(use_easyocr=False, use_keras_model=False)
        
        # Create a simple test image
        import numpy as np
        from PIL import Image
        
        # Create test image with text
        test_image = Image.new('RGB', (200, 50), 'white')
        
        # Preprocess the image
        processed = ocr.preprocess_image(test_image)
        
        print(f"Original image size: {test_image.size}")
        print(f"Processed image shape: {processed.shape}")
        print("Preprocessing successful")
        
    except Exception as e:
        print(f"Preprocessing example failed: {e}")


def main():
    """Run all examples."""
    print("OCRKeras German Language Support Examples\n")
    
    # Basic usage
    example_basic_usage()
    
    # Preprocessing example
    example_preprocessing()
    
    # These examples would work with actual image files:
    # example_text_extraction("/path/to/german_text_image.png")
    # example_custom_model_usage("/path/to/german_ocr_model.h5")
    # example_combined_backends("/path/to/german_text_image.png")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("Note: Text extraction examples require actual image files.")
    print("Replace file paths with real images to test full functionality.")


if __name__ == "__main__":
    main()