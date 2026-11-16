"""Pulse grid for Nils Frahm, "Says" (Spaces, 2013): python3 analysis/says.py path/to/recording.mp3   (needs librosa)

"Says" is a sequenced arpeggio (three notes to the beat) at a fixed tempo that builds for eight minutes over a
nearly unchanging harmony. The beat is tracked and a straight line fitted through it, which gives the tempo for the
whole track. The grid is counted from the first note, and the chords and bass change most at one beat of a 32-beat
(8-bar) cycle; breaths are anchored there. Also found: where the loud music stops (the full
sound cuts out before a quieter tail runs to the end of the file) and where the build reaches its plateau.
Writes says_timeline.json.
"""
import sys, json, numpy as np, librosa

y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
HOP = 256; fps = sr / HOP
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
_, bf = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=HOP, start_bpm=150, tightness=800)
bt = librosa.frames_to_time(bf, sr=sr, hop_length=HOP)
k = np.arange(len(bt)); beat, b0 = np.polyfit(k, bt, 1)
res = bt - (beat * k + b0)

on = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=HOP, units='time')
first = float(on[0])
j = round((first - b0) / beat)                                   # grid index nearest the first note
start = b0 + beat * j

# where the harmony turns over: chord and bass change across each grid beat, averaged by position in a 32-beat cycle
# counted from the first note
C = np.abs(librosa.cqt(y, sr=sr, hop_length=HOP, fmin=librosa.note_to_hz('C1'), n_bins=72))
ch = librosa.feature.chroma_cqt(C=C, sr=sr, hop_length=HOP)
def cos(u, v): return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))
def change(t, M, w=0.6):
    a, b, c = int((t - w) * fps), int(t * fps), int((t + w) * fps)
    return 1 - cos(M[:, a:b].mean(1), M[:, b:c].mean(1))
grid = start + beat * np.arange(int((bt[-1] - start) / beat))
prof = np.zeros(32); cnt = np.zeros(32)
for i, t in enumerate(grid):
    if t > 1: prof[i % 32] += change(t, ch) + change(t, C[:24]); cnt[i % 32] += 1
prof /= cnt
turn = int(np.argmax(prof))

rms = librosa.amplitude_to_db(librosa.feature.rms(y=y, hop_length=HOP)[0], ref=np.max)
sm = np.convolve(np.pad(rms, 25, mode='edge'), np.ones(51) / 51, 'valid')
loud = np.nonzero(sm > -8)[0]
cut = float(loud[-1] / fps)                                      # the full sound stops here
plateau = float(loud[0] / fps)                                   # the build reaches full level
build = float(np.argmax(sm > sm[int(30 * fps):int(200 * fps)].max() + 3) / fps)   # clearly louder than the long first stretch

print(f"tempo {60 / beat:.2f} per minute (beat {beat:.4f} s), grid residual p1/p99 {np.percentile(res, [1, 99]).round(3)}")
print(f"first note {first:.2f} s; chords and bass change most at beat {turn} of the 32-beat cycle counted from it "
      f"({prof[turn] / prof.mean():.2f} x average; next {sorted(prof / prof.mean())[-2]:.2f} x)")
print(f"build from {build:.1f} s, full level from {plateau:.1f} s, full sound stops at {cut:.1f} s of {len(y) / sr:.2f} s")
json.dump(dict(duration=round(len(y) / sr, 2), start=round(start, 3), beat=round(float(beat), 5), turn=turn,
               build=round(build, 1), plateau=round(plateau, 1), cut=round(cut, 2)),
          open('says_timeline.json', 'w'), separators=(',', ':'))
