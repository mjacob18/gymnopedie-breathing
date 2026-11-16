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

Published page: https://claude.ai/artifact/NrJP13nNcomWLEL7MMywau

`hon-shirabe.html` is the same breathing guide for "Hon Shirabe (Original Tuning)", Alcvin Takegawa Ramos, *Zen Shakuhachi 1* (MP3, 4:19). The MP3 is not in this repo either.

- Honkyoku has no beat. Each phrase is one exhalation by the player, ending in a fade, a pause for breath, and a sharp attack. The attacks are found from loudness alone: 17 phrases from 0:00 to the final fade at 4:10, 9.3 to 25.7 s long (14.7 s average).
- Each breath starts with the out-breath on an attack and ends with the in-breath as the note fades. By default phrases over 15 s are split into two equal breaths (23 breaths, 8.1 to 14.8 s, 5.5 per minute). "One breath per phrase" and "Steady 6 per minute" are the other modes.
- The trace shows the flute's loudness under the breath curve.

Rebuilding needs only numpy and ffmpeg:

```
python3 analysis/phrases.py path/to/recording.mp3     # writes hon_timeline.json (onsets, end, loudness envelope)
```

Then replace `__TIMELINE__` in `analysis/hon_shirabe_template.html` with the contents of `hon_timeline.json` to produce `hon-shirabe.html`. `data/hon_timeline.json` holds the current result.

## Mozart version

`present/mozart-k387.html` is a presentation page (see below) for Mozart, String Quartet No. 14 in G, K. 387, i. Allegro vivace assai, from *The Haydn Quartets*, Disc 1 (MP3, 7:28). The MP3 is not in this repo.

- The quarter-note beat runs at about 129 per minute, so 4 bars last about 7.4 s.
- The sections come from harmony: the opening recurs exactly 225 beats later (exposition repeat, 1:46), the development starts at 3:33, and the opening returns at 5:19 (recapitulation). The movement ends at 7:21.
- Breaths are 4 bars (in for 2, out for 2), counted from the start of each section; a leftover bar or beat at a section's end joins its last breath. That gives 58 breaths of 7.2 to 8.9 s, about 8 per minute. "Slower (8 bars)" gives about 4 per minute and "Steady 6 per minute" an exact 10 s cycle.
- The accent pattern inside each section was too weak to confirm every downbeat, so breaths are counted from the section starts, which are clear.

Rebuilding needs librosa:

```
python3 analysis/mozart.py path/to/recording.mp3      # writes mozart_timeline.json (beats, sections, end)
```

`data/mozart_timeline.json` holds the current result.

## Brahms version

`present/brahms-op115.html` is a presentation page for Brahms, Clarinet Quintet in B minor, Op. 115, i. Allegro, from *Clarinet Trio and Quintet* (MP3, 12:22). The MP3 is not in this repo.

- The movement is in 6/8 with a lot of rubato. The eighth-note beat drifts, so the dotted quarter (two per bar, about 1.15 s) is tracked; the exposition repeat then lands exactly 143 beats later all the way through.
- The opening returns at 2:47 (exposition repeat), 5:32 (development, which starts with the same motto) and 8:54 (recapitulation). The last quiet chords fade out at 12:16; past the last tracked beat (11:56) the final stretch is split into equal breaths.
- Breaths are 4 bars (8 beats, in for 2 bars, out for 2), counted from those section starts: 80 breaths of 8.1 to 10.0 s, about 6.5 per minute. "Steady 6 per minute" is the alternative.
- Brahms's hemiolas blur the downbeats, and the accent evidence disagrees between the two copies of the exposition, so breaths are counted from the section starts rather than from detected bar lines.

Rebuilding needs librosa:

```
python3 analysis/brahms.py path/to/recording.mp3      # writes brahms_timeline.json (beats, sections, end)
```

`data/brahms_timeline.json` holds the current result.

## Bach version

`present/bach-bwv1007.html` is a presentation page for Bach, Cello Suite No. 1 in G, BWV 1007, Prelude, played by Yo-Yo Ma (*Classic Yo-Yo*, M4A, 2:25). The recording is not in this repo.

- The Prelude is 42 bars of running sixteenths with one harmony per bar. Exactly 42 bar starts are fitted from the first note (0:03) to the final chord (2:10), at harmony changes and low-string attacks, preferring even bar lengths. Bars run 2.4 to 3.8 s (3.0 s median). As a check, the harmony changes about 2.5 times as much at the fitted bar lines as at mid-bar points, and more at the bar line in 78% of bars; the exceptions sit mostly in bars 32 to 39, over the held D pedal.
- Default breathing is in for 1 bar, out for 2 (14 breaths, about 6.3 per minute), so every turn falls on a bar line. "Slower: 4 bars" (in 2, out 2; about 5 per minute) and "Steady 6 per minute" are the alternatives. The last breath runs out over the final chord, which dies away at 2:16.

Rebuilding needs librosa and ffmpeg:

```
python3 analysis/bach.py path/to/recording.m4a        # writes bach_timeline.json (bar starts, end)
```

`data/bach_timeline.json` holds the current result.

## Says version

`present/frahm-says.html` is a presentation page for Nils Frahm, "Says", from *Spaces* (2013; MP3, 8:18). The MP3 is not in this repo.

- "Says" is a sequenced arpeggio at a fixed tempo, 149.6 beats per minute (0.401 s), building for eight minutes over a nearly unchanging harmony. A straight-line fit through the tracked beats holds to within about 0.1 s across the whole track, so one grid, counted from the first note (0:00.06), covers it.
- Chords and bass change most at beat 14 of a 32-beat (8-bar) cycle counted from the first note, about twice the average change, so the first note is a two-beat pickup and the breaths start on that chord change (0:05.7).
- Default breathing is 6 bars (24 beats, 9.6 s; in 3 bars, out 3), about 6.2 per minute. The 50th breath ends exactly where the full sound cuts out, at 8:06.9; the quieter tail to 8:18 is rest. "Slower: 8 bars, with the chords" (12.8 s, about 4.7 per minute) puts every breath start on the chord change; "Steady 6 per minute" is the alternative.
- The seek bar shades the long quiet stretch, the build from 4:43, and the full-level climax from 5:38.
- Stage light: if `says-light.mp4` (or `says-light.webm`) sits beside the page, a looping video of warm light through haze in a dark church plays behind the circle. It stays dark until the build (4:43), rises with the music to full by 5:38, brightens a little on each in-breath and dims on each out-breath, dims when playback is paused or faded out, and fades over 3 s when the full sound cuts out at 8:07. The page keeps its dark palette whatever the system theme. The video was generated with Gemini and prepared with ffmpeg: a small green exit sign was blended out, the black borders were cropped, the audio was dropped, and the 10 s clip was played forwards then backwards so it loops without a jump. It is not in this repo; the light layer (`light` in a page's config) is available to any presentation page.

Rebuilding needs librosa:

```
python3 analysis/says.py path/to/recording.mp3        # writes says_timeline.json (grid start, beat, chord-change beat, build, cut)
```

`data/says_timeline.json` holds the current result.

## Presentation pages

`present/gymnopedie.html`, `present/hon-shirabe.html`, `present/mozart-k387.html`, `present/brahms-op115.html`, `present/bach-bwv1007.html` and `present/frahm-says.html` are standalone, minimal-text versions for screen sharing (one screen: circle, breath trace, Play, Fade out, seek, Options, Full screen; Space plays or pauses, F toggles full screen). Fade out lowers the volume over 8 s, then pauses and restores the volume for the next Play; press it again to cancel. Put each next to its MP3 and open it straight from the folder; it plays the MP3 beside it. It looks for these names, in order:

- `gymnopedie.mp3`, `01 Gymnopedie No 1 & 3 --Satie.mp3`, `01_Gymnopedie_No_1_3_--Satie.mp3`, `Gymnopedie No 1 & 3 --Satie.mp3`
- `hon-shirabe.mp3`, `01 - Hon Shirabe (Original Tuning).mp3`, `01_-_Hon_Shirabe_Original_Tuning.mp3`, `Hon Shirabe (Original Tuning).mp3`
- `mozart.mp3`, `01 Quartet 14 in G, K.387, i) Allegro vivace assai.mp3`, `01_Quartet_14_in_G_K.387_i_Allegro_vivace_assai.mp3`, `Quartet 14 in G, K.387, i) Allegro vivace assai.mp3`
- `brahms.mp3`, `05 Quintet in B Minor, Op. 115 1 Allegro.mp3`, `05_Quintet_in_B_Minor_Op._115_1_Allegro.mp3`, `Quintet in B Minor, Op. 115 1 Allegro.mp3`
- `bach.m4a`, `bach.mp3`, `01 Bach (JS)_ Cello Suite #1 In G, B.m4a`, `01_Bach_JS__Cello_Suite_1_In_G_B.m4a`, `Bach (JS)_ Cello Suite #1 In G, BMV 1007 - Prelude.m4a` (a browser that cannot play AAC moves on to `bach.mp3`)
- `says.mp3`, `02 - Says.mp3`, `02_-_Says.mp3`, `Says.mp3`

If none is there, choose the file under Options; the browser then remembers it. Rebuild them all with `python3 analysis/build_present.py` (from `analysis/present_template.html` and the timelines in `data/`).
