# Gymnopédie Breathing

A resonant-breathing guide: a circle that grows on the in-breath and shrinks on the out-breath, paced by the phrases of Satie's Gymnopédie No. 1 and No. 3.

Published page: https://claude.ai/artifact/H1gbek3v7iTfS14Jjx1jjT

## How it works

- `index.html` is the whole page. Open it, choose the recording (MP3, 6:25, "Gymnopedie No 1 & 3 --Satie" from *A Day at the Beach*), and press Play. The audio stays on the device: the browser keeps a copy in IndexedDB so the page loads it by itself on the next visit ("Forget recording" removes it).
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

## Hon Shirabe version

`hon-shirabe.html` is the same breathing guide for "Hon Shirabe (Original Tuning)", Alcvin Takegawa Ramos, *Zen Shakuhachi 1* (MP3, 4:19). The MP3 is not in this repo either.

- Honkyoku has no beat. Each phrase is one exhalation by the player, ending in a fade, a pause for breath, and a sharp attack. The attacks are found from loudness alone: 17 phrases from 0:00 to the final fade at 4:10, 9.3 to 25.7 s long (14.7 s average).
- Each breath starts with the out-breath on an attack and ends with the in-breath as the note fades. By default phrases over 15 s are split into two equal breaths (23 breaths, 8.1 to 14.8 s, 5.5 per minute). "One breath per phrase" and "Steady 6 per minute" are the other modes.
- The trace shows the flute's loudness under the breath curve.

Rebuilding needs only numpy and ffmpeg:

```
python3 analysis/phrases.py path/to/recording.mp3     # writes hon_timeline.json (onsets, end, loudness envelope)
```

Then replace `__TIMELINE__` in `analysis/hon_shirabe_template.html` with the contents of `hon_timeline.json` to produce `hon-shirabe.html`. `data/hon_timeline.json` holds the current result.
