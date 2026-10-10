# Gymnopédie Breathing

A resonant-breathing guide: a circle that grows on the in-breath and shrinks on the out-breath, paced by the phrases of Satie's Gymnopédie No. 1 and No. 3.

Published page: https://claude.ai/artifact/H1gbek3v7iTfS14Jjx1jjT

## How it works

- `index.html` is the whole page. Open it, choose the recording (MP3, 6:25, "Gymnopedie No 1 & 3 --Satie" from *A Day at the Beach*), and press Play. The audio stays on the device.
- The MP3 is a commercial recording and is **not** in this repo. Re-analysis needs the file.
- Timing was measured from that recording's bass line:
  - No. 1: 86 bars from 0:36.4 to about 3:34, bass alternating G and D each bar. Average 86.8 BPM (2.07 s per bar).
  - No. 3: 69 bars from 3:42.0 to about 6:11.
  - One breath per 4 bars (in for 2, out for 2). No. 3 uses 6-bar breaths at bars 21, 43 and 49 where its phrases run longer.
  - Three steady 10 s lead-in breaths over the opening sounds, ending on bar 1.
  - Breaths average 8.8 s (about 6.8 per minute, 7.2 to 12.9 s). A "Steady 6 per minute" mode gives exact 0.1 Hz.

## Rebuilding the timing

Requires `librosa` (`pip install librosa`) and ffmpeg.

```
python3 analysis/downbeats.py path/to/recording.mp3   # writes bars_raw.json (bar times + bass notes)
python3 analysis/timeline.py                          # reads bars_raw.json, writes timeline.json
```

Then replace `__TIMELINE__` in `analysis/page_template.html` with the contents of `timeline.json` to produce `index.html`. The phrase groupings in `timeline.py` (which bars start a breath) were chosen by hand from the bar list, so check them for a different recording.

`analyze1.py` to `analyze4.py` are the exploratory steps: finding the gap between pieces, harmony and bass every 10 s, low-register onsets, and beat tracking.

`data/bars_raw.json` holds the detected downbeats. Bars 61 to 70 of No. 3 fall in the fading final chords and are less reliable; `timeline.py` uses bars 1 to 69.
