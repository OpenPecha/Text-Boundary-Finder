from text_boundary_finder.search import search
from pathlib import Path


def test_search():
    search_elem = Path("./tests/data/elem.txt").read_text(encoding="utf-8")
    pool_text = Path("./tests/data/pool.txt").read_text(encoding="utf-8")
    expected_result = Path("./tests/data/expected_result.txt").read_text(encoding="utf-8")
    start,end = search(search_elem,pool_text)
    assert expected_result==pool_text[start:end]
