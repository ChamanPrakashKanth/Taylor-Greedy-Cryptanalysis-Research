#!/usr/bin/env python3
"""WalkSAT-like control for the follow-up benchmark, paired on the same SAT instances and starts."""
from __future__ import annotations
import csv
import random
import time
from pathlib import Path
import numpy as np
import taylor_greedy_followup as tg

OUT=Path('results/raw')
PROB_NOISE=0.5


def solve_walksat(p, start, seed):
    rng=random.Random(seed)
    x=start
    e=p.energy(x)
    best=e
    scores=0
    accepted=0
    picks=0
    t0=time.perf_counter()
    while scores+3<=tg.BUDGET and best>0:
        bit = (np.right_shift(np.uint64(x),p.ids.astype(np.uint64)) & np.uint64(1))
        unsat=np.flatnonzero(np.all(bit!=p.signs,axis=1))
        if len(unsat)==0:
            assert e==0
            break
        ci=int(unsat[rng.randrange(len(unsat))])
        variables=p.ids[ci]
        vals=[p.energy(x ^ (1<<int(i))) for i in variables]
        scores+=3
        if rng.random()<PROB_NOISE:
            selected=rng.randrange(3)
        else:
            candidates=[i for i in range(3) if vals[i]==min(vals)]
            selected=candidates[rng.randrange(len(candidates))]
        x ^= 1<<int(variables[selected])
        e=vals[selected]
        best=min(e,best)
        accepted+=1
        picks+=1
    return {'hit':int(best==0),'best_unsat':best,'candidates':scores,
            'derivative_builds':0,'accepted':accepted,'restarts':0,
            'kicks':0,'pair_neighborhoods':0,'triple_neighborhoods':0,
            'elapsed_ms':(time.perf_counter()-t0)*1000}


def main():
    rng=random.Random(tg.SEED)
    more=[]
    for n in tg.SIZES:
        for ins in range(tg.INSTANCES):
            p=tg.generate(n,rng)
            for si in range(tg.STARTS):
                start=rng.getrandbits(n)
                seed=tg.SEED+n*1000003+ins*10007+si*313+999
                res=solve_walksat(p,start,seed)
                more.append(dict(variables=n,instance=ins,start_index=si,
                            method='walksat',clauses=len(p.ids),budget=tg.BUDGET,**res))
        print('WalkSAT completed N',n,flush=True)
    with (OUT/'taylor_greedy_followup_results.csv').open() as f:
        old=list(csv.DictReader(f))
    cols=list(old[0].keys())
    full=old+more
    with (OUT/'taylor_greedy_followup_with_walksat.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(full)
    print('Success rates',flush=True)
    for n in tg.SIZES:
        r=[a for a in more if a['variables']==n]
        print(n,sum(a['hit'] for a in r),'/',len(r),'median score',np.median([a['candidates'] for a in r]), 'median wall ms',np.median([a['elapsed_ms'] for a in r]),flush=True)

if __name__=='__main__':main()
