import librosa, numpy as np, sys
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
hop=256; fps=sr/hop
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop, aggregate=np.median)
tempo, beats = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop, start_bpm=87, tightness=400, units='time')
print("tempo", tempo, "nbeats", len(beats))
C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz('C1'), n_bins=48))
lowE = C[:24].sum(0)
rows=[]
for b in beats:
    a=int(b*fps); e=a+int(0.35*fps)
    lb = C[:24,a:e].mean(1)
    rows.append((b, lowE[a:e].mean(), librosa.midi_to_note(24+np.argmax(lb))))
np.save('beats.npy', beats)
for i,(b,e,n) in enumerate(rows):
    print(f"{i:4d} {b:7.2f} {e:8.2f} {n}")
