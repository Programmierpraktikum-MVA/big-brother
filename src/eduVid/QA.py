# question answering lib
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
# s2t lib
from faster_whisper import WhisperModel

# helper func to combine separate sentences into one array element within the limit
def combine_sentences(self, sentences, value, limit):
  result = []
  current_sentence = ''
  temp_sum = 0

  for sent, val in zip(sentences, value):
    temp_sum += val
    if temp_sum <= limit:
      current_sentence += sent
    else:
      result.append(current_sentence)
      current_sentence = sent
      temp_sum = 0

  if current_sentence:
    result.append(current_sentence)

  return result

# helper func to count how many tokens are used for each sentence. values are stored in array
def count_tokens(self, chunks, tokenizer):
  self.tokenizer = tokenizer
  sentence_token_counts = []
  for elem in chunks:
    sentences = elem.split('.')
    for sentence in sentences:
      sentence_tokens = self.tokenizer.encode(sentence, add_special_tokens=False)
      sentence_token_count = len(sentence_tokens) + 1
      sentence_token_counts.append(sentence_token_count)
  return sentence_token_counts[::2]

# helper func to merge overlapping segments (ex. array - [(13.0, 26.0), (26.0, 39.0)] can be merged into [(13.0, 39.0)])
def merge_overlapping_segments(segments):
  if not segments:
    return []

  # sort segments based on start time
  segments.sort(key=lambda x: x[0])
  merged_segments = [segments[0]]

  for segment in segments[1:]:
    # check for overlap
    if segment[0] <= merged_segments[-1][1]:
      merged_segments[-1] = (merged_segments[-1][0], max(merged_segments[-1][1], segment[1]))
    else:
      merged_segments.append(segment)

  return merged_segments

# helper func to search for matching segments (has answer as a list of words, if at least 2 of them one by one are overlapping with segment from tag_array - append)
def find_matching_segments(tag_array, answer):
  matching_segments = []
  answer_words = answer.split()
  answer_pairs = [" ".join(pair) for pair in zip(answer_words, answer_words[1:])]

  for segment in tag_array:
    segment_words = segment[2].split()
    segment_pairs = [" ".join(pair) for pair in zip(segment_words, segment_words[1:])]

    for pair in answer_pairs:
      if pair in segment_pairs:
        matching_segments.append((segment[0], segment[1]))
        break

  return matching_segments

# TODO
# add progress bar
class SpeechRecog:
  def __init__ (self, audio_source):
    self.model = WhisperModel("base")
    self.segments, self.info = self.model.transcribe(audio_source)
    
  def transcribe(self):
    transcription_list = []
    tag_array=[]
    for self.segment in self.segments:
      transcription_list.append(self.segment.text)
      tag_array.append([self.segment.start, self.segment.end, self.segment.text])
    script = ''.join(transcription_list)

    return script, tag_array

class QAAlgo:
  # define the maximum number of tokens per chunk (model limitations - 512)
  def __init__(self, model_name, max_tokens_per_chunk=512):
    # settings for hugging face model
    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    self.max_tokens_per_chunk = max_tokens_per_chunk

  def answer_question(self, context, question):
    # encode the full context to count the tokens
    context_tokens = self.tokenizer.encode(context, add_special_tokens=False)

    start_idx = 0
    chunks = []

    # split entire context into separate sentences
    while start_idx < len(context_tokens):
      # find the next sentence boundary (period)
      next_period_idx = context_tokens[start_idx:].index(self.tokenizer.convert_tokens_to_ids(".")) + start_idx
      if next_period_idx - start_idx <= self.max_tokens_per_chunk:
        # if the next sentence fits within the chunk, include it
        end_idx = next_period_idx + 1
      else:
        # if the next sentence doesn't fit, use the max_tokens_per_chunk limit
        end_idx = start_idx + self.max_tokens_per_chunk

      chunk_tokens = context_tokens[start_idx:end_idx]
      chunk_text = self.tokenizer.decode(chunk_tokens)
      chunks.append(chunk_text)
      start_idx = end_idx

    # create list with token values
    tok_val_list = count_tokens(self, chunks, self.tokenizer)
    # create ready chunks
    ready_chunks = combine_sentences(self, chunks, tok_val_list, self.max_tokens_per_chunk)

    final_answer_tokens = []
    # loop through each chunk and process it
    for chunk in ready_chunks:
      # encode the question and chunk
      encoding = self.tokenizer.encode_plus(question, chunk, max_length=512, truncation=True, return_tensors="pt")
      input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]
      # pass the encoded input through the model to obtain start and end scores for answer spans
      start_scores, end_scores = self.model(input_ids, attention_mask=attention_mask, return_dict=False)
      # determine the answer tokens based on the highest start and end scores
      ans_tokens = input_ids[0, torch.argmax(start_scores): torch.argmax(end_scores) + 1]
      answer_tokens = self.tokenizer.convert_ids_to_tokens(ans_tokens, skip_special_tokens=True)
      # append the answer tokens to the final answer
      final_answer_tokens += answer_tokens

    # convert the final answer tokens back into a string answer
    answer = self.tokenizer.convert_tokens_to_string(final_answer_tokens)
    return answer

# Usage
model_name = "timpal0l/mdeberta-v3-base-squad2"
# perform s2t
recog = SpeechRecog('audio.mp3')
# define context
context, tags = recog.transcribe()

# ask a question
question = 'Wenn reicht die Prolog Geschichte?'

# handle question answering 
qa_result = QAAlgo(model_name)
answer = qa_result.answer_question(context, question)
# handle segments time
matching_segments = find_matching_segments(tags, answer)
merged_segments = merge_overlapping_segments(matching_segments)

print("\nQuestion:", question)
print("\nAnswer:", answer)
print("\nTime in seconds:", merged_segments)
