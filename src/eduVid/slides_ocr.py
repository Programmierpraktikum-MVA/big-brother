import cv2
from PIL import Image
from pytesseract import pytesseract
import os

# TODO
#  Define paths
path_to_tesseract = r'!your_path!\tesseract.exe'
path_to_images = r''

# Link tesseract
pytesseract.tesseract_cmd = path_to_tesseract

# Create the merged output text file
merged_output_file = 'merged_output.txt'

# Define the separator between slide texts
slide_separator = '=== SLIDE ==='

# Set OCR language to German
ocr_language = 'deu'

# Get the file names in the directory
file_texts = []

for root, dirs, file_names in os.walk(path_to_images):
    # Iterate over each file name in the folder
    for file_name in file_names:
        # Construct the full path to the image file
        image_path = os.path.join(root, file_name)

        # Read the image using OpenCV
        img = cv2.imread(image_path, 0)  # Read as grayscale

        # Apply thresholding to the image
        _, thresholded_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Create a PIL Image object from the thresholded image
        pil_img = Image.fromarray(thresholded_img)

        # Extract text from the thresholded image with German language
        text = pytesseract.image_to_string(pil_img, lang=ocr_language)

        # Append the extracted text to the list
        file_texts.append(text)

# Join the file texts using the slide separator
merged_text = '\n\n'.join([f"{slide_separator}\n{text}" for text in file_texts])

# Save the merged output as a single text file
with open(merged_output_file, 'w', encoding='utf-8') as file:
    file.write(merged_text)
