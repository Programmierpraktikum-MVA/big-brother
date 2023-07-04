import os
import sys
import whisper

sys.path.append(os.path.join(os.path.dirname(__file__), 'processes'))
from slide_extractor import SlideExtractor
from ocr import SlideOCR
from summarization import TextSummarizer
from keyword_extractor import KeywordExtractor
from speech2text import VideoScript

# define function which wipes folder content
def wipe_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.remove(file_path)
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.rmdir(dir_path)

# Usage example:
if __name__ == "__main__":

    # ---------------------------------------------------------------------------------------------
    # ---PATHS-------------------------------------------------------------------------------------

        # define main dir path
    main_directory = os.path.dirname(os.path.abspath(__file__))
        # define folder in which output files should be saved
    output_path = os.path.join(main_directory, "output")

    # TODO: implement functionality to enable user to upload his mp4 file

        # path for video with presentation    # TODO : VVVVVVVVVVVVVVVV
    video_path = os.path.join(main_directory, "input", "Wie leitet.mp4")
        # folder where slides are extracted and saved
    slides_folder = os.path.join(main_directory, "output", "slides")

    # TODO: install Tesseract on server and link it

        # path for tesseract
    tesseract_path = r'E:\E Apps\Tesseract-OCR\tesseract.exe'
        # set where OCR txt file should be saved
    ocr_file = os.path.join(main_directory, "output", 'OCR_output.txt')
        # set where summary txt file should be saved
    summary_file = os.path.join(main_directory, "output", "summary.txt")
        # set where keywords should be saved
    keywords_file = os.path.join(main_directory, "output", 'keywords.txt')

    # ---------------------------------------------------------------------------------------------

    # clean output folder before starting
    wipe_folder(output_path)

    # ---------------------------------------------------------------------------------------------
    # ---SPEECH2TEXT-------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # whisper settings
    model = whisper.load_model("base")
    fp16 = False

    # execute s2t
    transcriber = VideoScript(model)
    transcriber.transcribe_video(video_path, output_path)

    # ---------------------------------------------------------------------------------------------
    # ---SLIDE EXTRACTOR---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute Slide extractor
    slide_extractor_ = SlideExtractor(video_path, slides_folder)
    slide_extractor_.extract_slides_from_video()

    # ---------------------------------------------------------------------------------------------
    # ---OCR---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute OCR
    slide_ocr_ = SlideOCR(tesseract_path, slides_folder, ocr_file)
    slide_ocr_.ocr_text_from_slides()

    # ---------------------------------------------------------------------------------------------
    # ---SUMMARIZER--------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute summarizer
    summarizer = TextSummarizer()
    summarizer.summarize_file(ocr_file, summary_file)

    # ---------------------------------------------------------------------------------------------
    # ---KEYWORD EXTRACTOR ------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    # execute keyword extractor
    keyword_extractor = KeywordExtractor()
    extracted_keywords = keyword_extractor.extract_keywords(summary_file)
    keyword_extractor.save_keywords(extracted_keywords, keywords_file)
