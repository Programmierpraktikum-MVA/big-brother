import os
import sys
import io
import json
<<<<<<< HEAD
=======
import importlib.util
>>>>>>> EduVids-Completing
from datetime import datetime, timedelta

from flask import (render_template, request, Blueprint, url_for, send_from_directory, redirect, Response, jsonify)
import flask_login
from flask_socketio import emit
import cv2
from PIL import Image, UnidentifiedImageError
import numpy as np
import base64
import gridfs
from pymongo import MongoClient
from bson import ObjectId

# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "database_management"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "gesture_recognition/user_scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid/vector_search"))
<<<<<<< HEAD
=======
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid/ocr_mistral"))
# Add src directory to path for proper package imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
>>>>>>> EduVids-Completing
available_courses_json = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid", "scrapers", "video_scrapers", "available_courses.json")
configure_json = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "eduVid", "config.json")

from app.blueprints.logic.forms import VideoUploadForm, QueryForm
from app import application, socketio

from gesture_recognizer import GestureRecognizer
<<<<<<< HEAD
import question_answering.qa_algo_core as qa
=======
# import question_answering.qa_algo_core as qa  # DISABLED - Llama 4 nicht mehr laden

import Graphing.Graphing as gr
>>>>>>> EduVids-Completing

from base_database import BaseDatabase
from lua_sandbox_runner import run_lua_in_sandbox

from mongo_vs import search

db = BaseDatabase()

last_executed_lua_script = datetime.now()

logic = Blueprint("logic", __name__)
gesture = GestureRecognizer()

GESTURE_ACTIONS = {
    "like": ["yes", "like", "help", "good", "hungry"],
    "rock": ["Good Morning/Afternoon/Evening", "How are you?", "Thank you", "Please", "Hello"],
    "closed_fist": ["I", "You", "it", "she/he", "they"],
    "call": ["be", "eat", "do", "have", "go"],
    "ok": ["What", "Where", "When", "Which", "Who"],
    "dislike": ["no", "hate", "sorry", "Delete All", "Delete 1"],
    "italy": ["spaghetti", "pizza", "lasagna", "mamma mia", "i love italy"]
}

Gesture_Script_Map = {
    'like': 'hello_welt',
    'rock': 'hello_welt',
    'closed_fist': 'hello_welt',
    'call': 'standart_call',
    'ok ': 'hello_welt',
    'dislike': 'hello_welt',
    'italy': 'hello_welt',
    'one' : 'hello_welt', 
    'peace' : 'hello_welt',
    'three' : 'hello_welt', 
    'four' : 'hello_welt',
    'highfive' : 'hello_welt'
}

# Gesture to Action 
@logic.route("/gestureReco")
@flask_login.login_required
def gestureReco():
    return render_template("gestureReco_actions.html")

@socketio.on("gesture_recognition", namespace="/gesture_recognition")
def recognizing_gestures(data):
    try:
        img_url = data.get("image")
        if not img_url:
            print("Error: No image data found in request.")
            return
        
        img_data_parts = img_url.split(",")
        if len(img_data_parts) != 2:
            print("Error: Image data is not in the expected base64 format.")
            return

        img_str = img_data_parts[1]
        try:
            img_data = base64.b64decode(img_str)
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
            return
        
        try:
            pil_img = Image.open(io.BytesIO(img_data))
            np_img = np.array(pil_img)
        except UnidentifiedImageError as e:
            print(f"Error: Unable to identify image. {e}")
            return
        except Exception as e:
            print(f"Error loading image into PIL: {e}")
            return

        np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

        try:
            annotated_image, class_name = gesture.recognize(np_img)
        except Exception as e:
            print(f"Error during gesture recognition: {e}")
            return

        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.putText(annotated_image, class_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        pil_annotated_img = Image.fromarray(annotated_image)

        buffered = io.BytesIO()
        pil_annotated_img.save(buffered, format="JPEG")
        response_data_url = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Execute the Lua script based on the recognized gesture
        script_id = Gesture_Script_Map.get(class_name)
        global last_executed_lua_script
        if script_id and (datetime.now() - last_executed_lua_script) > timedelta(seconds=2):
            script_content = db.get_lua_script_by_id(script_id)
            lua_result = run_lua_in_sandbox(script_content)
            last_executed_lua_script = datetime.now()
            emit("ack_gesture_recognition", {"image": response_data_url, "gesture": class_name, "lua_result": lua_result})
        else:
            emit("ack_gesture_recognition", {"image": response_data_url, "gesture": class_name, "lua_result": "No script found"})

    except Exception as e:
        print(f"Error in recognizing_gestures: {e}")


@logic.route('/action_control', methods=['GET', 'POST'])
@flask_login.login_required
def action_control():
    if request.method == 'POST':
        for gesture in Gesture_Script_Map.keys():
            selected_script_id = request.form.get(gesture)
            Gesture_Script_Map[gesture] = selected_script_id
        return redirect(url_for('logic.action_control'))
    #['standart_like', 'standart_rock', 'standart_closed_first', 'standart_call', 'standart_ok', 'standart_dislike', 'standart_italy']
    user_id = flask_login.current_user.get_id()
    accessible_scripts = db.get_accessible_scripts(user_id)  # Assume 'user1' for now
    private_scripts = db.get_private_scripts(user_id)  # Fetch private scripts separately if needed


    return render_template('action_control.html', gesture_script_map=Gesture_Script_Map, accessible_scripts=accessible_scripts,
                           private_scripts= private_scripts)

@logic.route('/upload_script', methods=['POST'])
@flask_login.login_required
def upload_script(): 
    script_name = request.form.get('script_name')
    script_file = request.files.get('script_file')
    is_private = request.form.get('is_private') == 'on'
    userid = flask_login.current_user.get_id()

    if script_file and script_file.filename.endswith('.lua'):
        script_content = script_file.read().decode('utf-8')
        
        # Save the new script
        db.save_lua_script(userid, script_name, script_content, is_private)
        return redirect(url_for('logic.action_control'))
    else:
        return "Invalid file type. Only Lua files are allowed.", 400
  
# Gesture to Text Conversion
@logic.route("/gestureReco_text")
@flask_login.login_required
def gestureReco_text():
    return render_template("gestureReco_text.html")


@socketio.on("gesture_recognition_text", namespace="/gesture_recognition_text")
def recognizing_gestures_text(data):
    try:
        img_url = data.get("image")
        if not img_url:
            print("Error: No image data found in request.")
            return
        
        img_data_parts = img_url.split(",")
        if len(img_data_parts) != 2:
            print("Error: Image data is not in the expected base64 format.")
            return

        img_str = img_data_parts[1]
        try:
            img_data = base64.b64decode(img_str)
        except Exception as e:
            print(f"Error decoding base64 image data: {e}")
            return
        
        try:
            pil_img = Image.open(io.BytesIO(img_data))
            np_img = np.array(pil_img)
        except UnidentifiedImageError as e:
            print(f"Error: Unable to identify image. {e}")
            return
        except Exception as e:
            print(f"Error loading image into PIL: {e}")
            return

        np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)

        try:
            annotated_image, class_name = gesture.recognize(np_img)
        except Exception as e:
            print(f"Error during gesture recognition: {e}")
            return

        actions = GESTURE_ACTIONS.get(class_name, [])

        annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        cv2.putText(annotated_image, class_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        pil_annotated_img = Image.fromarray(annotated_image)

        buffered = io.BytesIO()
        pil_annotated_img.save(buffered, format="JPEG")
        response_data_url = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")

        emit("ack_gesture_recognition_text", {"image": response_data_url, "gesture": class_name, "actions": actions})

    except Exception as e:
        print(f"Error in recognizing_gestures: {e}")

@logic.route("/videos/<filename>")
def serve_video(filename):
    return send_from_directory(application.config["TMP_VIDEO_FOLDER"], filename)


@logic.route("/old_eduVid", methods=["GET", "POST"])
@flask_login.login_required
def old_eduVid():
    form = VideoUploadForm()

    if form.validate_on_submit():
        name = form.name.data
        video = form.video.data
        segment_file = request.files.get("segments")
        question = form.question.data

        segments_data = segment_file.stream.read()
        segments_json = json.loads(segments_data)
        segments = segments_json.get("time-stamps")

        if not os.path.isdir(application.config["TMP_VIDEO_FOLDER"]):
            os.makedirs(application.config["TMP_VIDEO_FOLDER"])

        # deletes every video file in tmp folder
        for vid_file in os.listdir(application.config["TMP_VIDEO_FOLDER"]):
            if vid_file.endswith(".md"):
                continue
            del_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], vid_file)
            if os.path.isfile(del_path):
                os.remove(del_path)

        video_path = os.path.join(application.config["TMP_VIDEO_FOLDER"], video.filename)
        video.save(video_path)

        model_name = "timpal0l/mdeberta-v3-base-squad2"

        audio_file = os.path.join(application.config["TMP_VIDEO_FOLDER"], video.filename + "_audio.wav")
        _ = qa.HelperFN.extract_audio_from_mp4(video_path, audio_file)

        recog = qa.SpeechRecog(audio_file)
        context, tags = recog.transcribe()

        qa_result = qa.QAAlgo(model_name)
        answer = qa_result.answer_question(context, question)

        matching_segments = qa.HelperFN.find_matching_segments(tags, answer)
        merged_segments = qa.HelperFN.merge_overlapping_segments(matching_segments)

        if len(merged_segments) == 0:
            print("No segments found !")
            answer = "Es konnte keine passende Antwort gefunden werden"

        video_url = url_for("logic.serve_video", filename=video.filename)

        if segments is None:
            segments = []

        answer_segments = [{f"Answer{i}": begin} for i, (begin, _) in enumerate(merged_segments, start=1)]

        video_info = {
            "title": name,
            "url": video_url,
            "time_stamps": segments,
            "question": question,
            "answer": answer,
            "answer_time_stamps": answer_segments
        }

        print(video_info)

        return render_template("eduVidPlayer.html", video_info=video_info)

    return render_template("eduVid_old.html", form=form)


<<<<<<< HEAD
@logic.route("/eduVid", methods=["GET", "POST"])
@flask_login.login_required
def eduVid():
    return render_template("eduVid.html")
=======
@logic.route("/eduVid_old_llama", methods=["GET", "POST"])
@flask_login.login_required
def eduVid_old_llama():
    """
    OLD IMPLEMENTATION - NOT USED
    Diese Funktion nutzte Llama 4 für Text-zu-Text Generation.
    Wurde ersetzt durch neue OCR + Mistral Implementierung.
    """
    form = QueryForm()
    if form.validate_on_submit():
        user_input = form.query.data
        uploaded_file = form.file.data
        if user_input:
            # Folgende Methode nutzt Llama um eine Antwort zu generieren, gerne anpassen
            answer = qa.TextToText.answerWithLlama(user_input)
            print(answer)
            content = answer.get("content", "")
            return render_template("eduVid.html", form=form, answer_text=content)
        if uploaded_file:
            #answer = Platzhalter für Funktion, welche die Datei verarbeitet und JSON Zurückgibt, json kommt dann zwei zeilen drunter in "json_data"
            static_folder = os.path.join(application.root_path, "static")
            answer= gr.create_graph_html_from_json(json_data, static_folder)
            print(answer)
            #Wenn zusätzlich Text zurückgegeben werden soll, einfach im return answer_text= blabla ändern
            return render_template("eduVid.html", form=form, answer_link=answer)
    return render_template("eduVid.html", form=form)


@logic.route("/eduVid", methods=["GET", "POST"])
@flask_login.login_required
def eduVid():
    """
    Verarbeitet hochgeladene PDFs oder Bilder mit OCR und zeigt extrahierten Text an.
    """
    import os
    import importlib.util
    import tempfile

    form = QueryForm()
    if form.validate_on_submit():
        user_input = form.query.data
        uploaded_file = form.file.data

        if uploaded_file:
            try:
                print("DEBUG: Datei hochgeladen, starte OCR...")

                # Dateiendung ermitteln
                filename = uploaded_file.filename
                ext = os.path.splitext(filename)[1].lower()

                # Datei temporär speichern
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                print(f"DEBUG: Temporäre Datei gespeichert unter {tmp_path}")

              
                current_dir = os.path.abspath(os.path.dirname(__file__))
                ocr_file_path = os.path.normpath(os.path.join(
                    current_dir, "..", "..", "..", "..", "eduVid", "ocr_mistral", "ocr_text_recognition.py"
                ))

                # OCR-Modul importieren
                ocr_module_spec = importlib.util.spec_from_file_location("ocr_text_recognition", ocr_file_path)
                ocr_module = importlib.util.module_from_spec(ocr_module_spec)
                ocr_module_spec.loader.exec_module(ocr_module)

                # PDF oder Bild unterscheiden
                if ext == ".pdf":
                    with tempfile.TemporaryDirectory() as tmp_output:
                        text_list = ocr_module.extract_text_from_pdf(tmp_path, tmp_output)
                        response_text = "\n\n".join(text_list)
                elif ext in [".jpg", ".jpeg", ".png"]:
                    response_text = ocr_module.extract_text_from_image(tmp_path)
                else:
                    response_text = f"Nicht unterstützter Dateityp: {ext}"

                print(f"DEBUG: OCR Ergebnis:\n{response_text}")

                # Direkte Imports verwenden statt dynamische Imports
                import sys
                import os
                
                # Füge src-Verzeichnis zu sys.path hinzu für korrekte Paket-Imports
                src_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                
                from src.eduVid.ocr_mistral import mistral_nextslide_text as mistral_module
                from src.eduVid.ocr_mistral import ocr_json_graph as json_module

                # Erstellt nächste Slide - KORRIGIERT: Übergebe response_text als Argument
                next_slide_text = mistral_module.generate_next_slide(response_text)

                # JSON Erstellen
                print(f"DEBUG: Calling generate_json with text: {next_slide_text[:100]}...")
                json_output = json_module.generate_json(next_slide_text)
                print(f"DEBUG: generate_json returned: {json_output[:500]}...")

                return render_template("eduVid.html", form=form, answer_text=next_slide_text+"\n\n=== JSON OUTPUT ===\n"+json_output)

            except Exception as e:
                error_msg = f"Fehler bei der JSON-Verarbeitung: {str(e)}"
                print(error_msg)
                return render_template("eduVid.html", form=form, answer_text=error_msg)

        elif user_input:
            return render_template("eduVid.html", form=form, answer_text=f"Du hast eingegeben: {user_input}")

    return render_template("eduVid.html", form=form)
>>>>>>> EduVids-Completing


@logic.route('/search', methods=['POST'])
def search_videos():
    data = request.get_json()
    query = data.get('query', '')

    with open(configure_json, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    mongodb_uri = config_data['MONGO_URI']

    database_name = "BigBrother"
    collection_name = "extracted_data"
    thumbnail_collection = "thumbnails"

    client = MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]

    videos = search(query, collection, db, thumbnail_collection)
    return jsonify(videos)

@logic.route('/courses', methods=['GET'])
def get_courses():
    with open(available_courses_json, 'r', encoding='utf-8') as f:
        courses_data = json.load(f)
    return jsonify(courses_data)