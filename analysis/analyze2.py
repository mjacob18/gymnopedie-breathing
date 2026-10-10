import librosa, numpy as np, sys
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
hop=512
C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz('C1'), n_bins=84))
chroma = librosa.feature.chroma_cqt(C=C, sr=sr, hop_length=hop)
names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
fps = sr/hop
# broadband noise level: spectral flatness
flat = librosa.feature.spectral_flatness(y=y, hop_length=hop)[0]
rms = librosa.feature.rms(y=y, hop_length=hop)[0]
for s in range(0, int(len(y)/sr), 10):
    a,b = int(s*fps), int((s+10)*fps)
    c = chroma[:,a:b].mean(1)
    top = np.argsort(c)[::-1][:4]
    # lowest strong bass note
    bass = C[:24,a:b].mean(1)
    bn = librosa.midi_to_note(24+np.argmax(bass))
    print(f"{s:4d}s rms={20*np.log10(rms[a:b].mean()+1e-9):6.1f} flat={flat[a:b].mean():.3f} chroma={' '.join(names[i] for i in top)} bass={bn}")
