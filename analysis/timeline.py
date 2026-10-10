import json, numpy as np
raw = json.load(open('bars_raw.json'))
t1 = [b['t'] for b in raw['no1']]   # bars 1..86
t3 = [b['t'] for b in raw['no3'][:69]]  # bars 1..69 (70th is the fade, dropped)
B = lambda arr, n: arr[n-1]
cycles = []
# lead-in: three steady 10 s breaths ending at bar 1
for k in (3,2,1):
    s = t1[0]-10*k
    cycles.append(dict(i=round(s,2), o=round(s+5,2), e=round(s+10,2), p=0, b=0, n=0))
def grp(arr, piece, start, n, end=None):
    half = n//2
    i, o = B(arr,start), B(arr,start+half)
    e = end if end is not None else B(arr,start+n)
    cycles.append(dict(i=round(i,2), o=round(o,2), e=round(e,2), p=piece, b=start, n=n))
for s in range(1, 85, 4): grp(t1, 1, s, 4)
# closing chord of No. 1: inhale through bar 85-86, exhale into the gap until No. 3 starts
cycles.append(dict(i=round(B(t1,85),2), o=round(B(t1,86)+2.0,2), e=round(t3[0],2), p=1, b=85, n=2))
for s in (1,5,9,13,17): grp(t3, 3, s, 4)
grp(t3, 3, 21, 6)
for s in (27,31,35,39): grp(t3, 3, s, 4)
grp(t3, 3, 43, 6); grp(t3, 3, 49, 6)
for s in (55,59,63): grp(t3, 3, s, 4)
cycles.append(dict(i=round(B(t3,67),2), o=round(B(t3,69),2), e=371.5, p=3, b=67, n=3))
# sanity: contiguity
for a,b in zip(cycles, cycles[1:]):
    assert abs(a['e']-b['i'])<1e-6, (a,b)
mus = [c for c in cycles if c['p']]
durs = np.array([c['e']-c['i'] for c in mus])
print("cycles", len(cycles), "music cycles", len(mus))
print("cycle s: mean %.2f min %.2f max %.2f -> mean bpm %.2f" % (durs.mean(), durs.min(), durs.max(), 60/durs.mean()))
d1 = np.diff(t1); print("No.1 bar mean %.3f s -> %.1f BPM" % (d1.mean(), 180/d1.mean()))
data = dict(
  duration=384.94,
  bars1=[round(x,2) for x in t1], bars3=[round(x,2) for x in t3],
  bass1=[b['bass'] for b in raw['no1']], bass3=[b['bass'] for b in raw['no3'][:69]],
  cycles=[[c['i'],c['o'],c['e'],c['p'],c['b'],c['n']] for c in cycles],
)
json.dump(data, open('timeline.json','w'), separators=(',',':'))
print(len(open('timeline.json').read()), "bytes")
