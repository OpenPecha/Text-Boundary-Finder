from pathlib import Path
import search
import yaml
import os

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
        bases = [f"{opf_path}/{Path(opf_path).stem}/opf/base{base}" for base in bases]
    return bases


def get_text_from_opf(opf_path,target_text):
    bases_path = get_bases_path(opf_path)
    for base_path in bases_path:
        print(base_path)
        base_text = Path(base_path).read_text(encoding="utf-8")
        span = search.search_text(target_text,base_text)
        if span:
            print(span)


if __name__ == "__main__":
    opf_path="data/P000800"
    target_text = Path("data/target.txt").read_text(encoding="utf-8")
    get_text_from_opf(opf_path,target_text)