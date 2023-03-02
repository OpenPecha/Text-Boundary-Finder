from fuzzysearch import find_near_matches
from pathlib import Path

from text_boundary_finder.verse_tokenizer import tokenize_verse
from text_boundary_finder.seg import Seg


def push_segments(obj,texts):
    for text in texts:
        obj.push(text)

def fuzzy_search(elem,pool):
    max_l_dist = int(0.3*len(elem))
    matches = find_near_matches(elem,pool,max_l_dist=max_l_dist)
    return matches

def get_nearest_match(prev_match,cur_matches):
    nearest_match = None
    least_dist = None
    for cur_match in cur_matches:
        dist_two_seg = abs((prev_match.end+prev_match.start)/2-(cur_match.end+cur_match.start)/2)
        actual_dist_two_seg = int((prev_match.end-prev_match.start)/2+(cur_match.end-cur_match.start)/2)
        excepted_dist_range = range(int(actual_dist_two_seg-0.2*actual_dist_two_seg),int(actual_dist_two_seg+0.2*actual_dist_two_seg))
        if least_dist == None:
            least_dist = dist_two_seg+1
        if dist_two_seg < least_dist and dist_two_seg in excepted_dist_range:
            least_dist = dist_two_seg
            nearest_match = cur_match

    return nearest_match

def traverse_right(mid_seg,mid_match,pool_text):
    cur_seg = mid_seg.next
    prev_match = mid_match
    while cur_seg != None:
        cur_matches = fuzzy_search(cur_seg.data,pool_text)
        nearest_match = get_nearest_match(prev_match,cur_matches)
        if not nearest_match:
            return
        prev_match = nearest_match
        cur_seg = cur_seg.next
    
    return prev_match.end


def traverse_left(mid_seg,mid_match,pool_text):
    cur_seg = mid_seg.prev
    prev_match = mid_match
    while cur_seg != None:
        cur_matches = fuzzy_search(cur_seg.data,pool_text)
        nearest_match = get_nearest_match(prev_match,cur_matches)
        if not nearest_match:
            return 
        prev_match = nearest_match
        cur_seg = cur_seg.prev
    
    return prev_match.start


def get_spans(search_elem_obj,pool_text):
    spans = []
    mid_seg = search_elem_obj.getMiddle()
    mid_matches = fuzzy_search(mid_seg.data,pool_text)
    if not mid_matches:
        return
    for mid_match in mid_matches:
        start = traverse_left(mid_seg,mid_match,pool_text)
        end = traverse_right(mid_seg,mid_match,pool_text)   
        if start is not None and end is not None: 
            spans.append((start,end))
    return spans

def search(search_elem,pool_text):
    search_elem_verses = tokenize_verse(search_elem)
    search_elem_obj = Seg()
    push_segments(search_elem_obj,search_elem_verses)
    spans = get_spans(search_elem_obj,pool_text)
    return spans

if __name__ == "__main__":
    search_elem = Path("tests/data/sample_elem.txt").read_text(encoding="utf-8")
    pool_text = Path("tests/data/sample_pool.txt").read_text(encoding="utf-8")
    spans = search(search_elem,pool_text)
    start,end = spans[0]
    Path("tests/data/result.txt").write_text(pool_text[start:end])

