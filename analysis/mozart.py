"""Beat grid and sections for Mozart, String Quartet No. 14 in G, K. 387, i. Allegro vivace assai:
python3 analysis/mozart.py path/to/recording.mp3   (needs librosa)

The quarter-note beat is tracked across the whole movement. The sections are found from harmony (beat-synchronous
chroma): the exposition repeat is where the opening 32 beats recur exactly, the development starts one exposition
later, and the recapitulation is the next return of the opening. Writes mozart_timeline.json.
"""
import sys, json, numpy as np, librosa

y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
HOP = 256
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
_, bf = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=HOP, start_bpm=120)
bt = librosa.frames_to_time(bf, sr=sr, hop_length=HOP)
ch = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP)
cs = librosa.util.sync(ch, bf, aggregate=np.median)
cs /= np.linalg.norm(cs, axis=0, keepdims=True) + 1e-9
n, W = len(bt), 32

def opening_match(k): return float(np.mean(np.sum(cs[:, :W] * cs[:, k:k + W], 0)))
rep = max(range(150, 300), key=opening_match)                    # exposition repeat
dev = 2 * rep                                                    # development follows the second exposition
recap = max(range(dev + 100, n - W), key=opening_match)          # opening returns
ibi = float(np.median(np.diff(bt)))
end = round(float(bt[-1] + ibi), 2)                              # last chord sounds for one more beat

sections = [('Exposition', 0), ('Exposition repeat', rep), ('Development', dev), ('Recapitulation', recap)]
for name, k in sections:
    print(f"{name:18s} beat {k:4d}  {bt[k]:7.2f} s  (opening match {opening_match(k):.2f})")
print(f"{n} beats, median {ibi:.3f} s ({60 / ibi:.0f} per minute), 4 bars = {16 * ibi:.1f} s; ends {end} of {len(y) / sr:.2f} s")
json.dump(dict(duration=round(len(y) / sr, 2), end=end, beats=[round(float(t), 2) for t in bt],
               sections=[[name, k] for name, k in sections]),
          open('mozart_timeline.json', 'w'), separators=(',', ':'))
