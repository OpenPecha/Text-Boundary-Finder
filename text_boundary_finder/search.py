from fuzzysearch import find_near_matches
from pathlib import Path
from verse_tokenizer import tokenize_verse

class TextSearcher:

    def fuzzy_search(self, elem, pool):
        matches = find_near_matches(elem, pool, max_l_dist=int(len(elem)/4))
        return matches


    def fuzzy_searches(self, elems, pool):
        matches = []
        for elem in elems:
            matches.append(self.fuzzy_search(elem, pool))
        return matches
    

    def get_elements(self, text):
        verses = tokenize_verse(text)
        first_elems = verses[0:3]
        last_elems = verses[-3:]
        mid_elems = verses[int(len(verses)/2)-1:int(len(verses)/2)+2]
        return (first_elems, mid_elems, last_elems)


    def get_closest_value(self,input_list, input_value):
        min_diff = float('inf')
        closest_index = None

        for i, value in enumerate(input_list):
            diff = abs(value - input_value)
            if diff < min_diff:
                min_diff = diff
                closest_index = i

        return closest_index


    def get_total_len_of_list_elems(self, elems):
        total_len= 0
        for elem in elems:
            total_len+=len(elem)
        return total_len


    def is_order_valid(self, match_comb):
        first_match, mid_match, last_match = match_comb
        if first_match.end <= mid_match.start and mid_match.end <= last_match.start:
            return True
        return False
    

    def get_closest_match(self, matches_comb, len_pool_text):
        len_of_texts = []
        for match_comb in matches_comb:
            first_match, _, last_match = match_comb
            valid_order = self.is_order_valid(match_comb)
            if not valid_order:
                len_of_texts.append(0)
                continue
            cur_len_of_text = last_match.end - first_match.start
            len_of_texts.append(cur_len_of_text)
        i = self.get_closest_value(len_of_texts, len_pool_text)
        return matches_comb[i]


    def get_nearest_match(self, matches_comb, len_of_total_elems):
        nearest_matches = []
        standard_threshold = int(len_of_total_elems/3*0.3)
        for match_comb in matches_comb:
            first_match, mid_match, last_match = match_comb
            valid_order = self.is_order_valid(match_comb)
            if not valid_order:
                continue
            elif (mid_match.start - first_match.end) < standard_threshold and (last_match.start - mid_match.end) < standard_threshold:
                nearest_matches.append(match_comb)
        return nearest_matches


    def get_boundary_matches(self, elems, pool_text, pos):
        boundary_matches = []
        matches_comb = []
        elems_matches = self.fuzzy_searches(elems, pool_text)
        len_of_total_elems = self.get_total_len_of_list_elems(elems)
        first_seg_matches, second_seg_matches, third_seg_matches = elems_matches
        if 0 in (len(first_seg_matches), len(second_seg_matches), len(third_seg_matches)):
            return
        for first_seg_match in first_seg_matches:
            for second_seg_match in second_seg_matches:
                for third_seg_match in third_seg_matches:
                    matches_comb.append([first_seg_match, second_seg_match, third_seg_match])
        closest_matches = self.get_nearest_match(matches_comb, len_of_total_elems)
        for closest_match in closest_matches:
            if pos == "first":
                boundary_matches.append(closest_match[0])
            elif pos == "last":
                boundary_matches.append(closest_match[-1])
            else:
                boundary_matches.append(closest_match[1])
        return boundary_matches


    def search_text(self,target_text,pool_text):
        matches_comb = []
        first_elems,mid_elems,last_elems = self.get_elements(target_text)
        first_matches = self.get_boundary_matches(first_elems,pool_text,pos="first")
        mid_matches = self.get_boundary_matches(mid_elems,pool_text,pos="mid")
        last_matches = self.get_boundary_matches(last_elems,pool_text,pos="last")
        if None in (first_matches,mid_matches,last_matches):
            return
        for first_match in first_matches:
            for mid_match in mid_matches:
                for last_match in last_matches:
                    matches_comb.append((first_match,mid_match,last_match))
        closest_match = self.get_closest_match(matches_comb,len(pool_text))
        first_match,_,last_match= closest_match
        start = first_match.start
        end = last_match.end
        return start,end
    

if __name__ == "__main__":
    obj = TextSearcher()
    pool_text = Path("I2KG212406.txt").read_text(encoding="utf-8")
    target_text = "ཡིད་ཀྱིས་ཀུན་ནས་སློང་བ་དེ་ནི་ལེན་པའི་རྐྱེན་གྱིས་སྲིད་པ་ཞེས་བྱའོ།"
    match = obj.fuzzy_search(target_text,pool_text)
    print(match)
