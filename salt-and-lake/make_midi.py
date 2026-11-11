"""Write salt-and-lake.mid: the same notes the page plays, as a standard MIDI file.

No dependencies. Run: python3 salt-and-lake/make_midi.py
"""
import os
import struct

BPM = 54
PPQ = 480
END = 25.5  # beats; bar 8 plus the fermata

# (start beat, MIDI note, velocity, end beat). The sustain pedal is down throughout.
STRIKES = [
    # Bar 1: B4 + C5 together, forte. Keys stay down.
    (0, 71, 90, 12), (0, 72, 90, 12),
    # Bar 3: C2, G2, E3 enter below, one per beat, while the clash still rings.
    (6, 36, 58, 12), (7, 43, 52, 12), (8, 52, 50, 12),
    # Bar 5: all five together, piano.
    (12, 36, 50, END), (12, 43, 46, END), (12, 52, 46, END),
    (12, 71, 58, 18), (12, 72, 58, 18),
    # Bar 7: the clash alone again, pianissimo, over the ringing bass.
    (18, 71, 40, END), (18, 72, 40, END),
]


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def tick(beat):
    return round(beat * PPQ)


def build():
    events = []  # (tick, order, bytes); note-offs sort before note-ons at the same tick
    events.append((0, 0, b"\xff\x03" + vlq(13) + b"Salt and Lake"))
    events.append((0, 0, b"\xff\x51\x03" + struct.pack(">I", round(60_000_000 / BPM))[1:]))
    events.append((0, 0, b"\xff\x58\x04\x03\x02\x18\x08"))  # 3/4
    events.append((0, 0, b"\xc0\x00"))  # acoustic grand
    events.append((0, 1, b"\xb0\x40\x7f"))  # pedal down
    for start, note, vel, end in STRIKES:
        events.append((tick(start), 2, bytes([0x90, note, vel])))
        events.append((tick(end), 1, bytes([0x80, note, 0])))
    events.append((tick(END), 1, b"\xb0\x40\x00"))  # pedal up
    events.sort(key=lambda e: (e[0], e[1]))

    track = bytearray()
    last = 0
    for t, _, data in events:
        track += vlq(t - last) + data
        last = t
    track += vlq(tick(2)) + b"\xff\x2f\x00"  # two beats of silence for the ring-out
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ)
    return header + b"MTrk" + struct.pack(">I", len(track)) + bytes(track)


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salt-and-lake.mid")
    with open(path, "wb") as f:
        f.write(build())
    print("wrote", path)
