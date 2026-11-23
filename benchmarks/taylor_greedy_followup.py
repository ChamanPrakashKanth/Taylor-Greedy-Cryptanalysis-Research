#!/usr/bin/env python3
"""Independent controlled Taylor/greedy SAT benchmark.

The multilinear violated-clause objective is degree <=3, so Taylor order 3
is exact for *every* Boolean assignment. Compare first-order greedy,
first-order restart, exact 2-bit lookahead restart, selective exact third-order
lookahead restart, and random perturbation under a capped number of scored
candidate moves. This is a heuristic experiment, not a complexity result.
"""
from __future__ import annotations
import csv
import itertools
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
import numpy as np

OUT = Path('results/raw')
SEED = 20261123
SIZES = (12, 20, 32, 48, 64)
INSTANCES = 12
STARTS = 3
CLAUSE_RATIO = 4.3
BUDGET = 5000
SELECT_K = 16
METHODS = ('greedy1', 'restart1', 'restart2', 'select3', 'kick1')

@dataclass
class SAT:
    n: int
    ids: np.ndarray
    signs: np.ndarray
    planted: int
    cubic: np.ndarray
    hsign: np.ndarray

    def energy(self, state: int) -> int:
        return int(np.count_nonzero(np.all(np.right_shift(np.uint64(state), self.ids.astype(np.uint64)) & np.uint64(1) != self.signs, axis=1)))

    def taylor(self, state: int):
        v = (np.right_shift(np.uint64(state), self.ids.astype(np.uint64)) & np.uint64(1) != self.signs).astype(np.int32)
        a, b, c = self.ids.T
        da, db, dc = self.hsign.T
        va, vb, vc = v.T
        g = np.zeros(self.n, dtype=np.int32)
        h = np.zeros((self.n, self.n), dtype=np.int32)
        np.add.at(g, a, da*vb*vc)
        np.add.at(g, b, db*va*vc)
        np.add.at(g, c, dc*va*vb)
        np.add.at(h, (a,b), da*db*vc)
        np.add.at(h, (a,c), da*dc*vb)
        np.add.at(h, (b,c), db*dc*va)
        sign = 1-2*np.array([(state>>i)&1 for i in range(self.n)], dtype=np.int32)
        return sign, g*sign, h * sign[:,None]*sign[None,:]


def generate(n: int, rng: random.Random) -> SAT:
    planted = rng.getrandbits(n)
    ids, signs = [], []
    for _ in range(round(CLAUSE_RATIO*n)):
        triple = sorted(rng.sample(range(n),3))
        while True:
            s = [rng.randrange(2) for _ in range(3)]
            if any(((planted>>i)&1)==v for i,v in zip(triple,s)):
                break
        ids.append(triple)
        signs.append(s)
    ia = np.array(ids, dtype=np.int64)
    sa = np.array(signs, dtype=np.int32)
    d = 1-2*sa
    cc = np.zeros((n,n,n), dtype=np.int32)
    a,b,c=ia.T
    np.add.at(cc,(a,b,c),d[:,0]*d[:,1]*d[:,2])
    problem=SAT(n,ia,sa,planted,cc,d)
    assert problem.energy(planted) == 0
    return problem


def combinations(n: int, k: int) -> np.ndarray:
    return np.array(list(itertools.combinations(range(n),k)), dtype=np.int64).reshape(-1,k)


def gains_for_moves(grad, hess, cubic, sign, moves):
    size = moves.shape[1]
    i=moves[:,0]
    if size == 1: return grad[i]
    j=moves[:,1]
    gain=grad[i]+grad[j]+hess[i,j]
    if size==2: return gain
    k=moves[:,2]
    return (gain + grad[k] + hess[i,k] + hess[j,k]
            + cubic[i,j,k]*sign[i]*sign[j]*sign[k])


def flipmask(row):
    return sum(1 << int(i) for i in row)


def verify_taylor() -> int:
    rng=random.Random(33445)
    count=0
    for n in (10,16,32,64):
        for _ in range(6):
            prob=generate(n,rng)
            x=rng.getrandbits(n)
            sign, grad, hess=prob.taylor(x)
            e=prob.energy(x)
            for k in (1,2,3):
                moves=np.array([sorted(rng.sample(range(n),k)) for i in range(20)], dtype=np.int64)
                delta=gains_for_moves(grad,hess,prob.cubic,sign,moves)
                for row,v in zip(moves,delta):
                    assert prob.energy(x ^ flipmask(row)) - e==int(v),(n,x,row,v)
                    count+=1
    return count


def solve(prob: SAT, start: int, method: str, seed: int, fullpairs: np.ndarray):
    n=prob.n
    rng=random.Random(seed)
    x=start
    e=prob.energy(x)
    best=e
    scores=0
    accepted=0
    restarts=0
    kicks=0
    builds=0
    pair_tries=0
    triple_tries=0
    t0=time.perf_counter()
    while scores<BUDGET and best>0:
        if scores+n > BUDGET: break
        sign,grad,hess=prob.taylor(x)
        builds+=1
        scores+=n
        choice=int(np.argmin(grad))
        delta=int(grad[choice])
        if delta<0:
            x ^= 1 << choice
            e += delta
            accepted+=1
        else:
            updated=False
            if method in ('restart2','select3'):
                if method == 'restart2':
                    pairs=fullpairs
                else:
                    # Prioritize interactions that could compensate for an
                    # individually unfavorable flip (adaptive Taylor guidance).
                    negative_interaction = np.minimum(hess,0)
                    priority = grad + negative_interaction.sum(axis=1)
                    selected=np.sort(np.argsort(priority,kind='stable')[:min(n,SELECT_K)])
                    pairs=selected[combinations(len(selected),2)]
                if scores+len(pairs)<=BUDGET:
                    pair_tries+=1
                    pd=gains_for_moves(grad,hess,prob.cubic,sign,pairs)
                    scores+=len(pairs)
                    ix=int(np.argmin(pd))
                    if pd[ix]<0:
                        x ^= flipmask(pairs[ix]); e+=int(pd[ix]); accepted+=1; updated=True
                if not updated and method=='select3':
                    triples=selected[combinations(len(selected),3)]
                    if scores+len(triples)<=BUDGET:
                        triple_tries+=1
                        td=gains_for_moves(grad,hess,prob.cubic,sign,triples)
                        scores+=len(triples)
                        ix=int(np.argmin(td))
                        if td[ix]<0:
                            x ^= flipmask(triples[ix]); e+=int(td[ix]); accepted+=1; updated=True
            if not updated:
                if method=='greedy1': break
                if method=='kick1':
                    if scores+1>BUDGET:break
                    # One explicit uphill/sideways perturbation, then greedily
                    # descend again. Count the actual candidate evaluation.
                    kk=2 if n>=2 else 1
                    bits=rng.sample(range(n),kk)
                    x ^= flipmask(bits)
                    e=prob.energy(x)
                    scores+=1
                    kicks+=1
                else:
                    if scores+n>BUDGET: break
                    x=rng.getrandbits(n)
                    e=prob.energy(x)
                    restarts+=1
            # end not updated
        assert e == prob.energy(x),'Exact Taylor score mismatch'
        best=min(best,e)
    elapsed=time.perf_counter()-t0
    return {'hit':int(best==0),'best_unsat':best,'candidates':scores,
            'derivative_builds':builds,'accepted':accepted,
            'restarts':restarts,'kicks':kicks,'pair_neighborhoods':pair_tries,
            'triple_neighborhoods':triple_tries,'elapsed_ms':elapsed*1000}


def ring_cost(n, x):
    y=[(x>>i)&1 for i in range(n)]
    return 2*sum(y[i]!=y[(i+1)%n] for i in range(n)) + ((1-y[0])*(1-y[1])*(1-y[2]))


def adversarial_check():
    checks=0
    for n in (12,20,32,48,64):
        assert ring_cost(n,0)==1 and ring_cost(n,(1<<n)-1)==0
        for k in (1,2,3):
            for bits in itertools.combinations(range(n),k):
                mask=flipmask(bits)
                assert ring_cost(n,mask)>=4
                checks+=1
    return checks


def main():
    print('Checking Taylor coefficients...',flush=True)
    checks=verify_taylor()
    print('Taylor comparisons pass:',checks,flush=True)
    trap=adversarial_check()
    print('Adversarial trap checks pass:',trap,flush=True)
    rows=[]
    rng=random.Random(SEED)
    for n in SIZES:
        pairs=combinations(n,2)
        for instance in range(INSTANCES):
            p=generate(n,rng)
            for s in range(STARTS):
                start=rng.getrandbits(n)
                for mi,method in enumerate(METHODS):
                    res=solve(p,start,method,SEED+n*1000003+instance*10007+s*313+mi*17,pairs)
                    rows.append({'variables':n,'instance':instance,'start_index':s,
                                 'method':method,'clauses':len(p.ids),'budget':BUDGET,**res})
        print('Finished N',n,'runs',len(rows),flush=True)
    csvfile=OUT/'taylor_greedy_followup_results.csv'
    with csvfile.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    report=[]
    report.append('# Taylor–Greedy controlled follow-up benchmark')
    report.append('')
    report.append('**Date:** 23 November 2026. **Result:** empirical heuristic comparison only, no theorem, and no cryptographic implications.')
    report.append(f'**Design:** {len(rows)} runs, {INSTANCES} planted-satisfiable random 3-SAT problems x {STARTS} shared starting states per size, N={SIZES}; {len(METHODS)} methods; clause ratio={CLAUSE_RATIO}; max {BUDGET} scored candidate moves each. The planted satisfying assignment certifies the global objective minimum zero. Fixed random seed={SEED}.')
    report.append(f'**Validation:** {checks} exact Taylor gain checks passed across 1-,2-,3-bit moves; {trap} adversarial ring-trap moves checked.')
    report.append('**Taylor model:** 3-SAT clause violations are multilinear polynomials of degree <=3. Derivatives of orders 1,2,3 are computed analytically. Third-order representation is exact globally, but searching all assignments is a separate problem.')
    report.append('**Methods:** greedy1=single-bit steepest descent, stop on plateau; restart1=greedy + random restarts; restart2=single-bit then exhaustive 2-bit improvements then restart; select3=single-bit then exact pair and triple changes restricted to a 16-variable interaction-ranked subset then restart; kick1=single-bit then random two-bit perturbations (may temporarily worsen objective).')
    report.append('**Budget fairness:** all methods have the same maximum number of candidate-move scores, not equivalent arithmetic operations. Derivative builds and CPU timings shown separately. No parameter tuning on test instances.')
    report.append('')
    report.append('| N | Method | Success | Median scored candidates | Median runtime (ms) | Median unsatisfied clauses |')
    report.append('|---:|---|---:|---:|---:|---:|')
    for n in SIZES:
        for method in METHODS:
            r=[a for a in rows if a['variables']==n and a['method']==method]
            hits=sum(a['hit'] for a in r)
            report.append(f'| {n} | {method} | {hits}/{len(r)} ({hits/len(r):.1%}) | {statistics.median(a["candidates"] for a in r):.0f} | {statistics.median(a["elapsed_ms"] for a in r):.2f} | {statistics.median(a["best_unsat"] for a in r):.1f} |')
    report.append('')
    report.append('## High-priority caveats')
    report.append('1. Planted-satisfiable random SAT is not a representative distribution of NP-complete instances; 0 is known to be feasible but not given to the solvers.')
    report.append('2. A local Taylor expansion is not an efficient global search oracle. The exact cubic representation does not make exhaustive search polynomial.')
    report.append('3. On binary SAT, raising Taylor order and increasing the move neighborhood are different operations; select3 uses exact cubic derivatives to evaluate chosen triple flips. A different search policy might work better or worse.')
    report.append('4. Candidate-score budgets are not CPU budgets. Runtime includes coefficient computation, temporary arrays, and candidate selection. Python runtime is platform-specific and affected by measurement noise.')
    report.append('5. Shared starting states permit paired method comparisons; outcomes for repeated starts of the same instance are not statistically independent.')
    report.append('6. Ring trap: E=2 sum_i (x_i-x_{i+1})^2+(1-x_1)(1-x_2)(1-x_3), cyclic boundary. E(0^N)=1, E(1^N)=0, and any other bitstring E>=4. Strictly improving k-bit local search with k<N cannot leave 0^N despite a globally exact cubic Taylor expansion. This is not a lower bound for arbitrary algorithms.')
    report.append('')
    report.append('## Follow-up')
    report.append('Compare against WalkSAT/GSAT and modern SAT solvers, multiple generators, matched wall-time budgets and larger independent samples; investigate learning a variable subset without requiring dense high-order tensors.')
    (OUT/'taylor_greedy_followup_report.md').write_text('\n'.join(report)+'\n')
    print('\n'.join(report),flush=True)

if __name__=='__main__':main()
