from search import search
from pathlib import Path
from . import PROJECT_PATH

def test_search():
    
    search_elem = Path("./test/data/elem.txt").read_text(encoding="utf-8")
    pool_text = Path("./test/data/pool.txt").read_text(encoding="utf-8")
    expected_result = Path("./test/data/expected_result.txt").read_text(encoding="utf-8")
    start,end = search(search_elem,pool_text)
    assert expected_result==pool_text[start:end]
