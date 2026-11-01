"""Decode a dialog tree: python -I dialog.py <db> <DialogId>  (takes, children, conditions, actions, locale)."""
import sqlite3, sys, uuid
db, did = sys.argv[1], sys.argv[2]; d=lambda x:x.decode('cp1252','replace')
s=sqlite3.connect(f'file:{db}/static.db4?mode=ro',uri=True); s.text_factory=d
l=sqlite3.connect(f'file:{db}/locale.db4?mode=ro',uri=True); l.text_factory=d
H=lambda b: b.hex() if isinstance(b,bytes) else b
dg=s.execute('select * from _Story_Dialogs where DialogId=?',(did,)).fetchone(); print('DIALOG', [H(x) for x in dg])
takes=s.execute('select TakeGUID,TakeId,TakeSpeaker,TakeType,TakeEmote,TakeSound,TakeSoundActiv,TakeText,TakeShortText,hex(ConditionRef),hex(ConditionBlock),TakeLocaId,TakeTimeStamp,TakeShortTextLocaId from _Story_DialogTakes where DialogGUID=? order by rowid',(dg[0],)).fetchall()
for t in takes:
    loc=t[11]; key=str(uuid.UUID(bytes_le=loc)) if isinstance(loc,bytes) and len(loc)==16 else loc
    lt=(l.execute('select LocaText from _Locale where LocaId=?',(key,)).fetchone() or l.execute('select LocaText from _Locale where LocaId=?',(t[1],)).fetchone() or [None])[0]
    kids=[r[0] for r in s.execute('select TakeChildId from _Story_DialogTakeChildMapping where TakeGUID=? order by TakeChildPosition',(t[0],))]
    acts=[r[0][:160] for r in s.execute('select ActionContent from _Story_DialogActions where TakeGUID=?',(t[0],))]
    conds=[r[0][:120] for r in s.execute("select ConditionType||': '||ConditionContent from _Story_DialogConditions where ConditionBlockGUID=?",(t[10] and bytes.fromhex(t[10]),))] if t[10]!='00000000000000000000000000000000' else []
    print(f"- {t[1]} [{t[3]}] spk={t[2]} snd={t[5]}/{t[6]} ts={t[12]} loca={key} short={t[8]!r}\n    text={str(t[7])[:90]!r} | locale={str(lt)[:90]!r}\n    kids={kids}\n    cond={conds}\n    acts={acts}")
