import re
from pathlib import Path
new_re = "([།]+ *)+"

def tokenize_verse(text):
    text = text.replace("\n","")
    main_re =  "([།༔]+ ?[།༔]*)"
    verses = re.split(main_re,text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"་\s?་+", "་", text)

    tokenized_sentence = []
    prev_element = ""
    for verse in verses:
        if re.search(main_re,verse):
            if tokenized_sentence and tokenized_sentence[-1] in ("༄༅༅། །","༄། །"):
                tokenized_sentence[-1] = tokenized_sentence[-1]+prev_element+verse
            else:
                tokenized_sentence.append(prev_element+verse)
        prev_element = verse    
    return tokenized_sentence


if __name__ == "__main__":
    text = Path("tests/data/elem.txt").read_text(encoding="utf-8")
    verses = tokenize_verse(text)
    new_text =""
    for verse in verses:
        new_text+=verse+"\n"
    Path("demo.txt").write_text(new_text)
