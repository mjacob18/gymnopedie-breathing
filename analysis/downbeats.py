import librosa, numpy as np, sys, json
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
hop=256; fps=sr/hop
C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz('C1'), n_bins=48))
low = C[:24]
# low-band onset envelope (positive flux), fine time grid
ld = librosa.amplitude_to_db(low, ref=np.max)
flux = np.maximum(0, np.diff(ld, axis=1)).sum(0); flux = np.concatenate([[0], flux])
flux = flux / np.percentile(flux, 99)
def segment(t0, t1, bar0):
    # DP over candidate frames: downbeat frames must be ~bar0 apart (0.75..1.5x)
    a, b = int(t0*fps), int(t1*fps)
    f = librosa.util.normalize(np.convolve(flux[a:b], np.hanning(9), 'same'))
    n = len(f); B = bar0*fps
    lo, hi = int(0.7*B), int(1.6*B)
    score = np.full(n, -1e9); prev = np.full(n, -1)
    score[:hi] = f[:hi]
    for i in range(lo, n):
        js = np.arange(max(0, i-hi), i-lo+1)
        gap = (i-js)/B
        cand = score[js] - 2.0*np.log(gap)**2
        k = np.argmax(cand); score[i] = cand[k] + f[i]; prev[i] = js[k]
    i = np.argmax(score[n-hi:]) + n-hi
    path=[]
    while i >= 0: path.append(i); i = prev[i]
    return [(a+p)/fps for p in path[::-1]]
segs = {"no1": (36.0, 213.0), "no3": (221.5, 366.0)}
out = {}
for name,(t0,t1) in segs.items():
    db = segment(t0, t1, 2.06)
    bars=[]
    for i,t in enumerate(db):
        a=int((t+0.04)*fps); e=a+int(0.5*fps)
        note = librosa.midi_to_note(24+int(np.argmax(low[:,a:e].mean(1))), unicode=False)
        nxt = db[i+1] if i+1 < len(db) else None
        bars.append({"t": round(t,3), "bass": note, "len": round(nxt-t,2) if nxt else None})
    out[name]=bars
    print(name, len(bars), "bars")
    for i,b in enumerate(bars):
        print(f"  {i+1:3d} {b['t']:7.2f} {b['bass']:4s} {b['len']}")
json.dump(out, open('bars_raw.json','w'))
