import librosa, numpy as np, sys
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
print("tuning (fraction of semitone):", librosa.estimate_tuning(y=y[sr*35:sr*200], sr=sr))
hop=256
# onset strength in low band
S = np.abs(librosa.stft(y, n_fft=4096, hop_length=hop))
freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)
low = S[(freqs>50)&(freqs<180)]
env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(low), sr=sr, hop_length=hop)
on = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop, units='time', backtrack=False, delta=0.3, wait=int(1.2*sr/hop))
C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz('C1'), n_bins=36, bins_per_octave=12))
fps=sr/hop
out=[]
for t in on:
    a=int((t+0.05)*fps); b=a+int(0.4*fps)
    bn = librosa.midi_to_note(24+np.argmax(C[:,a:b].mean(1)))
    out.append((t,bn))
np.save('onsets.npy', np.array([o[0] for o in out]))
prev=None
for t,bn in out:
    d = t-prev if prev is not None else 0
    print(f"{t:7.2f} +{d:5.2f} {bn}")
    prev=t
