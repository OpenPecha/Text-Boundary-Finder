from pathlib import Path
from search import TextSearcher
import yaml
import os
import re
from verse_tokenizer import tokenize_verse
from fuzzysearch import find_near_matches
import random

try:
    yaml_loader = yaml.CSafeLoader
except (ImportError, AttributeError):
    yaml_loader = yaml.SafeLoader

def load_yaml(fn: Path) -> None:
    return yaml.load(fn.open(encoding="utf-8"), Loader=yaml_loader)

def get_meta(opf_path):
    pecha_id = Path(opf_path).stem
    meta_path = f"{opf_path}/{pecha_id}.opf/meta.yml"
    meta = load_yaml(Path(meta_path))
    return meta

def get_bases_path(opf_path):
    meta = get_meta(opf_path)
    base_file_path = f"{opf_path}/{Path(opf_path).stem}.opf/base"
    if "bases" not in meta.keys() or meta["bases"] is None:
        bases = list(Path(base_file_path).iterdir())
        bases = [base.as_posix() for base in bases]
        bases = sorted(bases, key=lambda path: os.path.basename(path))
    else:
        bases = meta["bases"].keys()
        bases = [f"{opf_path}/{Path(opf_path).stem}.opf/base/{base}.txt" for base in bases]
    return bases

def fuzzy_search(elem, pool):
    matches = find_near_matches(elem, pool, max_l_dist=int(len(elem)/4))
    return matches

def get_random_element(lst):
    random_element = random.choice(lst)
    return random_element

def remove_english_words_and_numbers(text):
    pattern = r'\b[a-zA-Z]+\b|\b[0-9]+\b'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def search_text_in_opf(opf_path,target_text):
    bases_path = get_bases_path(opf_path)
    for base_path in bases_path:
        print(base_path)
        matches = 0
        base_text = Path(base_path).read_text(encoding="utf-8")
        searcher = TextSearcher()
        base_text=remove_english_words_and_numbers(base_text)
        verses = tokenize_verse(target_text)
        for i in range(10):
            random_elem = get_random_element(verses)
            cur_matches = fuzzy_search(random_elem,base_text)
            if cur_matches:
                matches+=1
        if matches > 5:
            span = searcher.search_text(target_text,base_text)
            if span:
                start,end = span
                return base_text[start:end]

if __name__ == "__main__":
    opf_path="data/I4DBEE949"
    target_text = Path("data/target.txt").read_text(encoding="utf-8")
    span = search_text_in_opf(opf_path,target_text)