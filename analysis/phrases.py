"""Phrase timing for Hon Shirabe (shakuhachi): python3 analysis/phrases.py path/to/recording.mp3

Each honkyoku phrase is one exhalation by the player, so phrases are found from loudness alone:
a phrase starts where the level jumps back up after a quiet dip (the player's in-breath).
Needs numpy and ffmpeg. Writes hon_timeline.json (phrase onsets, end of the piece, 4 Hz loudness envelope).
"""
import sys, json, subprocess, numpy as np

SR, HOP, WIN = 22050, 220, 1102          # 10 ms hop, 50 ms window
HI, LO = -28, -40                        # dB re. peak: an onset crosses HI after dipping below LO in the last 1.5 s
END_FLOOR = -50                          # the piece ends at the last frame above this (room noise sits near -52)

pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     check=True, capture_output=True).stdout
x = np.frombuffer(pcm, dtype=np.float32)
n = (len(x) - WIN) // HOP
fr = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP][:n]
db = 20 * np.log10(np.sqrt((fr ** 2).mean(1) + 1e-12)); db -= db.max()
sm = np.convolve(db, np.ones(10) / 10, 'same')   # 100 ms smoothing
t = np.arange(n) * HOP / SR + WIN / 2 / SR

onsets = [0.0] if sm[:50].max() > HI else []    # the recording opens on an attack
for k in range(1, n):
    if sm[k] >= HI > sm[k - 1] and sm[max(0, k - 150):k].min() < LO and (not onsets or t[k] - onsets[-1] > 2.0):
        j = k
        while j > 0 and LO + 6 < sm[j - 1] < sm[j]: j -= 1   # back to the foot of the attack
        onsets.append(round(float(t[j]), 2))
end = round(float(t[np.nonzero(sm > END_FLOOR)[0][-1]]), 2)

lens = np.diff(onsets + [end])
for k, (a, L) in enumerate(zip(onsets, lens), 1):
    print(f"phrase {k:2d}  {a:7.2f}  length {L:5.2f} s")
print(f"{len(onsets)} phrases, length mean {lens.mean():.1f} s, min {lens.min():.1f}, max {lens.max():.1f}; ends {end} of {len(x) / SR:.2f} s")

env = db[:n // 25 * 25].reshape(-1, 25).mean(1)   # 0.25 s cells
json.dump(dict(duration=round(len(x) / SR, 2), end=end, onsets=onsets, envStep=0.25,
               env=[int(round(max(v, -60))) for v in env]),
          open('hon_timeline.json', 'w'), separators=(',', ':'))
