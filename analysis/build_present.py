"""Build the standalone presentation pages: python3 analysis/build_present.py (from the repo root).

Reads data/timeline.json (Satie) and data/hon_timeline.json (Hon Shirabe), fills analysis/present_template.html,
and writes present/gymnopedie.html and present/hon-shirabe.html. Each page plays the MP3 sitting beside it.
"""
import json, math, os

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

tpl = open('analysis/present_template.html').read()
os.makedirs('present', exist_ok=True)
for name, P in (('gymnopedie', satie()), ('hon-shirabe', hon())):
    T = P.pop('tokens')
    tokens = (f":root {{ {T['light']} --f-display: {T['display']}; --display-style: {T['style']}; --display-weight: {T['weight']}; }}\n"
              f"@media (prefers-color-scheme: dark) {{ :root {{ {T['dark']} color-scheme: dark; }} }}")
    page = (tpl.replace('__TITLE__', P.pop('title').replace('&amp;', '&')).replace('__HEADING__', P.pop('heading'))
               .replace('__FONTS__', P.pop('fonts')).replace('__TOKENS__', tokens)
               .replace('__CONFIG__', json.dumps(P, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')))
    assert '__' not in page.replace('__proto__', ''), name
    open(f'present/{name}.html', 'w').write(page)
    print(f'present/{name}.html', len(page), 'bytes')
