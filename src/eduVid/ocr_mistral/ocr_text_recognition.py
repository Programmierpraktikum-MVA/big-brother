import cv2
import numpy as np
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    print("TensorFlow not available (likely Python 3.13 compatibility issue)")
    print("Using EasyOCR backend instead...")
    TENSORFLOW_AVAILABLE = False

import pdf2image
from pdf2image import convert_from_path
import pathlib
from pathlib import Path
import os, sys
import matplotlib.pyplot as plt
from PIL import Image
import string

# Erweiterung der Zeichen für deutsche Sprache (Umlaute, ß und Sonderzeichen)
GERMAN_EXTRA_CHARS = "äöüÄÖÜß§€„“”‚‘’´`²³°^~|<>µ¢£¥©®™✓•¿¡←→↑↓«»±÷×≤≥≠≡∞∑∏∫√∂∆∇∈∉∋∌⊂⊃⊆⊇∩∪∧∨∃∀∅∈∉⊆⊇∝∠∴∵∗∅∥∦∧∨≅≈≃≡≤≥⊥∥∠∟⊾⊿⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⊲⊳⊴⊵⊶⊷⊸⊹⊺⊻⊼⊽⊾⊿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿⌀⌁⌂⌃⌄⌅⌆⌇⌈⌉⌊⌋⌌⌍⌎⌏⌓⌑⌒⌓⌔⌕⌖⌗⌘⌙⌚⌛⌜⌝⌞⌟⌠⌡⌢⌣⌤⌥⌦⌧⌨〈〉⌫⌬⌭⌮⌯⌰⌱⌲⌳⌴⌵⌶⌷⌸⌹⌺⌻⌼⌽⌾⌿⍀⍁⍂⍃⍄⍅⍆⍇⍈⍉⍊⍋⍌⍍⍎⍏⍐⍑⍒⍓⍔⍕⍖⍗⍘⍙⍚⍛⍜⍝⍞⍟⍠⍡⍢⍣⍤⍥⍦⍧⍨⍩⍪⍫⍬⍭⍮⍯⍰⍱⍲⍳⍴⍵⍶⍷⍸⍹⍺⍻⍼⎀⎁⎂⎃⎄⎅⎆⎇⎈⎉⎊⎋⎌⎍⎎⎏⎐⎑⎒⎓⎔⎕⎖⎗⎘⎙⎚⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪⎫⎬⎭⎮⎯⎰⎱⎲⎳⎴⎵⎶⎷⎸⎹⎺⎻⎼⎽⎾⎿"

class KerasOCR:
    """
    Keras-based OCR implementation with (multilingual) German+English support and special characters.
    """

    def __init__(self, languages=['en', 'de']):
        """
        Initialize the Keras OCR model
        """
        # Zeichen: Englisch, Deutsch (Umlaute, ß), Ziffern, Satzzeichen, Sonderzeichen und Leerzeichen
        combined_characters = string.ascii_letters + string.digits + string.punctuation + " " + GERMAN_EXTRA_CHARS
        self.characters = ''.join(sorted(set(combined_characters)))
        self.max_length = 50
        self.languages = languages

        if TENSORFLOW_AVAILABLE:
            self.char_to_num = tf.keras.layers.StringLookup(vocabulary=list(self.characters), mask_token=None)
            self.num_to_char = tf.keras.layers.StringLookup(vocabulary=self.char_to_num.get_vocabulary(), mask_token=None, invert=True)
        else:
            self.char_to_num = None
            self.num_to_char = None

        # Try to load pre-trained model, otherwise create a simple one
        try:
            self.model = self._load_or_create_model()
        except Exception as e:
            print(f"Warning: Could not load OCR model: {e}")
            print("Using EasyOCR backend only...")
            self.model = None

    def _load_or_create_model(self):
        """
        Load a pre-trained model or create a simple CNN-RNN architecture for OCR
        """
        try:
            # EasyOCR mit mehreren Sprachen, z.B. Deutsch und Englisch
            import easyocr
            self.easyocr_reader = easyocr.Reader(self.languages, gpu=False)  # GPU aus für Kompatibilität
            return None  # Wir nutzen EasyOCR, kein eigenes Modell
        except ImportError:
            print("EasyOCR not available, trying to create custom model...")
            if TENSORFLOW_AVAILABLE:
                return self._create_simple_ocr_model()
            else:
                print("Neither EasyOCR nor TensorFlow available. Limited functionality.")
                return None

    def _create_simple_ocr_model(self):
        """
        Create a simple CNN-RNN model for OCR
        """
        if not TENSORFLOW_AVAILABLE:
            print("TensorFlow not available, cannot create custom model")
            return None

        # Input für Bilder
        input_img = layers.Input(shape=(128, 512, 1), name="image")

        # CNN für Feature-Extraktion
        x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(input_img)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
        x = layers.MaxPooling2D((2, 2))(x)
        x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
        x = layers.MaxPooling2D((2, 2))(x)

        # Reshape für RNN
        new_shape = ((128 // 8), (512 // 8) * 128)
        x = layers.Reshape(target_shape=new_shape)(x)
        x = layers.Dense(64, activation="relu")(x)

        # RNN Layers
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25))(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25))(x)

        # Output Layer
        output = layers.Dense(len(self.char_to_num.get_vocabulary()) + 1, activation="softmax")(x)

        model = keras.models.Model(inputs=input_img, outputs=output, name="ocr_model")
        return model

    def _preprocess_image_for_ocr(self, image):
        """
        Preprocess image for OCR model
        """
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize to model input size
        image = cv2.resize(image, (512, 128))

        # Normalize
        image = image.astype(np.float32) / 255.0

        # Add batch and channel dimensions
        image = np.expand_dims(image, axis=[0, -1])

        return image

    def _extract_text_with_easyocr(self, image):
        """
        Extract text using EasyOCR (with language support)
        """
        try:
            if hasattr(self, 'easyocr_reader'):
                # Convert to RGB if needed
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image

                results = self.easyocr_reader.readtext(image_rgb)
                text = ' '.join([result[1] for result in results])
                return text
        except Exception as e:
            print(f"EasyOCR failed: {e}")

        return ""

    def _extract_text_with_keras_ocr(self, image):
        """
        Extract text using custom Keras OCR model
        """
        if not TENSORFLOW_AVAILABLE:
            print("TensorFlow not available for custom Keras OCR")
            return ""

        try:
            if self.model is None or self.num_to_char is None:
                return ""

            # Preprocess image
            processed_image = self._preprocess_image_for_ocr(image)

            # Predict
            prediction = self.model.predict(processed_image, verbose=0)

            # Decode prediction (simple greedy decoding)
            decoded_text = ""
            for timestep in prediction[0]:
                char_index = np.argmax(timestep)
                if char_index < len(self.num_to_char.get_vocabulary()):
                    char = self.num_to_char(char_index).numpy().decode('utf-8')
                    if char != '[UNK]':
                        decoded_text += char

            return decoded_text.strip()
        except Exception as e:
            print(f"Keras OCR failed: {e}")
            return ""

    def extract_text_from_image(self, image_path):
        """
        Read text from an image using OCR (EasyOCR with DE/EN support).
        """
        try:
            # Bild einlesen
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")

            # Erst EasyOCR (mehrsprachig), dann Fallback auf Custom
            text = self._extract_text_with_easyocr(image)

            if not text and self.model is not None:
                text = self._extract_text_with_keras_ocr(image)

            return text

        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def pdf_to_image(self, pdf_path, output_folder):
        """
        Convert PDF pages to images using pdf2image.
        """
        if not Path(output_folder).exists():
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        try:
            # Verschiedene Poppler-Pfade für Kompatibilität
            poppler_paths = [
                None,  # Automatisch suchen
                "/usr/bin",  # Linux
                "/opt/homebrew/bin",  # macOS Homebrew
                r"C:\Program Files\Poppler\poppler-24.08.0\Library\bin"  # Windows
            ]

            pages = None
            for poppler_path in poppler_paths:
                try:
                    if poppler_path:
                        pages = convert_from_path(pdf_path, output_folder=output_folder, fmt='png', poppler_path=poppler_path)
                    else:
                        pages = convert_from_path(pdf_path, output_folder=output_folder, fmt='png')
                    break
                except Exception:
                    continue

            if pages is None:
                raise Exception("Could not convert PDF with any poppler path")

            return pages

        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []

    def extract_text_from_pdf(self, pdf_path, output_folder):
        """
        Extract text from a PDF with OCR (supports German/English).
        """
        pages = self.pdf_to_image(pdf_path, output_folder)
        texts = []

        for i, page in enumerate(pages):
            try:
                page_array = np.array(page)
                text = self._extract_text_with_easyocr(page_array)
                if not text and self.model is not None:
                    text = self._extract_text_with_keras_ocr(page_array)
                texts.append(text)
            except Exception as e:
                print(f"Error processing page {i}: {e}")
                texts.append("")

        # Aufräumen temporärer Dateien
        for vid_file in os.listdir(output_folder):
            if vid_file.endswith(".md"):
                continue
            del_path = os.path.join(output_folder, vid_file)
            if os.path.isfile(del_path):
                try:
                    os.remove(del_path)
                except Exception as e:
                    print(f"Could not remove {del_path}: {e}")

        return texts

    def getFrame(self, sec, vid_path, output_folder):
        """
        Extract a frame at a specific time from a video.
        """
        if not Path(output_folder).exists():
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        try:
            vidcap = cv2.VideoCapture(vid_path)
            vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
            success, image = vidcap.read()

            if success:
                frame_path = os.path.join(output_folder, f"frame_{sec}.jpg")
                cv2.imwrite(frame_path, image)
                vidcap.release()
                return success
            else:
                vidcap.release()
                return None
        except Exception as e:
            print(f"Error extracting frame at {sec}s: {e}")
            return None

    def vid_to_frames(self, vid_path, output_folder, frame_rate):
        """
        Convert video to frames.
        """
        if not Path(output_folder).exists():
            Path(output_folder).mkdir(parents=True, exist_ok=True)

        try:
            success = self.getFrame(0, vid_path, output_folder)
            if not success:
                print("Could not extract first frame")
                return

            count = 1
            sec = 0

            while success:
                count += 1
                sec = sec + frame_rate
                sec = round(sec, 2)
                success = self.getFrame(sec, vid_path, output_folder)
                if count > 10000:  # Schutz vor Endlosschleife
                    print("Frame extraction limit reached")
                    break
        except Exception as e:
            print(f"Error converting video to frames: {e}")

    def extract_text_from_video_frames(self, vid_path, output_folder, frame_rate=1.0):
        """
        Extract text from video by first converting to frames, then applying OCR to each frame.
        """
        self.vid_to_frames(vid_path, output_folder, frame_rate)
        texts = []
        frame_files = [f for f in os.listdir(output_folder) if f.startswith("frame_") and f.endswith(".jpg")]
        frame_files.sort()

        for frame_file in frame_files:
            frame_path = os.path.join(output_folder, frame_file)
            text = self.extract_text_from_image(frame_path)
            texts.append(text)
        return texts

# Convenience functions
def create_keras_ocr(languages=['en', 'de']):
    """Create and return a KerasOCR instance with language support."""
    return KerasOCR(languages=languages)

_keras_ocr_instance = None

def get_keras_ocr_instance(languages=['en', 'de']):
    """Get or create global KerasOCR instance with language support."""
    global _keras_ocr_instance
    if _keras_ocr_instance is None:
        _keras_ocr_instance = KerasOCR(languages=languages)
    return _keras_ocr_instance

# Ensure the function extract_text_from_image is properly exposed at the module level
def extract_text_from_image(image_path):
    ocr = get_keras_ocr_instance()
    return ocr.extract_text_from_image(image_path)

def pdf_to_image(pdf_path, output_folder):
    ocr = get_keras_ocr_instance()
    return ocr.pdf_to_image(pdf_path, output_folder)

def extract_text_from_pdf(pdf_path, output_folder):
    ocr = get_keras_ocr_instance()
    return ocr.extract_text_from_pdf(pdf_path, output_folder)

def getFrame(sec, vid_path, output_folder):
    ocr = get_keras_ocr_instance()
    return ocr.getFrame(sec, vid_path, output_folder)

def vid_to_frames(vid_path, output_folder, frame_rate):
    ocr = get_keras_ocr_instance()
    return ocr.vid_to_frames(vid_path, output_folder, frame_rate)

if __name__ == "__main__":
    ocr = KerasOCR(languages=['en', 'de'])
    print("Keras OCR initialized successfully (with German + English language support and many special characters)!")