import re


def tokenize_verse(text):
    main_re = "([།༔གཀཤ] ?[།༔] ?)"
    verses = re.split(main_re,text)
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

