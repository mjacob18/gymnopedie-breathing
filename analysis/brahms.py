"""Beat grid and sections for Brahms, Clarinet Quintet in B minor, Op. 115, i. Allegro:
python3 analysis/brahms.py path/to/recording.mp3   (needs librosa)

The movement is in 6/8 with a lot of rubato. The eighth-note beat drifts, so the dotted quarter (two per bar) is
tracked instead; the exposition repeat then lands the same number of beats later all the way through.
Sections are where the opening returns, found on 1 s chroma with a 30 s window: the exposition repeat, the
development (which opens with the same motto) and the recapitulation. Each is moved to the tracked beat that
corresponds to the opening's first beat. The final chords after the last tracked beat are
too sparse to track, so the timeline also records where the sound ends. Writes brahms_timeline.json.
"""
import sys, json, numpy as np, librosa

y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
HOP = 256
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
_, bf = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=HOP, start_bpm=50, tightness=400)
bt = librosa.frames_to_time(bf, sr=sr, hop_length=HOP)

# where the opening returns (seconds)
H = 2048; fps = sr / H
ch = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=H)
k = int(fps); ch = np.array([np.convolve(r, np.ones(k) / k, 'same') for r in ch])
ch /= np.linalg.norm(ch, axis=0, keepdims=True) + 1e-9
rms = librosa.feature.rms(y=y, hop_length=H)[0]
start = int(np.argmax(rms > rms.max() * 0.05)); W = int(30 * fps)
def match(j): return float(np.mean(np.sum(ch[:, start:start + W] * ch[:, j:j + W], 0)))
def best(lo, hi): return max(range(int(lo * fps), int(hi * fps)), key=match)
rep = best(120, 220)
dev = best(rep / fps + 150, rep / fps + 200)
recap = best(dev / fps + 120, dev / fps + 260)
shift = bt[0] - start / fps                                     # first tracked beat after the music starts
def beat_at(j): return int(np.argmin(abs(bt - (j / fps + shift))))

# end: the last quiet chords fade into digital silence; take the last moment within 60 dB of the peak
db = librosa.amplitude_to_db(librosa.feature.rms(y=y, hop_length=HOP)[0], ref=np.max)
db = np.convolve(np.pad(db, 10, mode='edge'), np.ones(20) / 20, 'valid')
end = round(float(librosa.frames_to_time(np.nonzero(db > -60)[0][-1], sr=sr, hop_length=HOP)), 2)

sections = [('Exposition', 0), ('Exposition repeat', beat_at(rep)), ('Development', beat_at(dev)), ('Recapitulation', beat_at(recap))]
for (name, b), j in zip(sections, (start, rep, dev, recap)):
    print(f"{name:18s} opening match at {j / fps:6.1f} s ({match(j):.2f}) -> beat {b:3d} at {bt[b]:6.1f} s")
ibi = np.diff(bt)
print(f"{len(bt)} beats, median {np.median(ibi):.3f} s, 4 bars = {8 * np.median(ibi):.1f} s; last beat {bt[-1]:.1f} s, ends {end} of {len(y) / sr:.2f} s")
json.dump(dict(duration=round(len(y) / sr, 2), end=end, beats=[round(float(t), 2) for t in bt],
               sections=[[name, b] for name, b in sections]),
          open('brahms_timeline.json', 'w'), separators=(',', ':'))
