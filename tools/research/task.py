"""Decode tasks: python -I task.py <db> <TaskId>..."""
import sqlite3, sys, uuid
db=sys.argv[1]; d=lambda x:x.decode('cp1252','replace')
s=sqlite3.connect(f'file:{db}/static.db4?mode=ro',uri=True); s.text_factory=d
l=sqlite3.connect(f'file:{db}/locale.db4?mode=ro',uri=True); l.text_factory=d
g=sqlite3.connect(f'file:{db}/game.db4?mode=ro',uri=True); g.text_factory=d
L=lambda b: (l.execute('select LocaText from _Locale where LocaId=?',(str(uuid.UUID(bytes_le=b)),)).fetchone() or [None])[0] if isinstance(b,bytes) and len(b)==16 and any(b) else None
cols=[c[1] for c in s.execute('pragma table_info(_Story_Tasks)')]
for tid in sys.argv[2:]:
    r=dict(zip(cols, s.execute('select * from _Story_Tasks where TaskId=?',(tid,)).fetchone()))
    print('== TASK', tid, {k:(v.hex() if isinstance(v,bytes) else v) for k,v in r.items() if 'Loca' not in k and 'Block' not in k and 'Ref' not in k}, '| game:', g.execute('select TaskState from _Story_Tasks where TaskId=?',(tid,)).fetchone())
    print('   title/open/close:', L(r['TaskTitleLocaId']), '|', (L(r['TaskOpenTextLocaId']) or '')[:100], '|', (L(r['TaskCloseTextLocaId']) or '')[:80])
    print('   locaIds:', [str(uuid.UUID(bytes_le=r[k])) for k in ('TaskTitleLocaId','TaskOpenTextLocaId','TaskCloseTextLocaId')])
    for part, tbl in (('Open','_Story_TaskOpenConditions'),('Close','_Story_TaskCloseConditions')):
        print(f'   {part} cond ref={r[part+"ConditionRef"].hex()[:8]} blk={r[part+"ConditionBlock"].hex()[:8]}:', [(t,c[:110]) for t,c in s.execute(f'select ConditionType, ConditionContent from {tbl} where ConditionBlockGUID=? order by rowid',(r[part+'ConditionBlock'],))])
    for part, tbl in (('Open','_Story_TaskOpenActions'),('Close','_Story_TaskCloseActions')):
        print(f'   {part} actions:', [a[0][:200] for a in s.execute(f'select ActionContent from {tbl} where TaskGUID=?',(r['TaskGUID'],))])
