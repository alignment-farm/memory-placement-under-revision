"""Cheap account-aware BM25, using only public document IDs and request text."""
import re
from rank_bm25 import BM25Okapi

def tokens(text):return re.findall(r'[a-z]+|\d+',text.lower())

class Index:
    def __init__(self,docs):
        self.docs=docs
        self.index=BM25Okapi([tokens(d['title']+' '+d['content']) for d in docs])
        self.names={re.sub(r'_\d+$','',d['id'].removeprefix('doc_checking_accounts_')).replace('_',' ') for d in docs}
    def scores(self,question,entity=False):
        scores=dict(zip((d['id'] for d in self.docs),map(float,self.index.get_scores(tokens(question)))))
        if entity:
            matched=sorted((n for n in self.names if n.lower() in question.lower()),key=len,reverse=True)
            if matched:
                stem='doc_checking_accounts_'+matched[0].replace(' ','_')+'_'
                bonus=max(scores.values())-min(scores.values())+1
                for mid in scores:
                    if mid.startswith(stem):scores[mid]+=bonus
        return scores
