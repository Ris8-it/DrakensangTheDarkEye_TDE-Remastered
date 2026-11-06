"""Inventory every script "word" the vanilla data uses, and where it is used.

Collects, with counts per context:
  * action verbs   (script statements, dialog actions, task open/close actions, trigger Enter/Leave/Inside
                    actions, state-machine states, template string columns that hold actions)
  * condition atoms (script conditions, dialog/task conditions, trigger EntityFilter, state transitions)
  * hook events    (ScriptOverride on:/can: strings, _DSA_Preset rows)
  * argument names seen per verb/atom (merged), with one example

Usage:  python vocab.py <db_dir> [out.md]
Writes markdown to out.md (default: stdout).  stdlib only, read-only.
"""
import collections
import re
import pathlib
import sqlite3
import sys

VERB_RE = re.compile(r'(?:^|;)\s*([A-Z][A-Za-z0-9_]*)((?:\s+[A-Za-z0-9_]+="[^"]*")*)\s*(?=;|$)')
ARG_RE = re.compile(r'([A-Za-z0-9_]+)="')


def connect(path):
    c = sqlite3.connect(pathlib.Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    c.text_factory = lambda b: b.decode('cp1252', 'replace')
    return c


class Bag:
    def __init__(self):
        self.count = collections.Counter()
        self.ctx = collections.defaultdict(collections.Counter)
        self.args = collections.defaultdict(set)
        self.example = {}

    def add(self, text, ctx):
        for m in VERB_RE.finditer(text or ''):
            w, a = m.group(1), m.group(2)
            if w in ('True', 'False'):
                w = w  # literal condition atoms
            self.count[w] += 1
            self.ctx[w][ctx] += 1
            self.args[w].update(ARG_RE.findall(a))
            if w not in self.example or len(self.example[w]) < len(m.group(0)) < 220:
                self.example[w] = m.group(0).strip(' ;')


def collect(db_dir):
    s = connect(f'{db_dir}/static.db4')
    g = connect(f'{db_dir}/game.db4')
    verbs, atoms = Bag(), Bag()

    # statement blocks: find which "owner" each block belongs to
    owner = {}
    for (blk,) in s.execute('select StatementBlock from _Scripts_ActionScripts'):
        owner[blk] = 'action script'
    for row in s.execute('select StatusEffectOnStartBlock, StatusEffectOnTriggerBlock, StatusEffectOnStopBlock '
                         'from _Scripts_StatusEffectScripts'):
        for b in row:
            owner[b] = 'status effect'
    for row in s.execute('select OnEntryStatementBlock, OnFrameStatementBlock, OnExitStatementBlock '
                         'from _Script_StateMachineStates'):
        for b in row:
            owner[b] = 'state machine'
    for (b,) in s.execute('select StatementBlock from _Script_StateTransitions'):
        owner[b] = 'state machine'
    for c, blk in s.execute("select StatementContent, StatementBlockGUID from _Scripts_Statements "
                            "where StatementType='Action'"):
        verbs.add(c, owner.get(blk, 'statement (other)'))

    cowner = {}
    for (blk,) in s.execute('select ConditionBlock from _Scripts_ConditionScripts'):
        cowner[blk] = 'condition script'
    for (blk,) in s.execute('select ConditionBlock from _Script_StateTransitions'):
        cowner[blk] = 'state transition'
    for c, blk in s.execute("select ConditionContent, ConditionBlockGUID from _Scripts_Conditions where ConditionType='Atom'"):
        atoms.add(c, cowner.get(blk, 'script if'))
    for tbl, ctx in (('_Story_DialogConditions', 'dialog'), ('_Story_TaskOpenConditions', 'task open'),
                     ('_Story_TaskCloseConditions', 'task close')):
        for (c,) in s.execute(f"select ConditionContent from {tbl} where ConditionType='Atom'"):
            atoms.add(c, ctx)
    for tbl, ctx in (('_Story_DialogActions', 'dialog'), ('_Story_TaskOpenActions', 'task open'),
                     ('_Story_TaskCloseActions', 'task close')):
        for (c,) in s.execute(f'select ActionContent from {tbl}'):
            verbs.add(c, ctx)

    # trigger-like instances (game.db4) + their templates
    for db, prefix in ((g, '_Instance_'), (s, '_Template_')):
        for cat in ('Trigger', 'Trap', 'EncounterTrigger', 'AreaSpellTrigger'):
            t = prefix + cat
            for flt, en, lv, ins in db.execute(f'select EntityFilter, EnterActions, LeaveActions, InsideActions from {t}'):
                atoms.add(flt, f'{cat} filter')
                for txt, w in ((en, 'Enter'), (lv, 'Leave'), (ins, 'Inside')):
                    verbs.add(txt, f'{cat} {w}')

    # events
    events = collections.Counter()
    for db in (s, g):
        for (t,) in db.execute("select name from sqlite_master where type='table' and "
                               "(name like '_Template_%' or name like '_Instance_%')"):
            cols = [x[1] for x in db.execute(f'pragma table_info("{t}")')]
            cat = t.split('_', 2)[2]
            if 'ScriptOverride' in cols:
                for (v,) in db.execute(f'select ScriptOverride from "{t}" where ScriptOverride != ""'):
                    for m in re.finditer(r'(on|can):(\w+):', v):
                        events[(m.group(1), m.group(2), cat, 'ScriptOverride')] += 1
    preset_users = collections.defaultdict(set)
    for (t,) in s.execute("select name from sqlite_master where name like '_Template_%'"):
        cols = [x[1] for x in s.execute(f'pragma table_info("{t}")')]
        if 'ScriptPreset' in cols:
            for (p,) in s.execute(f'select distinct ScriptPreset from "{t}" where ScriptPreset != ""'):
                preset_users[p].add(t[10:])
    for name, typ, act in s.execute('select PresetName, PresetType, PresetActionName from _DSA_Preset'):
        for cat in preset_users.get(name, {'(unused preset)'}):
            events[('on' if typ == 'OnAction' else 'can', act, cat, 'ScriptPreset')] += 1
    return verbs, atoms, events


def md(verbs, atoms, events):
    out = ['# Script vocabulary (generated by tools/engine/vocab.py)', '',
           'Counts are occurrences in vanilla data. "Contexts" says where the word appears; a verb that works in one',
           'context is **inferred** to work in the others (one action/condition factory), but test before relying on it.', '']
    out.append('## Hook events')
    out.append('')
    out.append('| kind | event | category | via | uses |')
    out.append('|---|---|---|---|---|')
    for (k, e, c, via), n in sorted(events.items()):
        out.append(f'| {k} | {e} | {c} | {via} | {n} |')
    for title, bag in (('Action verbs', verbs), ('Condition atoms', atoms)):
        out += ['', f'## {title} ({len(bag.count)})', '', '| word | uses | contexts | arguments | example |',
                '|---|---|---|---|---|']
        for w, n in sorted(bag.count.items(), key=lambda x: x[0].lower()):
            ctx = ', '.join(f'{c} {k}' for c, k in bag.ctx[w].most_common())
            ex = bag.example.get(w, '').replace('|', '\\|')
            out.append(f'| `{w}` | {n} | {ctx} | {" ".join(sorted(bag.args[w]))} | `{ex}` |')
    return '\n'.join(out) + '\n'


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    text = md(*collect(argv[1]))
    if len(argv) > 2:
        with open(argv[2], 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
