# OCR German Language Support

This document describes the enhanced OCR functionality with German language support implemented in the `OCRKeras.py` module.

## Overview

The `KerasOCR` class provides OCR functionality with comprehensive support for German text, including special characters (umlauts and eszett). The implementation supports both custom TensorFlow/Keras models and EasyOCR backend for maximum flexibility.

## German Character Support

### Supported Characters

The OCR system now supports all German special characters:

- **Lowercase umlauts**: `ä`, `ö`, `ü`
- **Uppercase umlauts**: `Ä`, `Ö`, `Ü`
- **Eszett**: `ß`

### Complete Character Set

The extended character set includes:
- Standard ASCII characters (letters, numbers, punctuation)
- German special characters
- Total of 100+ characters for comprehensive text recognition

## Language Configuration

### EasyOCR Backend

The EasyOCR backend is configured with German language support:

```python
# Initialize with German and English language support
ocr = KerasOCR(languages=['de', 'en'])
```

### Available Languages

- `'de'`: German
- `'en'`: English (default fallback)

Additional languages can be added to the list as needed.

## Usage Examples

### Basic Initialization

```python
from OCRKeras import KerasOCR

# Initialize with EasyOCR and German support
ocr = KerasOCR(
    use_easyocr=True,
    use_keras_model=False,
    languages=['de', 'en']
)
```

### Text Extraction

```python
# Extract text from image file
text = ocr.extract_text('german_document.png')

# Extract text using specific backend
text = ocr.extract_text('image.jpg', backend='easyocr')
```

### Character Support Verification

```python
# Check if German characters are supported
print(f"German support: {ocr.is_german_text_supported()}")

# Get all supported characters
chars = ocr.get_supported_characters()
german_chars = [c for c in chars if c in 'äöüÄÖÜß']
print(f"German characters: {german_chars}")
```

## Backend Integration

### EasyOCR Backend

- **Language Support**: Configured with German ('de') language
- **Automatic Setup**: Initializes automatically when `use_easyocr=True`
- **Confidence Filtering**: Filters results with confidence > 0.3
- **Format Support**: Handles various image formats directly

### TensorFlow/Keras Backend

- **Custom Models**: Supports loading custom trained models
- **Character Mapping**: Includes German characters in vocabulary
- **Preprocessing**: Adaptive thresholding for better recognition
- **Extensible**: Easy to integrate new model architectures

## API Reference

### KerasOCR Class

#### Constructor Parameters

- `model_path` (str, optional): Path to custom Keras model
- `use_easyocr` (bool): Enable EasyOCR backend (default: True)
- `use_keras_model` (bool): Enable custom Keras model (default: False)
- `languages` (List[str]): Language codes for recognition (default: ['de', 'en'])

#### Key Methods

- `extract_text(image, backend='auto')`: Extract text using specified backend
- `extract_text_easyocr(image)`: Extract text using EasyOCR
- `extract_text_keras(image)`: Extract text using custom Keras model
- `extract_text_combined(image)`: Use both backends and combine results
- `preprocess_image(image)`: Preprocess image for OCR
- `get_supported_characters()`: Get list of supported characters
- `is_german_text_supported()`: Check German character support

## Installation Requirements

Add to `requirements.txt`:

```
easyocr
opencv-python
tensorflow>=2.14.0
keras>=2.14.0
numpy
Pillow
```

## Integration Examples

### With Existing OCR Pipeline

```python
# Replace existing OCR implementation
from OCRKeras import KerasOCR

# Old: using Tesseract
# pytesseract.image_to_string(image, lang='deu')

# New: using KerasOCR with German support
ocr = KerasOCR(languages=['de', 'en'])
text = ocr.extract_text(image)
```

### Batch Processing

```python
import os
from OCRKeras import KerasOCR

# Initialize OCR
ocr = KerasOCR(languages=['de', 'en'])

# Process directory of images
for filename in os.listdir('images/'):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join('images/', filename)
        text = ocr.extract_text(image_path)
        
        # Check for German characters
        has_german = any(char in text for char in 'äöüÄÖÜß')
        print(f"{filename}: German text detected: {has_german}")
```

## Performance Considerations

### EasyOCR
- **Pros**: High accuracy, multi-language support, no training required
- **Cons**: Larger memory footprint, slower initialization
- **Best for**: Production use, high accuracy requirements

### Custom Keras Models
- **Pros**: Fast inference, customizable, smaller footprint
- **Cons**: Requires training, model-specific preprocessing
- **Best for**: Specialized use cases, embedded systems

## Troubleshooting

### Common Issues

1. **EasyOCR Installation**: Requires internet connection for model download
2. **Memory Usage**: EasyOCR models are large (100MB+)
3. **GPU Support**: Optional but recommended for large-scale processing

### Error Handling

The implementation includes comprehensive error handling:
- Graceful fallback when backends fail
- Clear error messages for configuration issues
- Automatic backend selection when preferred method unavailable

## Future Enhancements

Potential improvements:
- Additional European language support
- Model ensemble methods
- Confidence-based result selection
- Custom character set training utilities