from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

# helper func to combine separate sentences into one array element within the limit 
def combine_sentences(sentences, value, limit):
    result = []
    current_sentence = ''
    i = 0
    temp_sum = 0
    
    for sent, val in zip(sentences, value):
        temp_sum = temp_sum + value[i]
        if temp_sum <= limit:
            current_sentence += sent
        else:
            result.append(current_sentence)
            current_sentence = sent
            temp_sum = 0
        if i < len(sentences):
          i += 1
    
    if current_sentence:
        result.append(current_sentence)
    
    return result

# helper func to count how many tokens are used for each sentence. values are stored in array
def count_tokens(chunks):
  sentence_token_counts = []
  for elem in chunks:
    sentences = elem.split('.')
    for sentence in sentences:
          sentence_tokens = tokenizer.encode(sentence, add_special_tokens=False)
          sentence_token_count = len(sentence_tokens) + 1
          sentence_token_counts.append(sentence_token_count)
  return sentence_token_counts[::2]

# settings for hugging face model
tokenizer = AutoTokenizer.from_pretrained("timpal0l/mdeberta-v3-base-squad2")
model = AutoModelForQuestionAnswering.from_pretrained("timpal0l/mdeberta-v3-base-squad2")

# second model (I think upper one is better)
  #tokenizer = AutoTokenizer.from_pretrained("deepset/gelectra-base-germanquad")
  #model = AutoModelForQuestionAnswering.from_pretrained("deepset/gelectra-base-germanquad")

# variables
# define context 
context = 'Lasst uns beginnen mit der Vorlesung über logische Programmierung. Wir sind im Verlauf dieser Vorlesung schon relativ weit jetzt fortgeschritten.' \
                'Genauer gesagt, wir sind ja bei der letzten Vorlesung angelangt. Wir sind im Programmierparadigmen-Anteil und hier in dem Blog über logische Programmierung vor allem mit Prolog.' \
                'Heute wollen wir uns mit Prolog beschäftigen, mit logischer Programmierung. Wir beginnen mit einer Einführung in Prolog. Ich werde euch dann erzählen, wie die Syntax der Sprache aussieht.' \
                'Dann werden wir über Unifikation und Resolution reden. Das sind die grundlegenden Mechanismen, die in Prolog angewendet werden. Ja, dann wollen wir uns anschauen, wie Rekursion in Prolog funktioniert.' \
                'Und abschließend wollen wir uns mit vordefinierten Predikaten auseinandersetzen. Beginnen wir mit einer Einführung in Prolog.' \
                'Die logische Programmierung insgesamt ist ein weiterer Vertreter der sogenannten deklarativen Programmierung.' \
                'Deklerativ bedeutet, dass wir uns darauf konzentrieren, was wir berechnen wollen, was das Problem ist, dass man lösen will.' \
                'Und dass wie, also wie das Problem angelöst wird, die Implementierung, das soll möglichst uns automatisch abgenommen werden.' \
                'Also die Implementierung, die soll dann der Interpreter vorgeben, sich drum kümmern, damit möchte man als Programmierer weniger zu tun haben.' \
                'Ja, und das setzt man in Prolog dadurch um, dass man eine Programmiersprache hier eben Prolog auf der mathematischen Logik aufsetzt.' \
                'Wir haben hier Aktionen, das können Fakten und Regeln sein, die eine Situation beschreiben. Damit beschreiben wir also was gilt, die diese Aktionen enthalten, damit auch die gesamte Datenbasis.' \
                'Ja, und dann werden Anfragen an das System vom Genutze als Ziel vorgegeben. Und der Interpreter versucht automatisch weitere Regeln herzuleiten, um die Frage zu beantworten.' \
                'Das klingt jetzt sicher noch ein bisschen abstrakt, aber ich denke, wenn wir die Vorlesung gehört haben, dann macht es alles super Sinn.' \
                'Ja, in Prolog sieht die Lösungsmetode so aus, dass man eine Art Tiefensuche nach einer Lösung startet und diese Tiefensuche arbeitet mit Unifikation und Resolution.' \
                'Ziel ist es sozusagen in der Anfrage an das System, die eventuell offene Variablen enthält, Variablenbelegungen zu finden, mit denen die Anfrage wahr wird.' \
                'Bei einer positiven Antwort können wir die Anfrage aus der Datenbasis ableiten, dann wird eine gültige Belegung der freien Variablen zurückgegeben.' \
                'Bei einer negativen Antwort kann die Anfrage nicht aus der Datenbasis abgeleitet werden. Der kann also keine gültige Belegung gefunden werden und die Antwort ist dann ein No bzw. false.' \
                'Prolog hat vielfältige Anwendungsgebiete in der künstlichen Intelligenz wird Prolog eingesetzt bei der Spracherkennung, bei der Datenbanksuche, bei Expertensystemen und im Constraint Programming.' \
                'Die Geschichte von Prolog die reicht in die 60er zurück. 1965 hat John Alan Robinson den Resolutionskalkülen entwickelt. Das ist die basis, die theoretische Basis auf der Prolog arbeitet.' \
                '1972 kam dann der erste Prologinterpräter, der wurde von Alan Colmerauer in Frankreich entwickelt. Daher leitet sich auch die Bedeutung des Namens Prolog ab.' \
                'Das steht nämlich für Programmation und Logique. Danach hat sich die Entwicklung von Prolog weiter verlegt nach Schottland.' \
                'Der erste Prolog-Kompeiler wurde von David Warren entwickelt, den Edinburgh und nannte sich Warren abstract-machine. Seit 1995 gibt es einen ISO standard für Prolog, der basiert auf dem Edinburgh-Dialect.' \
                'Es gibt verschiedene Implementierungen für Prolog, das ist nicht weiter erstaunlich.' \
                'Wir verwenden SWI-Prolog und da habt ihr hier auch auf der Folie den Link, mit dem ihr euch die Sprache, also den Interpräter, implementieren, installieren könnt.' \
                'Ja so viel erstmal zu Einführung, wir machen gleich weiter mit der Sprach Syntax.'

# ask a question
question = 'Was entwickelte Alan Colmerauer?'

# define the maximum number of tokens per chunk
max_tokens_per_chunk = 512
start_idx = 0
chunks = []
final_answer_tokens = []

# encode the full context to count the tokens
context_tokens = tokenizer.encode(context, add_special_tokens=False)

# split entire context into separate sentences
while start_idx < len(context_tokens):
    # find the next sentence boundary (period)
    next_period_idx = context_tokens[start_idx:].index(tokenizer.convert_tokens_to_ids(".")) + start_idx
    if next_period_idx - start_idx <= max_tokens_per_chunk:
        # if the next sentence fits within the chunk, include it
        end_idx = next_period_idx + 1
    else:
        # if the next sentence doesn't fit, use the max_tokens_per_chunk limit
        end_idx = start_idx + max_tokens_per_chunk

    chunk_tokens = context_tokens[start_idx:end_idx]
    chunk_text = tokenizer.decode(chunk_tokens)
    chunks.append(chunk_text)
    start_idx = end_idx

# create list with token values
tok_val_list = count_tokens(chunks)

# create ready chunks
ready_chunks = combine_sentences(chunks, tok_val_list, max_tokens_per_chunk)

# loop through each chunk and process it
for chunk in ready_chunks:

    # encode the question and chunk
    encoding = tokenizer.encode_plus(question, chunk, max_length=512, truncation=True, return_tensors="pt")
    input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

    # pass the encoded input through the model to obtain start and end scores for answer spans
    start_scores, end_scores = model(input_ids, attention_mask=attention_mask, return_dict=False)

    # determine the answer tokens based on the highest start and end scores
    ans_tokens = input_ids[0, torch.argmax(start_scores) : torch.argmax(end_scores) + 1]
    answer_tokens = tokenizer.convert_ids_to_tokens(ans_tokens, skip_special_tokens=True)

    # append the answer tokens to the final answer
    final_answer_tokens += answer_tokens

# convert the final answer tokens back into a string answer
answer = tokenizer.convert_tokens_to_string(final_answer_tokens)

print("\nQuestion: ", question)
print("\nAnswer Tokens: ")
print(final_answer_tokens)
print("\Answer: ", answer)
