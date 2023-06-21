from rake_nltk import Rake

def extract_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    r = Rake(language='german')
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()

    return keywords

# TODO
#  set path
input_file_path = '.txt'
output_file_path = 'keywords.txt'

extracted_keywords = extract_keywords(input_file_path)

with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write('\n'.join(extracted_keywords))

print("Keywords extracted and saved successfully!")
