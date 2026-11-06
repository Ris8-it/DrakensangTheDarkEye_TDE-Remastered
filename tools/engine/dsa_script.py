"""Decode Drakensang data-driven scripts into readable pseudo-code.

Covers every place the game stores a statement/condition tree:
  action scripts      _Scripts_ActionScripts      (ScriptName -> Begin statement)
  condition scripts   _Scripts_ConditionScripts   (ScriptName -> condition row)
  status effects      _Scripts_StatusEffectScripts (Start / Trigger / Stop)
  state machines      _Script_StateMachines + States + Transitions (AI behaviours)
  tasks               _Story_Tasks open/close conditions + actions

Usage (Windows or Linux, Python 3.8+, stdlib only):
  python dsa_script.py <db_dir> action  <ScriptName>        e.g. roaming_01.xml
  python dsa_script.py <db_dir> cond    <ScriptName>        e.g. is_trap_active.xml
  python dsa_script.py <db_dir> status  <Id>                e.g. regeneration
  python dsa_script.py <db_dir> fsm     <MachineId>         e.g. clever_fighter
  python dsa_script.py <db_dir> task    <TaskId>
  python dsa_script.py <db_dir> list    action|cond|status|fsm   (names only)
  python dsa_script.py <db_dir> grep    <regex>              script names whose text matches

<db_dir> is the folder holding static.db4 (opened read-only).
"""
import re
import pathlib
import sqlite3
import sys
import uuid

GUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
ZERO = bytes(16)


def open_static(db_dir):
    con = sqlite3.connect(pathlib.Path(db_dir, 'static.db4').resolve().as_uri() + '?mode=ro', uri=True)
    con.text_factory = lambda b: b.decode('cp1252', 'replace')
    return con


def ref_to_blob(ref):
    """.NET GUID string -> 16-byte blob as stored in the db (bytes_le)."""
    return uuid.UUID(ref).bytes_le


class Decoder:
    def __init__(self, con):
        self.con = con
        self.stmt = {}
        for g, t, c in con.execute('select StatementGUID, StatementType, StatementContent from _Scripts_Statements'):
            self.stmt[g] = (t, c or '')
        self.cond = {}
        for tbl in ('_Scripts_Conditions', '_Story_TaskOpenConditions', '_Story_TaskCloseConditions',
                    '_Story_DialogConditions'):
            for g, t, c in con.execute(f'select ConditionGUID, ConditionType, ConditionContent from {tbl}'):
                self.cond.setdefault(g, (t, c or ''))

    # ---- conditions ----
    def cond_expr(self, blob, depth=0):
        if blob is None or blob == ZERO:
            return 'true'
        if depth > 40:
            return '<recursion>'
        row = self.cond.get(blob)
        if row is None:
            return f'<missing condition {uuid.UUID(bytes_le=blob)}>'
        typ, content = row
        refs = [ref_to_blob(m) for m in GUID_RE.findall(content)]
        if typ == 'Atom':
            return content.strip().rstrip(';').strip()
        if typ == 'Not':
            return 'not (' + self.cond_expr(refs[0], depth + 1) + ')'
        if typ in ('And', 'Or'):
            return '(' + f' {typ.lower()} '.join(self.cond_expr(r, depth + 1) for r in refs) + ')'
        if typ in ('Condition', 'OpenCondition', 'CloseCondition'):   # several children = implicit AND (vanilla does this)
            if not refs:
                return 'true'
            if len(refs) == 1:
                return self.cond_expr(refs[0], depth + 1)
            return '(' + ' and '.join(self.cond_expr(r, depth + 1) for r in refs) + ')'
        return f'<{typ}: {content}>'

    # ---- statements ----
    def stmt_lines(self, blob, ind=0, depth=0):
        pad = '    ' * ind
        if blob is None or blob == ZERO:
            return [pad + '(empty)']
        if depth > 60:
            return [pad + '<recursion>']
        row = self.stmt.get(blob)
        if row is None:
            return [pad + f'<missing statement {uuid.UUID(bytes_le=blob)}>']
        typ, content = row
        refs = [ref_to_blob(m) for m in GUID_RE.findall(content)]
        out = []
        if typ in ('Begin', 'Then', 'Else'):
            for r in refs:
                out += self.stmt_lines(r, ind, depth + 1)
        elif typ == 'Action':
            for verb in [v.strip() for v in content.split('; ') if v.strip()]:
                out.append(pad + verb.rstrip(';'))
        elif typ == 'If':
            c = self.stmt.get(refs[0], ('', ''))
            crefs = [ref_to_blob(m) for m in GUID_RE.findall(c[1])]
            out.append(pad + 'if ' + (self.cond_expr(crefs[0]) if crefs else 'true') + ':')
            if len(refs) > 1:
                out += self.stmt_lines(refs[1], ind + 1, depth + 1)
            if len(refs) > 2:
                out.append(pad + 'else:')
                out += self.stmt_lines(refs[2], ind + 1, depth + 1)
        elif typ == 'Condition':
            out.append(pad + 'cond ' + (self.cond_expr(refs[0]) if refs else 'true'))
        else:
            out.append(pad + f'<{typ}> {content}')
        return out

    def text(self, blob, ind=1):
        return '\n'.join(self.stmt_lines(blob, ind))

    # ---- entry points ----
    def action(self, name):
        r = self.con.execute('select StatementRef from _Scripts_ActionScripts where ScriptName=?', (name,)).fetchone()
        return f'action script {name}\n' + (self.text(r[0]) if r else '    <not found>')

    def condition(self, name):
        r = self.con.execute('select ConditionRef from _Scripts_ConditionScripts where ScriptName=?', (name,)).fetchone()
        return f'condition script {name}\n    ' + (self.cond_expr(r[0]) if r else '<not found>')

    def status(self, sid):
        r = self.con.execute('select StatusEffectOnStartRef, StatusEffectOnTriggerRef, StatusEffectOnStopRef, '
                             'StatusEffectCategories, StatusEffectStackable, StatusEffectPower '
                             'from _Scripts_StatusEffectScripts where Id=?', (sid,)).fetchone()
        if not r:
            return f'status {sid}: <not found>'
        out = [f'status effect {sid}  categories={r[3]!r} stackable={r[4]} power={r[5]}']
        for label, blob in (('on start', r[0]), ('on trigger (loop)', r[1]), ('on stop', r[2])):
            out.append(f'  {label}:')
            out.append(self.text(blob, 2))
        return '\n'.join(out)

    def fsm(self, mid):
        r = self.con.execute('select StartState from _Script_StateMachines where Id=?', (mid,)).fetchone()
        if not r:
            return f'state machine {mid}: <not found>'
        out = [f'state machine {mid}  (start: {r[0]})']
        states = self.con.execute('select StateName, OnEntryStatementRef, OnFrameStatementRef, OnExitStatementRef '
                                  'from _Script_StateMachineStates where MachineName=? order by rowid', (mid,)).fetchall()
        for name, en, fr, ex in states:
            out.append(f'  state {name}')
            for label, blob in (('entry', en), ('frame', fr), ('exit', ex)):
                if blob and blob != ZERO:
                    out.append(f'    on {label}:')
                    out.append(self.text(blob, 3))
            for to, cref, sref, idx in self.con.execute(
                    'select ToState, ConditionRef, StatementRef, TransitionIndex from _Script_StateTransitions '
                    'where MachineName=? and StateName=? order by TransitionIndex', (mid, name)):
                out.append(f'    -> {to}  [{idx}] when {self.cond_expr(cref)}')
                if sref and sref != ZERO:
                    out.append(self.text(sref, 4))
        return '\n'.join(out)

    def task(self, tid):
        r = self.con.execute('select TaskGUID, TaskState, OpenConditionRef, CloseConditionRef, TaskParentGuid '
                             'from _Story_Tasks where TaskId=?', (tid,)).fetchone()
        if not r:
            return f'task {tid}: <not found>'
        out = [f'task {tid} (initial state {r[1]})']
        out.append('  open when:  ' + self.cond_expr(r[2]))
        for (a,) in self.con.execute('select ActionContent from _Story_TaskOpenActions where TaskGUID=?', (r[0],)):
            out.append('  on open:    ' + a.strip())
        out.append('  close when: ' + self.cond_expr(r[3]))
        for (a,) in self.con.execute('select ActionContent from _Story_TaskCloseActions where TaskGUID=?', (r[0],)):
            out.append('  on close:   ' + a.strip())
        return '\n'.join(out)

    def names(self, kind):
        q = {'action': 'select ScriptName from _Scripts_ActionScripts',
             'cond': 'select ScriptName from _Scripts_ConditionScripts',
             'status': 'select Id from _Scripts_StatusEffectScripts',
             'fsm': 'select Id from _Script_StateMachines'}[kind]
        return sorted(r[0] for r in self.con.execute(q))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    d = Decoder(open_static(argv[1]))
    cmd = argv[2]
    args = argv[3:]
    if cmd == 'list':
        print('\n'.join(d.names(args[0])))
    elif cmd == 'grep':
        rx = re.compile(args[0], re.I)
        for n in d.names('action'):
            if rx.search(d.action(n)):
                print(n)
    else:
        fn = {'action': d.action, 'cond': d.condition, 'status': d.status, 'fsm': d.fsm, 'task': d.task}[cmd]
        for a in args:
            print(fn(a))
            print()
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv))
