import sqlite3, sys, uuid, re
db = sys.argv[1]; dec = lambda b: b.decode('cp1252','replace')
s = sqlite3.connect(f'file:{db}/static.db4?mode=ro', uri=True); s.text_factory = dec
H = lambda b: b.hex().upper() if isinstance(b, bytes) else b
def show(gid, ind):
    for tbl, c in (('_Scripts_Statements','Statement'),('_Scripts_Conditions','Condition')):
        for r in s.execute(f'select rowid,{c}GUID,{c}Type,{c}Content,{c}BlockGUID from {tbl} where {c}GUID=?', (gid,)):
            print(ind, f'{tbl[9:12]} r{r[0]} {H(r[1])} [{r[2]}] blk {H(r[4])}: {r[3]}')
            for m in re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', r[3] or ''):
                show(uuid.UUID(m).bytes_le, ind+'  ')
cols=[c[1] for c in s.execute('pragma table_info(_Scripts_StatusEffectScripts)')]
for n in sys.argv[2:]:
    r = dict(zip(cols, s.execute('select rowid,* from _Scripts_StatusEffectScripts where Id=?', (n,)).fetchone()[1:]))
    print('==', n, {k: H(v) for k, v in r.items()})
    for part in ('Start','Trigger','Stop'):
        print('  ', part); show(r[f'StatusEffectOn{part}Ref'], '    ')
        print('    members of block', [ (x[0], H(x[1])) for x in s.execute('select rowid, StatementGUID from _Scripts_Statements where StatementBlockGUID=?', (r[f'StatusEffectOn{part}Block'],))])
