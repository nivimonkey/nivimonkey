import json
from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel

# Define data classes for the required information
@dataclass
class Token:
    id: str
    text: str
    lemma: str
    pos: str
    feats: str

@dataclass
class LemmaInfo:
    lemma: str
    pos: str
    inflection: List[str] = field(default_factory=list)
    wordform_count: int = 0

# Parse the JSON file and extract the required information
def process_json_file(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    lemmas_info = {}
    for sentence in data['sentences']:
        for token_data in sentence['tokens']:
            lemma = token_data['lemma']
            pos = token_data['pos_finegrained']
            inflection = token_data.get('feats', None)

            if lemma not in lemmas_info:
                lemmas_info[lemma] = LemmaInfo(lemma=lemma, pos=pos, inflection=[inflection] if inflection else [])
            else:
                lemma_info = lemmas_info[lemma]
                if inflection and inflection not in lemma_info.inflection:
                    lemma_info.inflection.append(inflection)

            lemmas_info[lemma].wordform_count += 1

    return lemmas_info

# Convert data classes to JSON-compatible format
class LemmaInfoOutput(BaseModel):
    lemma: str
    pos: str
    inflection: List[str] = []
    total_frequency: int
    wordform_frequency: int

    class Config:
        allow_population_by_field_name = True

# Generate the output JSON file
def generate_output_json(output_file_path, lemmas_info):
    output_data = []
    for lemma_info in lemmas_info.values():
        total_frequency = sum(lemma.wordform_count for lemma in lemmas_info.values() if lemma.lemma == lemma_info.lemma)
        output_data.append(dict(LemmaInfoOutput(**lemma_info.__dict__, total_frequency=total_frequency, wordform_frequency=lemma_info.wordform_count)))

    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_file_path = "C:\\Users\\Ariselab\\Downloads\\sample_parsed_sentences.json"
    output_file_path = "output.json"

    lemmas_info = process_json_file(input_file_path)
    generate_output_json(output_file_path, lemmas_info)

