from fuzzysearch import find_near_matches
from pathlib import Path
from pathlib import Path
import numpy as np

len_of_searched_elem = 30

def fuzzy_search(elem,pool):
    matches = find_near_matches(elem,pool,max_l_dist=5)
    return matches

def get_elements(text):
    first_elem = text[:len_of_searched_elem]
    last_elem = text[-len_of_searched_elem:]
    mid_elem = text[int(len(text)/2)-int(len_of_searched_elem/2):int(len(text)/2)+int(len_of_searched_elem/2)]
    return (first_elem,mid_elem,last_elem)

def closest_value(input_list, input_value,matches_comb):
  arr = np.asarray(input_list)
  i = (np.abs(arr - input_value)).argmin()
  return matches_comb[i]

def get_closest_match(matches_comb,len_pool_text):
    dists = []
    for match_comb in matches_comb:
        first_match,_,last_match = match_comb
        cur_dist = last_match.end - first_match.start
        dists.append(cur_dist)
        """ if not closest_dist:
            closest_dist = cur_dist
            closest_match = (first_match.start,last_match.end)
        elif cur_dist < closest_dist:
            closest_dist = cur_dist
            closest_match = (first_match.start,last_match.end) """
    val = closest_value(dists,len_pool_text,matches_comb)
    return val

def search(searched_elem,pool_text):
    matches_comb = []
    first_elem,mid_elem,last_elem = get_elements(searched_elem)
    first_matches = fuzzy_search(first_elem,pool_text)
    mid_matches = fuzzy_search(mid_elem,pool_text)
    last_matches = fuzzy_search(last_elem,pool_text)

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
    search_text = Path("test/data/elem.txt").read_text(encoding="utf-8")
    pool_text = Path("test/data/pool.txt").read_text(encoding="utf-8")
    segs = search(search_text,pool_text)