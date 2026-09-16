"""Cache a bounded, pinned banking subset while the full checkout downloads."""
import json
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

REV = "2174a603f6d014ef94473ffa95957f6ce27100db"
tree = json.loads(Path("downloads/tau-tree.json").read_text())["tree"]
paths = [x["path"] for x in tree if "/banking_knowledge/documents/doc_checking_accounts_" in x["path"]]
out = Path("downloads/checking")
out.mkdir(exist_ok=True)

def fetch(path):
    dest = out / Path(path).name
    if not dest.exists():
        req = urllib.request.Request(f"https://raw.githubusercontent.com/sierra-research/tau2-bench/{REV}/{path}", headers={"User-Agent": "memory-placement-study/0.1"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    return json.loads(dest.read_text())

for doc in ThreadPoolExecutor(max_workers=4).map(fetch, paths):
    print(doc["id"], doc["title"])
    if doc["id"].endswith("001"):
        print(doc["content"])
