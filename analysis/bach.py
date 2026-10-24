"""Bar lines for Bach, Cello Suite No. 1 in G, BWV 1007, Prelude: python3 analysis/bach.py path/to/recording.m4a
(needs librosa and ffmpeg).

The Prelude is 42 bars of running sixteenths with one harmony per bar, and the first half of each bar's figure is
often repeated in its second half. So a bar line is where the harmony changes and a low string is struck. Exactly
42 bar starts are fitted between the first note and the final chord, preferring even bar lengths, then checked
against the mid-bar points. Writes bach_timeline.json.
"""
import sys, json, subprocess, numpy as np, librosa

SR, HOP = 22050, 441                       # 50 frames per second
BARS, PEN = 42, 1.5
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     check=True, capture_output=True).stdout
y = np.frombuffer(pcm, dtype=np.float32).copy()
fps = SR / HOP

C = np.abs(librosa.cqt(y, sr=SR, hop_length=HOP, fmin=librosa.note_to_hz('C2'), n_bins=60))
ldb = librosa.amplitude_to_db(C, ref=np.max)
flux = np.concatenate([[0], np.maximum(0, np.diff(ldb[:19], axis=1)).sum(0)]); flux /= np.percentile(flux, 99)
ch = librosa.feature.chroma_cqt(C=C, sr=SR, hop_length=HOP)
n = ch.shape[1]; L = int(0.8 * fps)
cs = np.cumsum(np.pad(ch, ((0, 0), (1, 0))), axis=1)
def cos(u, v): return float(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))
nov = np.zeros(n)
for i in range(L, n - L): nov[i] = 1 - cos(cs[:, i] - cs[:, i - L], cs[:, i + L] - cs[:, i])
f = librosa.util.normalize(np.convolve(nov, np.hanning(5), 'same')) + 0.5 * librosa.util.normalize(np.convolve(flux, np.hanning(5), 'same'))

rms = librosa.amplitude_to_db(librosa.feature.rms(y=y, hop_length=HOP)[0], ref=np.max)
rms_s = np.convolve(np.pad(rms, 10, mode='edge'), np.ones(20) / 20, 'valid')
first = int(np.argmax(rms > -40))
last = int(np.nonzero(rms > -50)[0][-1])
end = round(float(np.nonzero(rms_s > -40)[0][-1] / fps), 2)        # the final chord has died away

B = (last - first) / (BARS - 0.4); lo, hi = int(0.55 * B), int(1.9 * B)
score = np.full((BARS, n), -1e18); prev = np.full((BARS, n), -1, int)
score[0, first] = f[first]                                          # bar 1 starts on the first note
for k in range(1, BARS):
    for i in range(first + lo, last):
        js = np.arange(max(first, i - hi), i - lo + 1)
        cand = score[k - 1, js] - PEN * np.log((i - js) / B) ** 2
        m = int(np.argmax(cand)); score[k, i] = cand[m] + f[i]; prev[k, i] = js[m]
i = int(np.argmax(score[BARS - 1, :last - int(2.5 * fps)])); path = [i]
for k in range(BARS - 1, 0, -1): i = prev[k, i]; path.append(i)
bars = np.array(path[::-1]) / fps

def change_at(t, w=0.8):
    a, b, c = int((t - w) * fps), int(t * fps), int((t + w) * fps)
    return 1 - cos(ch[:, a:b].mean(1), ch[:, b:c].mean(1))
real = np.array([change_at(t) for t in bars[1:]])
mid = np.array([change_at((a + b) / 2) for a, b in zip(bars, bars[1:])])
g = np.diff(bars)
print(f"bar 1 at {bars[0]:.2f} s, final chord (bar 42) at {bars[-1]:.2f} s, sound ends {end} s of {len(y) / SR:.2f} s")
print(f"bar length median {np.median(g[:-1]):.2f} s (min {g[:-1].min():.2f}, max {g[:-1].max():.2f})")
print(f"harmonic change at bar lines {real.mean():.3f} vs mid-bar {mid.mean():.3f}; bar line larger in {np.mean(real > mid) * 100:.0f}% of bars")
json.dump(dict(duration=round(len(y) / SR, 2), end=end, bars=[round(float(t), 2) for t in bars]),
          open('bach_timeline.json', 'w'), separators=(',', ':'))
