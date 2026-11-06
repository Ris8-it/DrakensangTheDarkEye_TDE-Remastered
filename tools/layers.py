"""Engine layers: generators for the 18 "extra layers" mapped in docs/ENGINE_ARCHITECTURE.md (section 11).

Everything works through a dsa.Mod (same install/undo/verify machinery as the rest of the pack). Each layer is one
method group on `Layers`; all of them write vanilla-shaped rows and an exact undo.

    from dsa import Mod
    from layers import Layers, A, Not, And, Or
    m = Mod(db, 'mymod'); L = Layers(m)
    L.action_script('my_script.xml', [A('ShowOverHeadMessage', msg='Hi', who='Hero'),
                                      ('if', 'IsPartyMember who="Rhulana"', [A('Heal', who='Rhulana', fixedLE=5)])])

Layers (numbers = rank in the architecture doc):
  1  reactive presets        preset(), attach_preset()                 on:/can: events of beings and objects
  2  can: gates              condition_script(), gate()                veto scripts for Use/Hit/Open/TriggerTrap
  3  custom AI machines      clone_machine() + Machine edits           _Script_StateMachine* rows
  4  global AI tuning        tune_machine()                            guarded edits of vanilla machine statements
  5  scripted attacks        script_attack(), add_attack_chance()      Game::ScriptCombatAction + CombatScriptName
  6  level-enter scripts     on_level_enter()                          _Instance_Levels.LevelEnterScript
  7  trigger volumes         trigger()                                 _Instance_Trigger
  8  zones                   marker(), zone atoms (inside(), all_inside())
  9  heartbeats / watchers   heartbeat(), watcher()                    status-effect loops, WaitForCondition
 10  interactive objects     object(), state_object()                  _Template/_Instance_Object, StateObject
 11  service points          clone_instance(), herb_patch()            WorkBench / Herb / DestroyableEntity / Entry
 12  encounters              encounter()                               EncounterTrigger + SpawnPoints + SpawnAtEncounter
 13  probes                  probe_item()                              usable test items in Rhulana's pack
 14  runtime XML tables      see tools/loosefiles.py                   loose data/tables/*.xml (effects, xp, ...)
 15  factions                faction()                                 _Template_Faction column + row + _Attributes
 16  area hazards            area_hazard()                             _Template_AreaSpellTrigger + CreateEntity
 17  blueprint extensions    see tools/loosefiles.py                   loose data/tables/blueprints.xml
 18  new categories          category()                                _Categories + tables + blueprint entry

Rules learned the hard way (docs/ENGINE_REFERENCE.md): status ids letters/digits only; no If without Else inside a
status-effect block; every PK is ON CONFLICT REPLACE so GUIDs are deterministic (uuid5) and collision-checked;
sqlite3.exe 3.6.1 runs the installers (no IS operator, no DROP COLUMN, no table-valued pragmas).
"""
import re, struct, uuid
from dsa import U, lit, insert, IDENT

Z = bytes(16)
SEL = 'actionSelection="script,quest,dialog"'
PARTY = ['Rhulana', 'Forgrimm_Sohn_des_Ferolax', 'Kladdis_Schladromir', 'pc_gwendala', 'Dranor_PC', 'pc_jost', 'pc_traldar',
         'pc_auralia', 'pc_nasreddin', 'pc_ancoron']   # Name column of the companions (_Instance_PC); the main hero is token "Hero"
GUID_RE = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


# ---------------------------------------------------------------- script text helpers
def A(verb, _sel=SEL, **kw):
    """One action string in vanilla syntax: A('Hurt', who='AimedEntity', fixedDamage=2) -> 'Hurt who="AimedEntity" fixedDamage="2" actionSelection=...'."""
    args = ' '.join(f'{k}="{v}"' for k, v in kw.items())
    return f'{verb} {args} {_sel}'.replace('  ', ' ').strip() if _sel else f'{verb} {args}'.strip()

def C(atom, **kw):
    """One condition atom: C('HasStatusEffect', id='burning', who='AimedEntity')."""
    return (atom + ' ' + ' '.join(f'{k}="{v}"' for k, v in kw.items())).strip()

def Not(x): return ('not', x)
def And(*xs): return ('and', list(xs))
def Or(*xs): return ('or', list(xs))


class Script:
    """A statement block in vanilla row shape. items: action strings, ('if', cond, then_items[, else_items]).
    Consecutive actions share one Action row (vanilla does the same). Conditions: atom string or Not/And/Or trees."""
    def __init__(self, key):
        self.key, self.n, self.st, self.co = key, 0, [], []
        self.guid = U(key, 'block')
        self.ref = None

    def _g(self, tag):
        self.n += 1
        return U(self.key, f'{tag}{self.n}')

    def stmt(self, typ, content):
        x = self._g('s')
        self.st.append((x, typ, content, self.guid))
        return x

    def cond_rows(self, spec, blk, rows):
        if isinstance(spec, str):
            x = self._g('c'); rows.append((x, 'Atom', spec.strip().rstrip(';') + '; ', blk)); return x
        op, arg = spec
        if op == 'not':
            inner = self.cond_rows(arg, blk, rows)
            x = self._g('c'); rows.append((x, 'Not', str(inner), blk)); return x
        kids = [self.cond_rows(a, blk, rows) for a in arg]
        if len(kids) == 1:
            return kids[0]
        x = self._g('c'); rows.append((x, op.capitalize(), ';'.join(map(str, kids)), blk)); return x

    def condition(self, spec):
        """Condition rows in their own block; returns (top 'Condition' row, block) for transitions/condition scripts."""
        blk = self._g('cb'); rows = []
        top = self.cond_rows(spec, blk, rows)
        c = self._g('c'); rows.append((c, 'Condition', str(top), blk))
        self.co += rows
        return c, blk

    def body(self, items):
        out, run = [], []
        def flush():
            if run:
                out.append(self.stmt('Action', ''.join(run))); run.clear()
        for it in items:
            if isinstance(it, str):
                run.append(it.strip().rstrip(';') + '; ')
                continue
            flush()
            assert it[0] == 'if', it
            c, blk = self.condition(it[1])
            cs = self.stmt('Condition', f'{c};{blk}')
            then = self.stmt('Then', ';'.join(map(str, self.body(it[2]))))
            if len(it) > 3 and it[3] is not None:
                els = self.stmt('Else', ';'.join(map(str, self.body(it[3]))))
                out.append(self.stmt('If', f'{cs};{then};{els}'))
            else:
                out.append(self.stmt('If', f'{cs};{then}'))
        flush()
        return out

    def begin(self, items):
        self.ref = self.stmt('Begin', ';'.join(map(str, self.body(items))))
        return self


def no_if_without_else(items):
    """Status-effect blocks assert on an If without Else (ifthenelseaction.cc:232): add empty-wait Else branches."""
    out = []
    for it in items:
        if isinstance(it, tuple) and it[0] == 'if':
            els = it[3] if len(it) > 3 and it[3] else ['WaitAction duration="0.1" permanent="false" actionSelection="script"']
            out.append(('if', it[1], no_if_without_else(it[2]), no_if_without_else(els)))
        else:
            out.append(it)
    return out


def xform(pos, scale=(1.0, 1.0, 1.0), rot=None):
    """4x4 row-major float matrix blob (Nebula: translation in elements 12..14). rot: 3x3 rows or None."""
    r = rot or ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    m = []
    for i in range(3):
        m += [r[i][0] * scale[i], r[i][1] * scale[i], r[i][2] * scale[i], 0.0]
    m += [pos[0], pos[1], pos[2], 1.0]
    return struct.pack('<16f', *m)


class Layers:
    def __init__(self, mod):
        self.m, self.ns = mod, mod.ns
        self.checks_static, self.checks_game = [], []   # verify queries: (label, sql returning a number, expected)
        self._presets = {}

    # ================================================================ shared plumbing
    def _emit(self, scr):
        m = self.m
        for x, typ, content, blk in scr.st:
            m.static.append(insert('_Scripts_Statements', dict(StatementGUID=x, StatementType=typ, StatementContent=content, StatementBlockGUID=blk)))
        for x, typ, content, blk in scr.co:
            m.static.append(insert('_Scripts_Conditions', dict(ConditionGUID=x, ConditionType=typ, ConditionContent=content, ConditionBlockGUID=blk)))
        if scr.st:
            m.undo_static.append(f"DELETE FROM _Scripts_Statements WHERE StatementBlockGUID={lit(scr.guid)};")
        for blk in sorted({c[3] for c in scr.co}, key=str):
            m.undo_static.append(f"DELETE FROM _Scripts_Conditions WHERE ConditionBlockGUID={lit(blk)};")
        m.new_guids += [x for x, *_ in scr.st] + [x for x, *_ in scr.co]

    def guarded_update(self, db, table, where, col, new, old=None):
        """UPDATE one column only if it still holds the value this build read (so a different baseline is left alone),
        undo restores it only if it still holds ours. where: dict of key columns."""
        con = self.m.s if db == 'static' else self.m.g
        w = ' AND '.join(f'"{k}"={lit(v)}' for k, v in where.items())
        if old is None:
            r = con.execute(f'select "{col}" from "{table}" where {w}', tuple()).fetchone()
            assert r is not None, (table, where, col)
            old = r[0]
        if old == new:
            return
        oldc = f'"{col}" IS NULL' if old is None else f'"{col}"={lit(old)}'   # IS NULL is fine in 3.6.1, only "a IS b" is not
        do = f'UPDATE "{table}" SET "{col}"={lit(new)} WHERE {w} AND {oldc};'
        undo = f'UPDATE "{table}" SET "{col}"={lit(old)} WHERE {w} AND "{col}"={lit(new)};'
        (self.m.static if db == 'static' else self.m.game).append(do)
        (self.m.undo_static if db == 'static' else self.m.undo_game).append(undo)
        (self.checks_static if db == 'static' else self.checks_game).append(
            (f'{table}.{col} of ' + ''.join(v.hex() if isinstance(v, bytes) else str(v) for v in where.values()), f'SELECT count(*) FROM "{table}" WHERE {w} AND "{col}"={lit(new)}', 1))

    def anchor_pos(self, level, anchor):
        """anchor = (instance category, Name[, column]) or (x, y, z) -> (x, y, z) in level coordinates."""
        if all(isinstance(v, (int, float)) for v in anchor):
            return tuple(anchor)
        cat, val, col = (tuple(anchor) + ('Name',))[:3]
        r = self.m.g.execute(f'select Transform from "_Instance_{cat}" where "{col}"=? and _Level=? order by rowid', (val, level)).fetchone()
        assert r, (anchor, level)
        return struct.unpack('<16f', r[0])[12:15]

    def place_row(self, cat, donor_sql, donor_args, over, tag):
        """Insert a new instance row cloned from a vanilla donor row (all columns copied, then `over`). Undo deletes it."""
        m = self.m
        d = m.g.execute(f'select * from "_Instance_{cat}" where {donor_sql} order by rowid', donor_args).fetchone()
        assert d, (cat, donor_sql, donor_args)
        row = dict(d)
        row.update(over)
        row['Guid'] = U(self.ns, 'inst', cat, tag).bytes
        m.game += [f'DELETE FROM "_Instance_{cat}" WHERE Guid={lit(row["Guid"])};', insert(f'_Instance_{cat}', row)]
        m.undo_game.insert(0, f'DELETE FROM "_Instance_{cat}" WHERE Guid={lit(row["Guid"])};')
        self.checks_game.append((f'{cat} {row.get("Name", tag)} placed', f'SELECT count(*) FROM "_Instance_{cat}" WHERE Guid={lit(row["Guid"])}', 1))
        return row

    def clone_template(self, cat, base, tid, **over):
        m = self.m
        r = m.s.execute(f'select * from "_Template_{cat}" where Id=?', (base,)).fetchone()
        assert r, (cat, base)
        t = dict(r)
        for k in over:
            assert k in t, (cat, k)
        t.update(Id=tid, **over)
        m.static += [f'DELETE FROM "_Template_{cat}" WHERE Id={lit(tid)};', insert(f'_Template_{cat}', t)]
        m.undo_static.append(f'DELETE FROM "_Template_{cat}" WHERE Id={lit(tid)};')
        self.checks_static.append((f'template {cat}/{tid}', f'SELECT count(*) FROM "_Template_{cat}" WHERE Id={lit(tid)}', 1))
        return t

    # ================================================================ scripts
    def action_script(self, name, items):
        scr = Script(f'{self.ns}/act/{name}').begin(items)
        self.m.static.append(f'-- action script {name}')
        self._emit(scr)
        self.m.static.append(insert('_Scripts_ActionScripts', dict(ScriptName=name, StatementRef=scr.ref, StatementBlock=scr.guid)))
        self.m.undo_static.append(f"DELETE FROM _Scripts_ActionScripts WHERE ScriptName={lit(name)};")
        self.checks_static.append((f'action script {name}', f"SELECT count(*) FROM _Scripts_ActionScripts WHERE ScriptName={lit(name)}", 1))
        return name

    # ---- layer 2: condition scripts and can: gates
    def condition_script(self, name, cond):
        scr = Script(f'{self.ns}/cond/{name}')
        ref, blk = scr.condition(cond)
        self.m.static.append(f'-- condition script {name}')
        self._emit(scr)
        self.m.static.append(insert('_Scripts_ConditionScripts', dict(ScriptName=name, ConditionRef=ref, ConditionBlock=blk)))
        self.m.undo_static.append(f"DELETE FROM _Scripts_ConditionScripts WHERE ScriptName={lit(name)};")
        return name

    @staticmethod
    def override(on=None, can=None):
        """ScriptOverride string: override(on={'Use': 'x.xml'}, can={'Use': 'y.xml'}) -> 'can:Use:y.xml;on:Use:x.xml'."""
        parts = [f'can:{e}:{s}' for e, s in (can or {}).items()] + [f'on:{e}:{s}' for e, s in (on or {}).items()]
        return ';'.join(parts)

    # ---- layer 1: presets
    def preset(self, name, on=None, can=None, base=None):
        """New _DSA_Preset (one row per event). base: an existing vanilla preset whose rows are copied first
        (events we also define replace the vanilla script for that event)."""
        m = self.m
        rows = {}
        if base:
            for typ, act, script in m.s.execute('select PresetType, PresetActionName, PresetScriptName from _DSA_Preset where PresetName=?', (base,)):
                rows[(typ, act)] = script
        for e, sname in (on or {}).items():
            rows[('OnAction', e)] = sname
        for e, sname in (can or {}).items():
            rows[('CanAction', e)] = sname
        assert not m.s.execute('select 1 from _DSA_Preset where PresetName=?', (name,)).fetchone(), f'preset {name} exists in vanilla'
        m.static.append(f'-- preset {name}' + (f' (based on {base})' if base else ''))
        m.static.append(f"DELETE FROM _DSA_Preset WHERE PresetName={lit(name)};")
        for (typ, act), sname in rows.items():
            m.static.append(insert('_DSA_Preset', dict(PresetName=name, PresetType=typ, PresetActionName=act, PresetScriptName=sname)))
        m.undo_static.append(f"DELETE FROM _DSA_Preset WHERE PresetName={lit(name)};")
        self.checks_static.append((f'preset {name} rows', f"SELECT count(*) FROM _DSA_Preset WHERE PresetName={lit(name)}", len(rows)))
        self._presets[name] = rows
        return name

    def attach_preset(self, cat, tid, on=None, can=None, instances=True):
        """Give template `tid` (and its placed instances) our events, keeping the vanilla preset's own events."""
        old = self.m.s.execute(f'select ScriptPreset from "_Template_{cat}" where Id=?', (tid,)).fetchone()
        assert old is not None, (cat, tid)
        old = old[0] or ''
        name = self._stable_name(old, on, can)
        if name not in self._presets:
            self.preset(name, on=on, can=can, base=old or None)
        self.guarded_update('static', f'_Template_{cat}', {'Id': tid}, 'ScriptPreset', name, old)
        if instances:
            for (g,) in self.m.g.execute(f'select Guid from "_Instance_{cat}" where Id=? and ScriptPreset=?', (tid, old)):
                self.guarded_update('game', f'_Instance_{cat}', {'Guid': g}, 'ScriptPreset', name, old)
        return name

    def _stable_name(self, old, on, can):
        key = (old or '-') + '|' + ';'.join(f'on:{e}:{s}' for e, s in sorted((on or {}).items())) + ';' + \
              ';'.join(f'can:{e}:{s}' for e, s in sorted((can or {}).items()))
        return f'{self.ns}_preset_{uuid.uuid5(uuid.NAMESPACE_URL, key).hex[:10]}.xml'

    # ================================================================ layer 3/4: state machines
    def _machine_rows(self, mid):
        s = self.m.s
        states = [dict(r) for r in s.execute('select * from _Script_StateMachineStates where MachineName=? order by rowid', (mid,))]
        trans = [dict(r) for r in s.execute('select * from _Script_StateTransitions where MachineName=? order by rowid', (mid,))]
        assert states, f'machine {mid} not found'
        return states, trans

    def _blocks_of(self, states, trans):
        sb, cb = set(), set()
        for st in states:
            for p in ('OnEntry', 'OnFrame', 'OnExit'):
                if st[f'{p}StatementBlock'] not in (None, Z): sb.add(st[f'{p}StatementBlock'])
        for t in trans:
            if t['ConditionBlock'] not in (None, Z): cb.add(t['ConditionBlock'])
            if t['StatementBlock'] not in (None, Z): sb.add(t['StatementBlock'])
        stmts = []
        for b in sb:
            stmts += [dict(r) for r in self.m.s.execute('select * from _Scripts_Statements where StatementBlockGUID=? order by rowid', (b,))]
        for st in stmts:   # If conditions live in their own blocks referenced from Condition statements
            if st['StatementType'] == 'Condition':
                refs = GUID_RE.findall(st['StatementContent'])
                if len(refs) > 1: cb.add(uuid.UUID(refs[1]).bytes_le)
        conds = []
        for b in cb:
            conds += [dict(r) for r in self.m.s.execute('select * from _Scripts_Conditions where ConditionBlockGUID=? order by rowid', (b,))]
        return stmts, conds

    def clone_machine(self, src, new_id, replace=None):
        """Copy a vanilla machine under a new Id (every statement/condition/block gets a new deterministic GUID).
        replace: {old text: new text} applied to every statement/condition content (e.g. SelectTarget weights).
        Returns a Machine to add states/transitions before emit()."""
        states, trans = self._machine_rows(src)
        stmts, conds = self._blocks_of(states, trans)
        mp = {}
        def nb(b):
            if b in (None, Z): return Z
            if b not in mp: mp[b] = U(self.ns, 'fsm', new_id, uuid.UUID(bytes_le=b).hex).bytes_le
            return mp[b]
        for st in stmts: nb(st['StatementGUID']); nb(st['StatementBlockGUID'])
        for c in conds: nb(c['ConditionGUID']); nb(c['ConditionBlockGUID'])
        def retext(t):
            t = GUID_RE.sub(lambda mm: str(uuid.UUID(bytes_le=mp.get(uuid.UUID(mm.group(0)).bytes_le, uuid.UUID(mm.group(0)).bytes_le))), t or '')
            for a, b in (replace or {}).items(): t = t.replace(a, b)
            return t
        mach = Machine(self, new_id, self.m.s.execute('select StartState from _Script_StateMachines where Id=?', (src,)).fetchone()[0])
        for st in stmts:
            mach.raw_stmts.append(dict(StatementGUID=nb(st['StatementGUID']), StatementType=st['StatementType'],
                                       StatementContent=retext(st['StatementContent']), StatementBlockGUID=nb(st['StatementBlockGUID'])))
        for c in conds:
            mach.raw_conds.append(dict(ConditionGUID=nb(c['ConditionGUID']), ConditionType=c['ConditionType'],
                                       ConditionContent=retext(c['ConditionContent']), ConditionBlockGUID=nb(c['ConditionBlockGUID'])))
        for st in states:
            mach.states[st['StateName']] = {p: (nb(st[f'{p}StatementRef']), nb(st[f'{p}StatementBlock'])) for p in ('OnEntry', 'OnFrame', 'OnExit')}
        for t in trans:
            mach.trans.setdefault(t['StateName'], []).append(dict(to=t['ToState'], cref=nb(t['ConditionRef']), cblk=nb(t['ConditionBlock']),
                                                                   sref=nb(t['StatementRef']), sblk=nb(t['StatementBlock'])))
        return mach

    def tune_machine(self, mid, replace):
        """Layer 4: edit text inside a VANILLA machine's statements/conditions (e.g. target weights) for every NPC using it.
        Each changed row is a guarded UPDATE with exact undo."""
        states, trans = self._machine_rows(mid)
        stmts, conds = self._blocks_of(states, trans)
        n = 0
        for tbl, key, col, rows in (('_Scripts_Statements', 'StatementGUID', 'StatementContent', stmts),
                                    ('_Scripts_Conditions', 'ConditionGUID', 'ConditionContent', conds)):
            for r in rows:
                new = r[col]
                for a, b in replace.items(): new = new.replace(a, b)
                if new != r[col]:
                    self.guarded_update('static', tbl, {key: r[key]}, col, new, r[col]); n += 1
        assert n, f'tune_machine({mid}): nothing matched'
        return n

    # ================================================================ layer 5: scripted attacks
    def script_attack(self, aid, name, script, desc='', base='ScriptCombatAction', **over):
        """New attack row of class Game::ScriptCombatAction that runs `script` when chosen by CombatActionGenerator."""
        t = self.clone_template('Attacks', base, aid, Name=f'{aid}_name', CombatScriptName=script, Description=f'{aid}_desc', **over)
        self.m.text(f'{aid}_name', name); self.m.text(f'{aid}_desc', desc or name)
        return t

    def add_attack_chance(self, cat, tid, aid, weight, column='SpecialAttackChances', instances=True):
        """Append 'aid weight 0' to a being's move list (the entity column overrides the machine's list; vanilla ogres work so).
        Done at install time on whatever the list holds then (6 Nov: a value-guarded update skipped the Ogre Chief, whose moves the
        pack had already changed); never twice; undo cuts exactly that piece out again."""
        piece = f'{aid} {weight} 0'
        assert self.m.s.execute(f'select 1 from "_Template_{cat}" where Id=?', (tid,)).fetchone(), (cat, tid)
        placed = instances and self.m.g.execute(f'select 1 from "_Instance_{cat}" where Id=?', (tid,)).fetchone()
        for db, tbl, key in (('static', f'_Template_{cat}', 'Id'),) + ((('game', f'_Instance_{cat}', 'Id'),) if placed else ()):
            c = f'"{column}"'
            do = (f"UPDATE \"{tbl}\" SET {c}=CASE WHEN trim(coalesce({c},''))='' THEN 'MeleeAttack 1.0 0, {piece}' "
                  f"ELSE rtrim(trim({c}),',') || ', {piece}' END WHERE \"{key}\"={lit(tid)} AND coalesce({c},'') NOT LIKE '%{aid} %';")
            undo = (f"UPDATE \"{tbl}\" SET {c}=replace(replace({c}, ', {piece}', ''), '{piece}', '') "
                    f"WHERE \"{key}\"={lit(tid)} AND {c} LIKE '%{piece}%';")
            (self.m.static if db == 'static' else self.m.game).append(do)
            (self.m.undo_static if db == 'static' else self.m.undo_game).append(undo)
            (self.checks_static if db == 'static' else self.checks_game).append(
                (f'{tbl}.{column} of {tid} has {aid}', f"SELECT count(*)>0 FROM \"{tbl}\" WHERE \"{key}\"={lit(tid)} AND {c} LIKE '%{piece}%'", 1))

    def set_behaviour(self, cat, tid, machine, instances=True):
        old = self.m.s.execute(f'select Behaviour from "_Template_{cat}" where Id=?', (tid,)).fetchone()[0]
        self.guarded_update('static', f'_Template_{cat}', {'Id': tid}, 'Behaviour', machine, old)
        if instances:
            for (g,) in self.m.g.execute(f'select Guid from "_Instance_{cat}" where Id=? and Behaviour=?', (tid, old)):
                self.guarded_update('game', f'_Instance_{cat}', {'Guid': g}, 'Behaviour', machine, old)

    # ================================================================ layer 6: level-enter scripts
    def on_level_enter(self, level, script):
        """Append `script` to the level's comma-separated LevelEnterScript (instance row = world/save; template for consistency)."""
        for db, tbl in (('game', '_Instance_Levels'), ('static', '_Template_Levels')):
            con = self.m.g if db == 'game' else self.m.s
            r = con.execute(f'select LevelEnterScript from {tbl} where Id=?', (level,)).fetchone()
            assert r is not None, (tbl, level)
            old = r[0] or ''
            new = f'{old},{script}' if old else script
            self.guarded_update(db, tbl, {'Id': level}, 'LevelEnterScript', new, old)

    # ================================================================ layer 7: triggers
    def trigger(self, name, level, anchor, offset=(0, 0, 0), radius=4.0, shape='sphere', filter='IsBeing;IsPartyMember;',
                enter='', inside='', leave='', once=True, one_way=True, active=1):
        """New trigger volume. enter/inside/leave: action strings (';'-separated, e.g. 'OnScript scriptNames="x.xml";')."""
        p = self.anchor_pos(level, anchor); p = (p[0] + offset[0], p[1] + offset[1], p[2] + offset[2])
        tid = 'DefaultTriggerSphere' if shape == 'sphere' else 'DefaultTriggerBox'
        sc = (radius, radius, radius) if not isinstance(radius, tuple) else radius
        return self.place_row('Trigger', 'Id=?', (tid,), dict(_ID=f'|Level|Objects|Trigger|{name}', _Level=level, _Layers='', Name=name,
                              Transform=xform(p, sc), EntityFilter=filter, EnterActions=enter, LeaveActions=leave, InsideActions=inside,
                              TriggerOnce=int(once), OneWayTrigger=int(one_way), TriggerActive=active), name)

    # ================================================================ layer 8: zones
    def marker(self, name, level, anchor, offset=(0, 0, 0)):
        p = self.anchor_pos(level, anchor); p = (p[0] + offset[0], p[1] + offset[1], p[2] + offset[2])
        return self.place_row('MarkerPoint', "Id='MarkerPoint'", (), dict(_ID=f'|Level|Objects|MarkerPoint|{name}', _Level=level, _Layers='',
                              Name=name, Transform=xform(p)), name)

    @staticmethod
    def inside(who, edges):
        """Atom: is `who` inside the polygon spanned by MarkerPoint names `edges` (vanilla numbers them edge1..N)."""
        return C('IsInside', who=who, **{f'edge{i + 1}': e for i, e in enumerate(edges)})

    @staticmethod
    def all_inside(script, edges, segment=0):
        """Action: run `script` on every being inside the polygon (vanilla numbers them edge0..N here)."""
        return A('RunScriptOnAllInside', script=script, segment=segment, **{f'edge{i}': e for i, e in enumerate(edges)})

    # ================================================================ layer 9: heartbeats / watchers
    def heartbeat(self, sid, name, desc, every, body, times=30, start='', state_effect='', hardpoint='', texture='status_fx_good_jewel',
                  categories='buff;good'):
        """Status effect that runs `body` every `every` seconds, `times` times (unrolled like vanilla scroll ticks).
        If-blocks inside get Else branches automatically (status-effect blocks assert without Else)."""
        ticks = []
        for _ in range(times):
            ticks += [x if isinstance(x, str) else x for x in body] + [f'WaitAction duration="{every}" permanent="false" actionSelection="script"']
        self._status_with_items(sid, name, desc, start, ticks, state_effect, hardpoint, texture, categories)
        return sid

    def _status_with_items(self, sid, name, desc, start, trigger_items, state_effect, hardpoint, texture, categories, stackable=0):
        m = self.m
        assert re.fullmatch(r'[A-Za-z0-9]+', sid), sid
        st = Script(f'{self.ns}/se/{sid}/start').begin([f'ModifyAttribute modifier="{start}" actionSelection="script"'] if start else [])
        tr = Script(f'{self.ns}/se/{sid}/trigger').begin(no_if_without_else(trigger_items))
        m.static.append(f'-- status effect {sid}')
        if start: self._emit(st)
        self._emit(tr)
        sg = U(self.ns, 'se', sid)
        m.static.append(insert('_Scripts_StatusEffectScripts', dict(Guid=sg, Id=sid, Name='',
            StatusEffectOnStartRef=st.ref if start else Z, StatusEffectOnStartBlock=st.guid if start else Z,
            StatusEffectOnTriggerRef=tr.ref, StatusEffectOnStopRef=Z, StatusEffectOnTriggerBlock=tr.guid, StatusEffectOnStopBlock=Z,
            StatusEffectCategories='', StatusEffectTexture='', StatusEffectStackable=stackable, StatusEffectPower=1)))
        m.static.append(insert('_Template_Statuseffects', dict(Id=sid, State_Effect=state_effect, State_Hardpoint=hardpoint, State_Sound='',
            State_Texture=f'textures:icons/{texture}.dds', State_Categories=categories, Name=f'{sid}_name', ShortDescription=f'{sid}_short',
            LongDescription=f'{sid}_long', State_Immunity='')))
        m.undo_static += [f"DELETE FROM _Scripts_StatusEffectScripts WHERE Guid={lit(sg)};", f"DELETE FROM _Template_Statuseffects WHERE Id={lit(sid)};"]
        m.text(f'{sid}_name', name); m.text(f'{sid}_short', name); m.text(f'{sid}_long', desc)
        m.se_names[sid] = name
        m.new_guids.append(sg)
        self.checks_static.append((f'status {sid}', f"SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id={lit(sid)}", 1))

    def timed_status(self, sid, name, desc, mods, seconds, state_effect='', hardpoint='', texture='status_fx_good_jewel', categories='buff;good'):
        """Plain timed buff/debuff: ModifyAttribute on start, reverted when the trigger wait ends (vanilla potion shape)."""
        self._status_with_items(sid, name, desc, mods, [f'WaitAction duration="{seconds}" permanent="false" actionSelection="script"'],
                                state_effect, hardpoint, texture, categories)
        return sid

    @staticmethod
    def watcher(condition_script, then, seconds=1):
        """Action list: wait (polling every `seconds`) until a condition script holds, then run `then`."""
        return [A('WaitForCondition', _sel='actionSelection="script"', condition=condition_script, duration=seconds, permanent='true')] + list(then)

    @staticmethod
    def for_party(make):
        """Action items applying make(who) to the hero and to every companion currently in the party."""
        out = [make('Hero')]
        for n in PARTY:
            out.append(('if', C('IsPartyMember', who=n), [make(n)]))
        return out

    # ================================================================ layer 10: interactive objects
    def object(self, oid, display, desc, level, anchor, offset=(0, 0, 0), base='dun04_altarschale', graphics=None, physics=None,
               on_use=None, can_use=None, picking=3.0):
        """Usable static object (Object category: graphics + physics + Useable + ScriptProperty), e.g. a shrine."""
        over = dict(Name=oid, LookAtText=f'lookat_{oid}', CanUse=1, PickingRange=picking,
                    ScriptOverride=self.override(on={'Use': on_use} if on_use else None, can={'Use': can_use} if can_use else None))
        if graphics: over.update(Graphics=graphics, Physics=physics or graphics, Placeholder='')
        t = self.clone_template('Object', base, oid, **over)
        self.m.text(f'lookat_{oid}', display)
        p = self.anchor_pos(level, anchor); p = (p[0] + offset[0], p[1] + offset[1], p[2] + offset[2])
        inst = {k: v for k, v in t.items() if k != 'Id'}
        inst.update(Id=oid, _ID=f'|Level|Objects|Object|{oid}', _Level=level, _Layers='', Transform=xform(p))
        icols = {c[1] for c in self.m.g.execute('pragma table_info(_Instance_Object)')}
        return self.place_row('Object', 'Id=?', (base,), {k: v for k, v in inst.items() if k in icols}, oid)

    def state_object(self, oid, display, level, anchor, base, state=None, offset=(0, 0, 0), on_use=None, can_use=None):
        """Usable state object cloned from a vanilla template (its .n2 defines the state names; `state` = initial one)."""
        over = dict(Name=oid, LookAtText=f'lookat_{oid}', CanUse=1,
                    ScriptOverride=self.override(on={'Use': on_use} if on_use else None, can={'Use': can_use} if can_use else None))
        if state: over['State'] = state
        t = self.clone_template('StateObject', base, oid, **over)
        self.m.text(f'lookat_{oid}', display)
        p = self.anchor_pos(level, anchor); p = (p[0] + offset[0], p[1] + offset[1], p[2] + offset[2])
        icols = {c[1] for c in self.m.g.execute('pragma table_info(_Instance_StateObject)')}
        inst = {k: v for k, v in t.items() if k in icols}
        inst.update(_ID=f'|Level|Objects|StateObject|{oid}', _Level=level, _Layers='', Transform=xform(p))
        donor = self.m.g.execute('select 1 from _Instance_StateObject where Id=?', (base,)).fetchone()
        return self.place_row('StateObject', 'Id=?' if donor else '1=1', (base,) if donor else (), inst, oid)

    # ================================================================ layer 11: service points
    def clone_instance(self, cat, src_name, src_level, new_name, level, pos=None, offset=(0, 0, 0), **over):
        """Copy a placed vanilla instance (WorkBench, Herb, DestroyableEntity, Blockade, ...) to a new spot/level."""
        r = self.m.g.execute(f'select Transform from "_Instance_{cat}" where Name=? and _Level=?', (src_name, src_level)).fetchone()
        assert r, (cat, src_name, src_level)
        mat = list(struct.unpack('<16f', r[0]))
        if pos: mat[12:15] = pos
        mat[12] += offset[0]; mat[13] += offset[1]; mat[14] += offset[2]
        o = dict(_ID=f'|Level|Objects|{cat}|{new_name}', _Level=level, Name=new_name, Transform=struct.pack('<16f', *mat))
        o.update(over)
        return self.place_row(cat, 'Name=? and _Level=?', (src_name, src_level), o, new_name)

    def entry(self, name, level, transform):
        """Object entry point (spawn target for CreateEntity how="spawnAtEntity", TransferEntity entryPoint=)."""
        return self.place_row('Entry', "Id='EntryPortalObject'", (), dict(_ID=f'|Level|Objects|Entry|{name}', _Level=level, Name=name,
                              Transform=transform), name)

    def herb_patch(self, pid, level, src_guid, offset=(1.2, 0, 0.6)):
        """A regrowable herb: unique template (clone of the source herb's template), first plant placed next to a vanilla herb,
        an entry point at its spot; regrow() gives the actions that destroy and respawn it (vanilla player-house pattern)."""
        src = dict(self.m.g.execute('select * from _Instance_Herb where Guid=?', (src_guid,)).fetchone())
        t = self.clone_template('Herb', src['Id'], pid, Name=pid)
        mat = list(struct.unpack('<16f', src['Transform'])); mat[12] += offset[0]; mat[13] += offset[1]; mat[14] += offset[2]
        tr = struct.pack('<16f', *mat)
        self.entry(f'{pid}_spot', level, tr)
        icols = {c[1] for c in self.m.g.execute('pragma table_info(_Instance_Herb)')}
        inst = {k: v for k, v in t.items() if k in icols}
        inst.update(_ID=f'|Level|Objects|Herb|{pid}', _Level=level, _Layers=src['_Layers'], Transform=tr)
        self.place_row('Herb', 'Guid=?', (src_guid,), inst, pid)
        return [A('DestroyEntity', item=pid, notInStorage='true', destroyDirectly='false'),
                A('CreateEntity', category='Herb', templateId=pid, how='spawnAtEntity', entity=f'{pid}_spot')]

    # ================================================================ layer 12: encounters
    def encounter(self, name, level, copy_from, script_items, reactivate_after=900.0, count=5, active=1, filter='IsBeing;IsPartyLeader;'):
        """Respawning encounter on the ground of a vanilla one: copies its trigger box and spawn points (valid positions),
        with our own spawn script. script_items: action items using spawn(index, category, templateId)."""
        g = self.m.g
        trig = g.execute('select * from _Instance_EncounterTrigger where Name=? and _Level=?', (copy_from, level)).fetchone()
        assert trig, (copy_from, level)
        sname = f'{name}.xml'
        self.action_script(sname, script_items)
        self.place_row('EncounterTrigger', 'Name=? and _Level=?', (copy_from, level), dict(
            _ID=f'|Level|Encounter|{name}|{name}_Trigger__id1', Name=name, InsideActions=f'OnScript scriptNames="{sname}";', EnterActions='',
            LeaveActions='', EntityFilter=filter, TriggerActive=active, ReactivateTrigger=1, ReactivateTriggerTime=reactivate_after,
            ReactivateCount=count, AssignAutoGroup=1, Groups=''), name)
        pts = g.execute('select rowid, SpawnPointIndex from _Instance_SpawnPoint where EncounterName=? and _Level=? order by SpawnPointIndex', (copy_from, level)).fetchall()
        assert pts, copy_from
        for rid, idx in pts:
            self.place_row('SpawnPoint', 'rowid=?', (rid,), dict(_ID=f'|Level|Encounter|{name}|{name}_SpawnPoint{idx}__id1', EncounterName=name), f'{name}/sp{idx}')
        return len(pts)

    @staticmethod
    def spawn(index, category, template, initial_script=None):
        kw = dict(spawnPointIndex=index, category=category, templateId=template)
        if initial_script: kw['initialScript'] = initial_script
        return A('SpawnAtEncounter', _sel='actionSelection="script"', **kw)

    # ================================================================ layer 13: probes
    def probe_item(self, iid, display, desc, script, base='heiltrank_klein', owner=('pc', 'pc_rhulana', None)):
        """Usable, reusable test item that runs `script` (CanDestroy 0: not consumed). Placed in Rhulana's start pack."""
        self.m.template('Item', base, iid, display, desc, ScriptOverride=f'on:Use:{script}', ScriptPreset='', CanDestroy=0, Value=0)
        self.m.place('Item', iid, owner[0], owner[1], owner[2])
        return iid

    # ================================================================ layer 15: factions
    def add_column(self, db, table, col, sqltype='INTEGER', default=None, attr_type=None, rw=1):
        """Add a column (= a new dynamic attribute) to a table, plus the _Attributes row in both databases (once per name).
        Undo rebuilds the table without it (SQLite 3.6.1 has no DROP COLUMN): same CREATE statement, same indexes, same rows."""
        m = self.m
        con = m.s if db == 'static' else m.g
        store, undo = (m.static, m.undo_static) if db == 'static' else (m.game, m.undo_game)
        cols = [c[1] for c in con.execute(f'pragma table_info("{table}")')]
        assert col not in cols, (table, col)
        create = con.execute("select sql from sqlite_master where name=?", (table,)).fetchone()[0]
        idx = [r[0] for r in con.execute("select sql from sqlite_master where tbl_name=? and type='index' and sql is not null", (table,))]
        tmp = f'{table}_lay_tmp'
        colsql = ','.join(f'"{c}"' for c in cols)
        assert f"'{table}'" in create, create[:80]
        rebuild = '\n'.join([f'DROP TABLE IF EXISTS {tmp};', create.replace(f"'{table}'", tmp, 1) + ';',
                              f'INSERT INTO {tmp} ({colsql}) SELECT {colsql} FROM "{table}";',
                              f'DROP TABLE "{table}";', f'ALTER TABLE {tmp} RENAME TO "{table}";'] + [i + ';' for i in idx])
        # install = rebuild to the original columns (drops the column if a previous install added it) + ADD COLUMN: idempotent
        # under sqlite3.exe -bail (3.6.1 has neither ADD COLUMN IF NOT EXISTS nor DROP COLUMN). Values of the column restart
        # from the default on every install, so set them after this call. Assumes no other mod changed this table's columns.
        if not hasattr(self, '_rebuilt'): self._rebuilt = set()
        if (db, table) not in self._rebuilt:   # several new columns on one table: one rebuild, then all ADD COLUMNs
            self._rebuilt.add((db, table))
            store.append(rebuild)
            undo.append(rebuild)   # one entry: static undo is reversed
        store.append(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {sqltype}' + (f' DEFAULT {lit(default)}' if default is not None else '') + ';')
        if not hasattr(self, '_attrs_added'): self._attrs_added = set()
        if col not in self._attrs_added:
            self._attrs_added.add(col)
            at = attr_type or {'INTEGER': 'int', 'TEXT': 'string', 'REAL': 'float'}[sqltype]
            for st, un in ((m.static, m.undo_static), (m.game, m.undo_game)):
                st += [f'DELETE FROM _Attributes WHERE AttrName={lit(col)};', insert('_Attributes', dict(AttrName=col, AttrType=at, AttrReadWrite=rw, AttrDynamic=1))]
                un.append(f'DELETE FROM _Attributes WHERE AttrName={lit(col)};')
        self.checks_static.append((f'attribute {col}', f"SELECT count(*) FROM _Attributes WHERE AttrName={lit(col)}", 1))

    # ================================================================ layer 15: factions
    def faction(self, fid, display, stances, default='Neutral'):
        """New faction: a column on _Template_Faction (every faction's stance towards it), its own row, _Attributes rows.
        stances: {other faction: 'Friendly'|'Neutral'|'Hostile'}, used both ways; others get `default`."""
        m = self.m
        assert re.fullmatch(r'Fa[A-Za-z0-9]+', fid), fid
        cols = [c[1] for c in m.s.execute('pragma table_info(_Template_Faction)')]
        others = [r[0] for r in m.s.execute('select Id from _Template_Faction')]
        m.static.append(f'-- faction {fid}')
        m.undo_static.append(f'DELETE FROM _Template_Faction WHERE Id={lit(fid)};')   # runs after the rebuild (undo is reversed)
        self.add_column('static', '_Template_Faction', fid, 'TEXT', attr_type='string', rw=0)
        for o in others:
            m.static.append(f'UPDATE _Template_Faction SET "{fid}"={lit(stances.get(o, default))} WHERE Id={lit(o)};')
        row = {c: '' for c in cols}
        row.update(Id=fid, Name=display, LocaleFaction=0, **{o: stances.get(o, default) for o in cols if o.startswith('Fa')})
        row[fid] = 'Friendly'
        m.static.append(insert('_Template_Faction', row))
        self.checks_static.append((f'faction {fid}', f"SELECT count(*) FROM _Template_Faction WHERE Id={lit(fid)}", 1))
        return fid

    def special_ability(self, sf, tables=(('static', '_Template_PC'), ('static', '_Template_PC_CharWizard'), ('game', '_Instance_PC'),
                                          ('game', '_Instance_PC_CharWizard'))):
        """New SF_* ability attribute on the hero tables (-500 = not known, 1 = known, like vanilla)."""
        for db, tb in tables:
            self.add_column(db, tb, sf, 'INTEGER', default=-500)
        return sf

    # ================================================================ layer 16: area hazards
    def area_hazard(self, hid, inside_script, base='DefaultOdemBubble', enter_script=None, graphics=None):
        """AreaSpellTrigger template that runs scripts on beings inside; spawn with the returned CreateEntity action."""
        over = dict(Name=hid, InsideActions=f'OnScript scriptNames="{inside_script}";', TriggerActive=1)
        if enter_script: over['EnterActions'] = f'OnScript scriptNames="{enter_script}";'
        if graphics: over['Graphics'] = graphics
        self.clone_template('AreaSpellTrigger', base, hid, **over)
        return lambda entity: A('CreateEntity', category='AreaSpellTrigger', templateId=hid, how='spawnAtEntity', entity=entity)

    # ================================================================ layer 18: new categories
    def category(self, name, like, blueprint_props=None):
        """New entity category with its own template/instance tables (schema copied from `like`) and _Categories row.
        Needs a blueprint entry of the same name (tools/loosefiles.py blueprint patch); without it the engine
        aborts on the first instance ("category not found in blueprints.xml"), so ship it with no instances until tested."""
        m = self.m
        c = m.s.execute('select * from _Categories where CategoryName=?', (like,)).fetchone()
        assert c and not m.s.execute('select 1 from _Categories where CategoryName=?', (name,)).fetchone()
        for db, con, store, undo, kind in (('static', m.s, m.static, m.undo_static, 'Template'), ('game', m.g, m.game, m.undo_game, 'Instance')):
            src = f'_{kind}_{like}'
            sql = con.execute("select sql from sqlite_master where name=?", (src,)).fetchone()
            if not sql: continue
            new = f'_{kind}_{name}'
            store.append(f'DROP TABLE IF EXISTS "{new}";')
            store.append(sql[0].replace(f"'{src}'", f"'{new}'", 1).replace(src, new, 1) + ';')
            for (isql,) in con.execute("select sql from sqlite_master where tbl_name=? and type='index' and sql is not null", (src,)):
                store.append(isql.replace(src, new) + ';')
            undo.append(f'DROP TABLE IF EXISTS "{new}";')
        row = dict(c); row.update(CategoryName=name, CategoryTemplateTable=f'_Template_{name}' if c['CategoryTemplateTable'] else '',
                                  CategoryInstanceTable=f'_Instance_{name}' if c['CategoryInstanceTable'] else '')
        m.static.append(insert('_Categories', row))
        m.undo_static.append(f'DELETE FROM _Categories WHERE CategoryName={lit(name)};')
        self.checks_static.append((f'category {name}', f"SELECT count(*) FROM _Categories WHERE CategoryName={lit(name)}", 1))
        return name

    # ================================================================ verify
    def write_checks(self, out):
        """Append our checks to the Mod's verify files ('(expect N): M' lines read by tools/maint/validate.py)."""
        import os
        for name, checks in (('verify_static.sql', self.checks_static), ('verify_game.sql', self.checks_game)):
            p = os.path.join(out, 'sql', name)
            lines = [f"SELECT {lit(label + ' (expect ' + str(exp) + '): ')} || ({q});" for label, q, exp in checks]
            with open(p, 'a', encoding='cp1252', newline='\r\n') as f:
                f.write('\n'.join(lines) + '\n')


class Machine:
    """A state machine under construction (from Layers.clone_machine or Layers.machine)."""
    def __init__(self, L, mid, start):
        self.L, self.id, self.start = L, mid, start
        self.raw_stmts, self.raw_conds = [], []
        self.states, self.trans = {}, {}
        self.scripts = []

    def _script(self, items, tag):
        scr = Script(f'{self.L.ns}/fsm/{self.id}/{tag}').begin(items)
        self.scripts.append(scr)
        return scr.ref.bytes_le, scr.guid.bytes_le

    def state(self, name, entry=None, frame=None, exit=None):
        """Add or replace a state's blocks (None keeps the existing block, [] clears it)."""
        cur = self.states.get(name, {p: (Z, Z) for p in ('OnEntry', 'OnFrame', 'OnExit')})
        for p, items in (('OnEntry', entry), ('OnFrame', frame), ('OnExit', exit)):
            if items is not None:
                cur[p] = self._script(items, f'{name}/{p}') if items else (Z, Z)
        self.states[name] = cur
        self.trans.setdefault(name, [])
        return self

    def transition(self, frm, to, cond, actions=None, index=None):
        """Add a transition (first match wins; index 0 = checked first)."""
        scr = Script(f'{self.L.ns}/fsm/{self.id}/t/{frm}/{to}/{len(self.trans.get(frm, []))}')
        cref, cblk = scr.condition(cond)
        t = dict(to=to, cref=cref.bytes_le, cblk=cblk.bytes_le, sref=Z, sblk=Z)
        if actions:
            scr.begin(actions); t['sref'], t['sblk'] = scr.ref.bytes_le, scr.guid.bytes_le
        self.scripts.append(scr)
        lst = self.trans.setdefault(frm, [])
        lst.insert(len(lst) if index is None else index, t)
        return self

    def remove_transitions(self, frm, to):
        self.trans[frm] = [t for t in self.trans.get(frm, []) if t['to'] != to]
        return self

    def emit(self):
        m, L = self.L.m, self.L
        m.static.append(f'-- state machine {self.id}')
        for r in self.raw_stmts: m.static.append(insert('_Scripts_Statements', r))
        for r in self.raw_conds: m.static.append(insert('_Scripts_Conditions', r))
        blocks = {r['StatementBlockGUID'] for r in self.raw_stmts}
        cblocks = {r['ConditionBlockGUID'] for r in self.raw_conds}
        for b in sorted(blocks): m.undo_static.append(f"DELETE FROM _Scripts_Statements WHERE StatementBlockGUID={lit(b)};")
        for b in sorted(cblocks): m.undo_static.append(f"DELETE FROM _Scripts_Conditions WHERE ConditionBlockGUID={lit(b)};")
        m.new_guids += [uuid.UUID(bytes_le=r['StatementGUID']) for r in self.raw_stmts] + [uuid.UUID(bytes_le=r['ConditionGUID']) for r in self.raw_conds]
        for scr in self.scripts: L._emit(scr)
        m.static += [f"DELETE FROM _Script_StateMachines WHERE Id={lit(self.id)};", insert('_Script_StateMachines', dict(Id=self.id, StartState=self.start))]
        m.undo_static.append(f"DELETE FROM _Script_StateMachines WHERE Id={lit(self.id)};")
        assert self.start in self.states
        for name, parts in self.states.items():
            row = dict(Id=f'{self.id}_{name}', StateName=name, MachineName=self.id)
            for p in ('OnEntry', 'OnFrame', 'OnExit'):
                row[f'{p}StatementRef'], row[f'{p}StatementBlock'] = parts[p]
            m.static.append(insert('_Script_StateMachineStates', row))
            for i, t in enumerate(self.trans.get(name, [])):
                assert t['to'] in self.states, (self.id, name, t['to'])
                m.static.append(insert('_Script_StateTransitions', dict(Id=f'{self.id}_{name}_{t["to"]}_{i}', StateName=name, MachineName=self.id,
                    ToState=t['to'], ConditionRef=t['cref'], ConditionBlock=t['cblk'], StatementRef=t['sref'], StatementBlock=t['sblk'], TransitionIndex=i)))
        m.undo_static += [f"DELETE FROM _Script_StateMachineStates WHERE MachineName={lit(self.id)};",
                          f"DELETE FROM _Script_StateTransitions WHERE MachineName={lit(self.id)};"]
        n = sum(len(v) for v in self.trans.values())
        L.checks_static += [(f'machine {self.id} states', f"SELECT count(*) FROM _Script_StateMachineStates WHERE MachineName={lit(self.id)}", len(self.states)),
                            (f'machine {self.id} transitions', f"SELECT count(*) FROM _Script_StateTransitions WHERE MachineName={lit(self.id)}", n)]
        return self.id


def write_sync_bat(out, title):
    """SyncSave.bat: applies the module's game.sql to the NEWEST save (a save is a copy of game.db4; game.sql is idempotent and
    every vanilla edit in it is guarded), so placed content reaches a running game. Keeps <save>.before_<module>; ends with the
    bundled sqlite3 VACUUM (saves rewritten by modern SQLite once failed to load, ENGINE_REFERENCE §12)."""
    import os
    name = os.path.basename(os.path.normpath(out))
    text = rf'''@echo off
:: {title}: put this module's world content into your NEWEST save (any name). Save in game, quit, run this, load that save.
:: A backup of the save is kept next to it (.before_{name}). Run Install.bat first.
setlocal
set "SQ=%~dp0sqlite3.exe"
set "SYS=%SystemRoot%\System32"
"%SYS%\tasklist.exe" /FI "IMAGENAME eq drakensang.exe" 2>nul | "%SYS%\find.exe" /I "drakensang.exe" >nul && ( echo Close Drakensang first. Nothing was changed. & goto end )
set "DSA="
for /f "delims=" %%f in ('powershell -NoProfile -Command "(Get-ChildItem -LiteralPath $env:USERPROFILE\Documents\Drakensang\profiles\default\save -Recurse -Filter *.dsa | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName"') do set "DSA=%%f"
if not defined DSA ( echo No save found. & goto end )
echo Save: %DSA%
copy /Y "%DSA%" "%DSA%.before_{name}" >nul || ( echo Backup failed. Nothing was changed. & goto end )
"%SQ%" -bail "%DSA%" < "%~dp0sql\game.sql" || ( echo ERROR. Your backup: %DSA%.before_{name} & goto end )
"%SQ%" "%DSA%" < "%~dp0sql\verify_game.sql"
"%SQ%" -bail "%DSA%" "VACUUM;"
echo Done. Load this save. Backup kept as %DSA%.before_{name}
:end
if /i not "%~1"=="nopause" pause
'''
    with open(os.path.join(out, 'SyncSave.bat'), 'w', encoding='ascii', newline='\r\n') as f:
        f.write(text)
