"""Fully decode an action script: every Statement/Condition row reachable, raw GUIDs, rowids."""
import sqlite3, sys, re, uuid
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec
seen = set()
def H(b): return b.hex().upper() if isinstance(b, bytes) else str(b)
def find(gidhex, ind):
    if gidhex in seen: print(ind, '(seen)', gidhex); return
    seen.add(gidhex); b = bytes.fromhex(gidhex)
    for tbl, cols in (('_Scripts_Statements', ('StatementGUID','StatementType','StatementContent','StatementBlockGUID')),
                      ('_Scripts_Conditions', ('ConditionGUID','ConditionType','ConditionContent','ConditionBlockGUID'))):
        for r in s.execute(f'select rowid,{",".join(cols)} from {tbl} where {cols[0]}=?', (b,)):
            print(ind, tbl[9:], 'row', r[0], 'GUID', H(r[1]), '| type', r[2], '| block', H(r[4]), '\n'+ind, '   content:', r[3])
            follow(r[3], ind + '    ')
        for r in s.execute(f'select rowid,{",".join(cols)} from {tbl} where {cols[3]}=? order by rowid', (b,)):
            print(ind, tbl[9:], '(member of block) row', r[0], 'GUID', H(r[1]), '| type', r[2], '\n'+ind, '   content:', r[3])
            follow(r[3], ind + '    ')
def follow(content, ind):
    for m in re.findall(r'[0-9A-Fa-f]{32}', content or ''): find(m.upper(), ind)
    for m in re.findall(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}', content or ''):
        find(uuid.UUID(m).bytes_le.hex().upper(), ind)
for name in sys.argv[2:]:
    seen.clear()
    r = s.execute('select ScriptName, StatementRef, StatementBlock from _Scripts_ActionScripts where ScriptName=?', (name,)).fetchone()
    print('#####', name, 'Ref', H(r[1]), 'Block', H(r[2]))
    print(' -- Ref:'); find(H(r[1]), '  ')
    print(' -- Block:'); find(H(r[2]), '  ')
