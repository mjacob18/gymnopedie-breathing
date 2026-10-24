"""Build the standalone presentation pages: python3 analysis/build_present.py (from the repo root).

Reads data/timeline.json (Satie), data/hon_timeline.json (Hon Shirabe), data/mozart_timeline.json (Mozart K. 387),
data/brahms_timeline.json (Brahms Op. 115) and data/bach_timeline.json (Bach BWV 1007), fills analysis/present_template.html,
and writes one page per piece to present/. Each page plays the MP3 sitting beside it.
"""
import json, math, os, re

R2 = lambda x: round(x, 2)

def satie():
    D = json.load(open('data/timeline.json'))
    cyc = [dict(zip(('i', 'o', 'e', 'piece', 'bar', 'n'), c)) for c in D['cycles']]
    lead, no1, no3, end, dur = cyc[0]['i'], D['bars1'][0], D['bars3'][0], 371.5, D['duration']
    gap = next(c['o'] for c in cyc if c['piece'] == 1 and c['bar'] == 85)
    turns = {c['i'] for c in cyc}
    bars = D['bars1'] + D['bars3']
    steady, i = [], lead
    while i < end: steady.append([R2(i), R2(i + 5), R2(i + 10), int(i < no1)]); i += 10
    return dict(
        title='Gymnopédie Breathing', heading='Gymnopédie No. 1 &amp; 3', key='gymnopedie', duration=dur, end=end,
        order='in', beforeWord='Settle in',
        files=['gymnopedie.mp3', '01 Gymnopedie No 1 & 3 --Satie.mp3', '01_Gymnopedie_No_1_3_--Satie.mp3', 'Gymnopedie No 1 & 3 --Satie.mp3'],
        modes=[dict(key='phrase', label='Follow the phrases (4 bars)', cycles=[[c['i'], c['o'], c['e'], int(c['piece'] == 0)] for c in cyc]),
               dict(key='steady', label='Steady 6 per minute', cycles=steady)],
        ripples=[[t, int(t in turns)] for t in bars], ticks=[[t, int(t in turns)] for t in bars],
        bands=[[0, lead, 'n'], [lead, no1, 'w'], [no1, gap, 'a'], [gap, no3, 'n'], [no3, end, 'b'], [end, dur, 'n']],
        env=None, envStep=None,
        fonts='https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@1,6..96,400&family=Jost:wght@400;500&family=Spline+Sans+Mono:wght@400;500&display=swap',
        tokens=dict(display='"Bodoni Moda", "Didot", "Bodoni 72", Georgia, serif', style='italic', weight=400,
                    light='--bg: #e8ecef; --surface: #f3f5f7; --ink: #1c2633; --muted: #5a6877; --line: #c3ccd5; --breath-rgb: 63 112 120; --wave-rgb: 128 146 160;',
                    dark='--bg: #0d131a; --surface: #131b24; --ink: #dce4ea; --muted: #8592a1; --line: #24303d; --breath-rgb: 142 194 192; --wave-rgb: 96 112 128;'))

def hon():
    D = json.load(open('data/hon_timeline.json'))
    on, end, dur = D['onsets'], D['end'], D['duration']
    ph = list(zip(on, on[1:] + [end]))
    def per_phrase(split):
        out = []
        for a, b in ph:
            n = math.ceil((b - a) / 15) if split else 1
            for j in range(n):
                i, e = a + (b - a) * j / n, a + (b - a) * (j + 1) / n
                out.append([R2(i), R2((i + e) / 2), R2(e), 0])
        return out
    steady = [[R2(i), R2(i + 5), R2(i + 10), 0] for i in range(0, math.ceil(end), 10)]
    return dict(
        title='Hon Shirabe Breathing', heading='Hon Shirabe', key='hon-shirabe', duration=dur, end=end,
        order='out', beforeWord='Breathe in',
        files=['hon-shirabe.mp3', '01 - Hon Shirabe (Original Tuning).mp3', '01_-_Hon_Shirabe_Original_Tuning.mp3', 'Hon Shirabe (Original Tuning).mp3'],
        modes=[dict(key='split', label='Follow the phrases (split over 15 s)', cycles=per_phrase(True)),
               dict(key='whole', label='One breath per phrase', cycles=per_phrase(False)),
               dict(key='steady', label='Steady 6 per minute', cycles=steady)],
        ripples=[[t, 1] for t in on], ticks=[[t, 1] for t in on],
        bands=[[a, b, 'ab'[k % 2]] for k, (a, b) in enumerate(ph)] + [[end, dur, 'n']],
        env=D['env'], envStep=D['envStep'],
        fonts='https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500&family=Jost:wght@400;500&family=Spline+Sans+Mono:wght@400;500&display=swap',
        tokens=dict(display='"Shippori Mincho", "Hiragino Mincho ProN", "Yu Mincho", Georgia, serif', style='normal', weight=500,
                    light='--bg: #e9ebe4; --surface: #f3f4ef; --ink: #1f2420; --muted: #5b6459; --line: #c8cdc2; --breath-rgb: 86 108 70; --wave-rgb: 138 148 132;',
                    dark='--bg: #10130f; --surface: #171b16; --ink: #dfe3d8; --muted: #8d9787; --line: #283026; --breath-rgb: 168 192 140; --wave-rgb: 96 108 92;'))

def beat_groups(bt, starts, end, size, bar):
    """Breaths of `size` beats counted from each section start. A remainder under half a breath joins the section's
    last breath; the turn falls on a bar line at or before the middle; a final stretch past the last tracked beat that
    runs long is split into equal breaths."""
    t = lambda k: bt[k] if k < len(bt) else end
    out = []
    for a, b in zip(starts, starts[1:]):
        ks = list(range(a, b, size))
        if len(ks) > 1 and b - ks[-1] < size / 2: ks.pop()
        for i, k in enumerate(ks):
            e = ks[i + 1] if i + 1 < len(ks) else b
            out.append([t(k), t(k + max(bar, (e - k) // (2 * bar) * bar)), t(e), 0])
    typical = sorted(c[2] - c[0] for c in out)[len(out) // 2]
    i, _, e, _ = out[-1]
    if e - i > 1.5 * typical:
        n = round((e - i) / typical)
        out[-1:] = [[R2(i + (e - i) * j / n), R2(i + (e - i) * (j + .5) / n), R2(i + (e - i) * (j + 1) / n), 0] for j in range(n)]
    return out

def mozart():
    D = json.load(open('data/mozart_timeline.json'))
    bt, end, dur = D['beats'], D['end'], D['duration']
    starts = [k for _, k in D['sections']] + [len(bt)]
    t = lambda k: bt[k] if k < len(bt) else end
    groups = lambda size: beat_groups(bt, starts, end, size, 4)
    four = groups(16)
    turns = {c[0] for c in four}
    bars = [bt[k] for a, b in zip(starts, starts[1:]) for k in range(a, b, 4)]
    steady = [[R2(bt[0] + i), R2(bt[0] + i + 5), R2(bt[0] + i + 10), 0] for i in range(0, math.ceil(end - bt[0]), 10)]
    rep, dev, recap = (t(k) for _, k in D['sections'][1:])
    return dict(
        title='Mozart Quartet Breathing', heading='Mozart · Quartet in G, K. 387', key='mozart-k387', duration=dur, end=end,
        order='in', beforeWord='Breathe out',
        files=['mozart.mp3', '01 Quartet 14 in G, K.387, i) Allegro vivace assai.mp3', '01_Quartet_14_in_G_K.387_i_Allegro_vivace_assai.mp3',
               'Quartet 14 in G, K.387, i) Allegro vivace assai.mp3'],
        modes=[dict(key='four', label='Follow the phrases (4 bars)', cycles=four),
               dict(key='eight', label='Slower (8 bars)', cycles=groups(32)),
               dict(key='steady', label='Steady 6 per minute', cycles=steady)],
        ripples=[[x, int(x in turns)] for x in bars], ticks=[[x, int(x in turns)] for x in bars],
        bands=[[0, bt[0], 'n'], [bt[0], rep, 'a'], [rep, dev, 'b'], [dev, recap, 'w'], [recap, end, 'a'], [end, dur, 'n']],
        env=None, envStep=None,
        fonts='https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500&family=Jost:wght@400;500&family=Spline+Sans+Mono:wght@400;500&display=swap',
        tokens=dict(display='"Cormorant Garamond", "Garamond", "Iowan Old Style", Georgia, serif', style='italic', weight=500,
                    light='--bg: #ebe8ec; --surface: #f5f3f6; --ink: #241d26; --muted: #625866; --line: #cec7d0; --breath-rgb: 122 52 78; --wave-rgb: 150 138 152;',
                    dark='--bg: #141015; --surface: #1c171d; --ink: #e6dfe7; --muted: #9a8f9c; --line: #302832; --breath-rgb: 214 150 172; --wave-rgb: 112 100 116;'))

def brahms():
    D = json.load(open('data/brahms_timeline.json'))
    bt, end, dur = D['beats'], D['end'], D['duration']
    starts = [k for _, k in D['sections']] + [len(bt)]
    t = lambda k: bt[k] if k < len(bt) else end
    four = beat_groups(bt, starts, end, 8, 2)        # beats are dotted quarters: 2 per 6/8 bar
    turns = {c[0] for c in four}
    bars = [bt[k] for a, b in zip(starts, starts[1:]) for k in range(a, b, 2)]
    steady = [[R2(bt[0] + i), R2(bt[0] + i + 5), R2(bt[0] + i + 10), 0] for i in range(0, math.ceil(end - bt[0]), 10)]
    rep, dev, recap = (t(k) for _, k in D['sections'][1:])
    return dict(
        title='Brahms Quintet Breathing', heading='Brahms · Clarinet Quintet, Op. 115', key='brahms-op115', duration=dur, end=end,
        order='in', beforeWord='Breathe out',
        files=['brahms.mp3', '05 Quintet in B Minor, Op. 115 1 Allegro.mp3', '05_Quintet_in_B_Minor_Op._115_1_Allegro.mp3',
               'Quintet in B Minor, Op. 115 1 Allegro.mp3'],
        modes=[dict(key='four', label='Follow the phrases (4 bars)', cycles=four),
               dict(key='steady', label='Steady 6 per minute', cycles=steady)],
        ripples=[[x, int(x in turns)] for x in bars], ticks=[[x, int(x in turns)] for x in bars],
        bands=[[0, bt[0], 'n'], [bt[0], rep, 'a'], [rep, dev, 'b'], [dev, recap, 'w'], [recap, end, 'a'], [end, dur, 'n']],
        env=None, envStep=None,
        fonts='https://fonts.googleapis.com/css2?family=Spectral:ital,wght@1,400&family=Jost:wght@400;500&family=Spline+Sans+Mono:wght@400;500&display=swap',
        tokens=dict(display='"Spectral", "Baskerville", "Iowan Old Style", Georgia, serif', style='italic', weight=400,
                    light='--bg: #e8e8e9; --surface: #f3f3f4; --ink: #22211f; --muted: #5f5c57; --line: #cbcac7; --breath-rgb: 132 88 32; --wave-rgb: 146 142 134;',
                    dark='--bg: #121211; --surface: #1b1a18; --ink: #e5e3de; --muted: #9a958c; --line: #2e2c29; --breath-rgb: 222 178 112; --wave-rgb: 108 104 96;'))

def bach():
    D = json.load(open('data/bach_timeline.json'))
    bars, end, dur = D['bars'], D['end'], D['duration']
    t = lambda k: bars[k] if k < len(bars) else end
    def groups(size, inn):
        # breaths of `size` bars from bar 1, in for `inn` bars; the last breath runs out over the final chord
        return [[t(k), t(min(k + inn, len(bars) - 1)), t(k + size), 0] for k in range(0, len(bars) - 1, size)]
    three, four = groups(3, 1), groups(4, 2)
    turns = {c[0] for c in three}
    steady = [[R2(bars[0] + i), R2(bars[0] + i + 5), R2(bars[0] + i + 10), 0] for i in range(0, math.ceil(end - bars[0]), 10)]
    return dict(
        title='Bach Prelude Breathing', heading='Bach · Cello Suite No. 1, Prelude', key='bach-bwv1007', duration=dur, end=end,
        order='in', beforeWord='Breathe out',
        files=['bach.m4a', 'bach.mp3', '01 Bach (JS)_ Cello Suite #1 In G, B.m4a', '01_Bach_JS__Cello_Suite_1_In_G_B.m4a',
               'Bach (JS)_ Cello Suite #1 In G, BMV 1007 - Prelude.m4a'],
        modes=[dict(key='three', label='In 1 bar, out 2 bars', cycles=three),
               dict(key='four', label='Slower: 4 bars (in 2, out 2)', cycles=four),
               dict(key='steady', label='Steady 6 per minute', cycles=steady)],
        ripples=[[x, int(x in turns)] for x in bars], ticks=[[x, int(x in turns)] for x in bars],
        bands=[[0, bars[0], 'n']] + [[c[0], c[2], 'ab'[k % 2]] for k, c in enumerate(three)] + [[end, dur, 'n']],
        env=None, envStep=None,
        fonts='https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@1&family=Jost:wght@400;500&family=Spline+Sans+Mono:wght@400;500&display=swap',
        tokens=dict(display='"IM Fell English", "Iowan Old Style", "Palatino", Georgia, serif', style='italic', weight=400,
                    light='--bg: #e8e9ee; --surface: #f3f4f8; --ink: #1b1f2e; --muted: #575d70; --line: #c7cad6; --breath-rgb: 52 72 140; --wave-rgb: 130 138 160;',
                    dark='--bg: #0f111a; --surface: #161a26; --ink: #e1e4ee; --muted: #8b91a6; --line: #262b3b; --breath-rgb: 150 172 236; --wave-rgb: 92 100 124;'))

tpl = open('analysis/present_template.html').read()
os.makedirs('present', exist_ok=True)
for name, P in (('gymnopedie', satie()), ('hon-shirabe', hon()), ('mozart-k387', mozart()), ('brahms-op115', brahms()), ('bach-bwv1007', bach())):
    T = P.pop('tokens')
    tokens = (f":root {{ {T['light']} --f-display: {T['display']}; --display-style: {T['style']}; --display-weight: {T['weight']}; }}\n"
              f"@media (prefers-color-scheme: dark) {{ :root {{ {T['dark']} color-scheme: dark; }} }}")
    page = (tpl.replace('__TITLE__', P.pop('title').replace('&amp;', '&')).replace('__HEADING__', P.pop('heading'))
               .replace('__FONTS__', P.pop('fonts')).replace('__TOKENS__', tokens)
               .replace('__CONFIG__', json.dumps(P, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')))
    assert not re.search(r'__[A-Z]+__', page), name
    open(f'present/{name}.html', 'w').write(page)
    print(f'present/{name}.html', len(page), 'bytes')
