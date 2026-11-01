"""Spoiler scan: lists every journal entry, dialogue line and item text the pack ADDS that names a later place, boss or monster.
Run through validate.py --spoilers (or: python -I spoiler_scan.py <installed db dir> <baseline db dir>).
Rule (docs/DESIGN_RULES.md): quest titles, objectives, early dialogue and early item texts stay vague. Hits are fine only where the
player already stands there or already holds the thing (a trophy's own text, a line said in that place, endgame dialogue)."""
import sqlite3, uuid, re, sys
A, B = sys.argv[1], sys.argv[2]
def L(p): 
    c = sqlite3.connect(p); c.text_factory = lambda b: b.decode('cp1252', 'replace'); return c
s, l = L(A + '/static.db4'), L(A + '/locale.db4')
bs, bl = L(B + '/static.db4'), L(B + '/locale.db4')
loc = dict(l.execute('select LocaId, LocaText from _Locale')); bloc = dict(bl.execute('select LocaId, LocaText from _Locale'))
def key(b): 
    if b is None: return None
    if isinstance(b, str): b = b.encode('cp1252', 'replace')
    try: return str(uuid.UUID(bytes_le=bytes(b)))
    except Exception: return None
s2 = sqlite3.connect(A + '/static.db4')
out = []
for tid, *ids in s2.execute('select TaskId, TaskTitleLocaId, TaskOpenTextLocaId, TaskCloseTextLocaId from _Story_Tasks'):
    for kind, b in zip(('title', 'open', 'close'), ids):
        k = key(b); t = loc.get(k)
        if t and t != bloc.get(k): out.append(('TASK', tid, kind, t))
for did, tk, b in s2.execute('select DialogId, TakeId, TakeLocaId from _Story_DialogTakes'):
    k = key(b); t = loc.get(k)
    if t and t != bloc.get(k): out.append(('DLG', did, tk, t))
for k, t in loc.items():
    if k.startswith(('lookat_arm', 'infoid_arm')) and t != bloc.get(k): out.append(('ITEM', k, '', t))
for k, t in loc.items():
    if t != bloc.get(k) and not k.startswith(('lookat_arm', 'infoid_arm')) and not any(k == key(x) for x in ()): pass
TERMS = r"cyclop|zyklop|spider|emerald|ratzinsk|rat[- ]?(mother|queen|plague|king)|plague|dragon|japhgur|purplewyrm|wyrm|tallon|murolosh|moorbridge|fire falls|gruldur|silver falls|umbracor|grolm|crypt|tatzelwurm|harpy|nadoret|oracle|pal.?na.?thar|amoeb|rakorium|dark forest|blood mountain|drakensang|kosch|deep"
for r in out:
    hits = sorted(set(m.group(0).lower() for m in re.finditer(TERMS, r[3], re.I)))
    if hits: print(f"{r[0]}|{r[1]}|{r[2]}|{','.join(hits)}|{r[3][:230]}".replace('\n', ' '))
print('ours scanned:', len(out), {k: sum(1 for r in out if r[0]==k) for k in ('TASK','DLG','ITEM')})
