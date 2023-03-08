from fuzzysearch import find_near_matches
from pathlib import Path
from pathlib import Path
import numpy as np
from verse_tokenizer import tokenize_verse
import os

len_of_searched_elem = 30

def fuzzy_search(elem,pool):
    matches = find_near_matches(elem,pool,max_l_dist=5)
    return matches

def get_elements(text):
    verses = tokenize_verse(text)
    first_elems = verses[0:3]
    last_elems = verses[-3:]
    mid_elems = verses[int(len(verses)/2)-1:int(len(verses)/2)+2]
    
    return (first_elems,mid_elems,last_elems)

def fuzzy_searches(elems,pool):
    matches = []
    for elem in elems:
        matches.append(fuzzy_search(elem,pool))

    return matches

def closest_value(input_list, input_value,matches_comb):
  arr = np.asarray(input_list)
  i = (np.abs(arr - input_value)).argmin()
  return i

def get_closest_match(matches_comb,len_pool_text):
    dists = []
    for match_comb in matches_comb:
        first_match,mid_match,last_match = match_comb
        valid_order = check_valid_order(match_comb)
        if not valid_order:
            dists.append(0)
            continue
        cur_dist = last_match.end - first_match.start
        dists.append(cur_dist)
    i = closest_value(dists,len_pool_text,matches_comb)
    return matches_comb[i]

def get_total_len_of_list_elems(elems):
    total_len= 0
    for elem in elems:
        total_len+=len(elem)
    return total_len

def get_nearest_match(matches_comb,len_of_total_elems):
    nearest_matches = []
    standard_threshold = int(len_of_total_elems/3*0.3)
    for match_comb in matches_comb:
        first_match,mid_match,last_match = match_comb
        valid_order = check_valid_order(match_comb)
        if not valid_order:
            continue
        if (mid_match.start-first_match.end) < standard_threshold and (last_match.start-mid_match.end) < standard_threshold:
            nearest_matches.append(match_comb)

    return nearest_matches        


def check_valid_order(match_comb):
    first_match,mid_match,last_match = match_comb
    if first_match.end <= mid_match.start and mid_match.end <= last_match.start:
        return True
    return False

def get_boundary_matches(elems,pos):
    ret_elem = []
    elems_matches = fuzzy_searches(elems,pool_text)
    len_of_total_elems = get_total_len_of_list_elems(elems)
    matches_comb = []
    first_seg_matches,second_seg_matches,third_seg_matches = elems_matches
    for first_seg_match in first_seg_matches:
        for second_seg_match in second_seg_matches:
            for third_seg_match in third_seg_matches:
                matches_comb.append([first_seg_match,second_seg_match,third_seg_match])

    closest_matches = get_nearest_match(matches_comb,len_of_total_elems)
    for closest_match in closest_matches:
        if pos == "first":
            ret_elem.append(closest_match[0])
        elif pos == "last":
            ret_elem.append(closest_match[-1])
        else:
            ret_elem.append(closest_match[1])
    return ret_elem


def search(searched_elem,pool_text):
    matches_comb = []
    first_elems,mid_elems,last_elems = get_elements(searched_elem)
    first_matches = get_boundary_matches(first_elems,pos="first")
    mid_matches = get_boundary_matches(mid_elems,pos="mid")
    last_matches = get_boundary_matches(last_elems,pos="last")

    for first_match in first_matches:
        for mid_match in mid_matches:
            for last_match in last_matches:
                matches_comb.append((first_match,mid_match,last_match))

    closest_match = get_closest_match(matches_comb,len(pool_text))
    first_match,_,last_match= closest_match
    start = first_match.start
    end = last_match.end

    return start,end

if __name__ == "__main__":
    pwd = os.getcwd()
    search_text = Path("./tests/data/elem.txt").read_text(encoding="utf-8")
    pool_text = Path("./tests/data/pool.txt").read_text(encoding="utf-8")
    start,end = search(search_text,pool_text)
    Path("./tests/data/result.txt").write_text(pool_text[start:end])