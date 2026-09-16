"""Pinned document adaptation; gold is generated separately from model inputs."""
import copy
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "downloads/tau2-bench/data/tau2/domains/banking_knowledge/documents"
SELECTED = {
    "blue_account": [1, 2, 12],
    "light_green_account": [1, 2, 13],
    "dark_green_account": [1, 2],
    "gold_years_account": [1, 2],
    "purple_account": [1],
    "green_account_(checking)": [1],
}
ACCOUNTS = ["Blue Account", "Light Green Account", "Dark Green Account", "Gold Years Account"]

def documents(version="v0"):
    docs = [json.loads((BASE / f"doc_checking_accounts_{name}_{i:03d}.json").read_text())
            for name, numbers in SELECTED.items() for i in numbers]
    docs.sort(key=lambda d: d["id"])
    for d in docs:
        if version in ("narrow", "broad") and "_blue_account_" in d["id"]:
            d["content"] = d["content"].replace("$625", "$900")
        if version == "broad" and "_light_green_account_" in d["id"]:
            d["content"] = d["content"].replace("24 years", "22 years").replace("13–24", "13–22")
        if version == "broad" and "_gold_years_account_" in d["id"]:
            d["content"] = d["content"].replace("62", "65")
        d["sha256"] = hashlib.sha256(d["content"].encode()).hexdigest()
    return docs

def make_case(rng, idx, family, shifted, version, prefix):
    account=ACCOUNTS[family]
    if not shifted:
        if family == 0:
            values = rng.sample(range(400,1101),3)
            question = f"For three separate {account} customers with minimum daily balances of {values} dollars, is the monthly maintenance fee waived for each? Return booleans in the given order."
            gold=[x >= (625 if version == "v0" else 900) for x in values]
            old=[x >= 625 for x in values]
            support=["blue_account_001", "blue_account_002"]
        else:
            low, high = {1:(10,29),2:(14,31),3:(55,74)}[family]
            values=rng.sample(range(low,high),3)
            question=f"For three separate prospective {account} primary holders aged {values} years, does each meet the age requirement? Assess age only; assume all other requirements are met. Return booleans in the given order."
            bounds={1:(13,22 if version=="broad" else 24),2:(17,26),3:(65 if version=="broad" else 62,200)}
            lo,hi=bounds[family]
            gold=[lo<=x<=hi for x in values]
            olo,ohi={1:(13,24),2:(17,26),3:(62,200)}[family]
            old=[olo<=x<=ohi for x in values]
            support={1:["light_green_account_002"],2:["dark_green_account_001","dark_green_account_002"],3:["gold_years_account_001","gold_years_account_002"]}[family]
    else:
        maxima={0:450,1:149,2:299,3:599}
        # The source does not specify half-cent rounding. Even dollar amounts
        # make the 2.5% fee exact in cents, avoiding an invented policy rule.
        values=rng.sample(range(20,maxima[family],2 if family==2 else 1),3)
        balances=rng.sample(range(8000,12001),3)
        question=f"Three {account} customers each made one successful foreign ATM withdrawal on a separate day. The USD-equivalent amounts were {values} dollars, and their respective account balances at withdrawal were {balances} dollars. What Rho-Bank foreign ATM fee applies to each? Exclude third-party fees. Return dollar amounts in the given order."
        gold=([round(max(.03*x,5),2) for x in values] if family==0 else
              [2.0 if x<=100 else 3.5 for x in values] if family==1 else
              [round(min(.025*x,6),2) for x in values] if family==2 else
              [0.0 if b>=10000 else 3.5 for b in balances])
        old=gold
        support={0:["blue_account_012"],1:["light_green_account_013"],2:["dark_green_account_002"],3:["gold_years_account_002"]}[family]
    return dict(id=f"{prefix}-{idx:03d}",question=question,family=family,shifted=shifted,version=version,
                gold=gold,old_gold=old,affected=gold!=old,
                supports=["doc_checking_accounts_"+x for x in support])

def stream(seed, n, version="v0", shifted=False, prefix="stable", seen=None):
    rng=random.Random(seed)
    families=list(range(4))*(n//4)
    assert len(families)==n
    rng.shuffle(families)
    # In shifted streams, every fourth request remains in the old family.
    seen=set() if seen is None else seen
    cases=[]
    for i,f in enumerate(families):
        while True:
            case=make_case(rng,i,f,shifted and i%4!=0,version,prefix)
            if case['question'] not in seen:break
        seen.add(case['question']);cases.append(case)
    return cases

def dump_json(path, data):
    Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
