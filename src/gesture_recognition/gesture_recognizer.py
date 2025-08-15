import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
from mediapipe.framework.formats import landmark_pb2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class GestureRecognizer:
    def __init__(self):
<<<<<<< HEAD
        # Ensure the correct relative path to the gesture_recognizer.task file
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, 'exported_model', 'gesture_recognizer.task')
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(base_options=base_options)
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

    def recognize(self, image):
        # Convert the image to the required format for Mediapipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(rgb_image))
        
        # Perform gesture recognition
        recognition_result = self.recognizer.recognize(mp_image)

        if not recognition_result.gestures:
            return image, "No gesture recognized"
        top_gesture = recognition_result.gestures[0][0]
        if top_gesture.score < 0.50:
            return image, "No gesture recognized"
        top_gesture = recognition_result.gestures[0][0]
        hand_landmarks_list = recognition_result.hand_landmarks

        # Annotate the image
        annotated_image = rgb_image.copy()
        for hand_landmarks in hand_landmarks_list:
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        # Convert the annotated image back to BGR for consistency with OpenCV
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
=======
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, 'exported_model', 'gesture_recognizer.task')
        
        if not os.path.exists(model_path):
            # Log oder raise, wenn die Modelldatei nicht gefunden wird
            error_msg = f"Gesture recognizer model not found at {model_path}"
            print(f"ERROR: {error_msg}") # Erwägen Sie die Verwendung von logging
            raise FileNotFoundError(error_msg)

        try:
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.GestureRecognizerOptions(base_options=base_options)
            self.recognizer = vision.GestureRecognizer.create_from_options(options)
        except Exception as e:
            error_msg = f"Failed to initialize GestureRecognizer: {e}"
            print(f"ERROR: {error_msg}") # Erwägen Sie die Verwendung von logging
            raise RuntimeError(error_msg)

    def recognize(self, image):
        if image is None:
            print("ERROR: Input image to recognize is None.") # Erwägen Sie die Verwendung von logging
            # Erstellen Sie ein leeres Platzhalterbild oder geben Sie das None direkt zurück mit einer Fehlermeldung
            # Für Konsistenz geben wir ein (möglicherweise leeres) Bild und eine Fehlermeldung zurück
            placeholder_image = np.zeros((100, 100, 3), dtype=np.uint8) # Beispiel für ein Platzhalterbild
            return placeholder_image, "Error: Input image was None"

        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(rgb_image))
        except cv2.error as e:
            print(f"ERROR: OpenCV error converting image: {e}") # Erwägen Sie die Verwendung von logging
            return image, "Error processing image" # Geben Sie das Originalbild und eine Fehlermeldung zurück
        except Exception as e:
            print(f"ERROR: Unexpected error converting image: {e}") # Erwägen Sie die Verwendung von logging
            return image, "Error processing image"

        try:
            recognition_result = self.recognizer.recognize(mp_image)
        except Exception as e:
            print(f"ERROR: Exception during MediaPipe recognition: {e}") # Erwägen Sie die Verwendung von logging
            # Geben Sie das Originalbild (BGR) und eine Fehlermeldung zurück
            return image, "Recognition error"

        # Überprüfen, ob Ergebnisse vorhanden sind und die erwartete Struktur haben
        # recognition_result.gestures ist List[List[Category]]
        # recognition_result.hand_landmarks ist List[List[NormalizedLandmark]]
        if not recognition_result or not recognition_result.gestures or not recognition_result.gestures[0]:
            # Keine Hände erkannt oder keine Gesten für die erste erkannte Hand
            return image, "No gesture recognized"

        top_gesture = recognition_result.gestures[0][0]

        if top_gesture.score < 0.50:
            return image, "No gesture recognized (low score)"
        
        # Beginnen Sie mit einer Kopie des RGB-Bildes für Anmerkungen
        annotated_image = rgb_image.copy()

        # Zeichnen Sie Hand-Landmarken, falls vorhanden
        if recognition_result.hand_landmarks:
            for hand_landmark_set in recognition_result.hand_landmarks: # hand_landmark_set ist List[NormalizedLandmark]
                if hand_landmark_set: # Stellen Sie sicher, dass Landmarken für diese Hand vorhanden sind
                    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                    hand_landmarks_proto.landmark.extend([
                        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) 
                        for landmark in hand_landmark_set
                    ])
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks_proto,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
        
        # Konvertieren Sie das annotierte Bild zurück zu BGR für Konsistenz mit OpenCV
        annotated_image_bgr = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        
>>>>>>> EduVids-Completing
        return annotated_image_bgr, top_gesture.category_name