import librosa, numpy as np, sys
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
print("dur", len(y)/sr)
rms = librosa.feature.rms(y=y, frame_length=4096, hop_length=2205)[0]
t = np.arange(len(rms))*0.1
# print quiet stretches
db = 20*np.log10(rms+1e-9)
mx = db.max()
quiet = t[db < mx-45]
# group
if len(quiet):
    groups=[]; s=quiet[0]; p=quiet[0]
    for q in quiet[1:]:
        if q-p>0.15: groups.append((s,p)); s=q
        p=q
    groups.append((s,p))
    for g in groups:
        if g[1]-g[0]>0.4: print("quiet %.1f-%.1f"%g)
