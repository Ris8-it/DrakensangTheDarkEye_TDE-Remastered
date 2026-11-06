"""Shared generator library for Drakensang SQL mods (see docs/ENGINE_REFERENCE.md §4).

A Mod collects idempotent install SQL + exact undo SQL for static/locale/game.db4, reading vanilla rows
as templates. Scripts are written in the exact vanilla row shape (Block). Nothing here writes to the game.
"""
import sqlite3, os, uuid, io, re

ACT = 'actionSelection="script,quest,dialog"; '
# Status ids the engine can create from an item script (proven in-game or used by vanilla items).
# NOT creatable (crash): somnigravis, horriphobus (and other spell-only states).
NATIVE_OK = {'wound', 'burning', 'poison_weapon', 'overthrown', 'corpofrigo', 'stun', 'blitzDichFind'}
NATIVE_NAMES = {'wound': 'Wound', 'burning': 'Burning', 'poison_weapon': 'Poison', 'overthrown': 'Knockdown',
                'corpofrigo': 'Cold Shock (Corpofrigo)', 'stun': 'Stun', 'blitzDichFind': 'Blinding Flash'}
ATTR = {'MU': 'Courage', 'KL': 'Cleverness', 'IN': 'Intuition', 'CH': 'Charisma', 'FF': 'Dexterity', 'GE': 'Agility',
        'KO': 'Constitution', 'KK': 'Strength', 'AT': 'Attack', 'PA': 'Parry', 'FK': 'Ranged combat', 'AW': 'Dodge',
        'MR': 'Magic resistance', 'LEmax': 'LE', 'AEmax': 'AE', 'AUmax': 'AU', 'ATW6': 'Damage',
        'Reg_LE': 'LE regeneration', 'Reg_AE': 'AE regeneration', 'Reg_AU': 'AU regeneration', 'Reg_LE_freq': 'LE regeneration speed', 'Reg_AE_freq': 'AE regeneration speed', 'Reg_AU_freq': 'AU regeneration speed',
        'TaSaebel': 'Sabers', 'TaHiebwaffen': 'Axes & maces', 'TaZwHiebwaffen': 'Two-handed impact weapons', 'TaBogen': 'Bows',
        'TaArmbrust': 'Crossbows', 'TaStaebe': 'Staves', 'TaDolche': 'Daggers', 'TaFechtwaffen': 'Fencing weapons',
        'TaSchwerter': 'Swords', 'TaZwSchwerter': 'Two-handed swords', 'TaSpeere': 'Spears', 'TaWurfwaffen': 'Throwing weapons',
        'TaSchleichen': 'Sneak', 'TaTaschendiebstahl': 'Pickpocket', 'TaSchloesser': 'Open locks', 'TaSinnenschaerfe': 'Perception',
        'TaHeilkundeWunden': 'Treat wounds', 'TaHeilkundeGift': 'Treat poison', 'TaSchmieden': 'Smithing', 'TaBogenbau': 'Bowcraft',
        'TaAlchimie': 'Alchemy', 'TaMagiekunde': 'Magic lore', 'TaWildnisleben': 'Wilderness lore', 'TaTierkunde': 'Animal lore',
        'TaPflanzenkunde': 'Plant lore', 'TaFallenEntschaerfen': 'Disarm traps', 'TaEtikette': 'Etiquette', 'TaUeberreden': 'Persuasion',
        'TaSelbstbeherrschung': 'Self-control', 'TaFeilschen': 'Haggle', 'TaMenschenkenntnis': 'Human nature',
        'ZaTatzeSchwinge': 'Helpful Paw', 'ZaArmatrutz': 'Armatrutz', 'ZaBlitz': 'Blitz', 'ZaFulminictus': 'Fulminictus',
        'ZaIgnifaxius': 'Ignifaxius', 'ZaBalsam': 'Balsam', 'ZaSkelettarius': 'Skelettarius', 'ZaElementarerDiener': 'Elemental Servant',
        'ZaAxxeleratus': 'Axxeleratus', 'ZaCorpofrigo': 'Corpofrigo', 'ZaHorriphobus': 'Horriphobus', 'ZaSomnigravis': 'Somnigravis',
        'ZaParalysis': 'Paralysis', 'ZaKulminatio': 'Kulminatio', 'ZaIgnisphaero': 'Ignisphaero', 'ZaGardianum': 'Gardianum',
        'ZaPsychostabilis': 'Psychostabilis', 'ZaAdlerauge': 'Eagle Eye', 'ZaFalkenaugeMeisterschuss': 'Falcon Eye',
        'ZaHerrUeberDasTierreich': 'Lord of Beasts', 'ZaEisenrost': 'Eisenrost', 'ZaPlumbumbarum': 'Plumbumbarum',
        'ZaSanftmut': 'Sanftmut', 'ZaKlarumPurum': 'Klarum Purum', 'ZaRuheKoerper': 'Rest of Body', 'ZaAttributoKK': 'Attributo (KK)'}
ATTR.update({'TaDolche': 'Daggers', 'TaFechtwaffen': 'Fencing Weapons', 'TaHiebwaffen': 'Axes and Maces', 'TaSaebel': 'Sabers', 'TaSchwerter': 'Swords', 'TaSpeere': 'Spears', 'TaStaebe': 'Staves', 'TaZwHiebwaffen': 'Two-handed Axes/Maces', 'TaZwSchwerter': 'Two-handed Swords', 'TaArmbrust': 'Crossbow', 'TaBogen': 'Bow', 'TaWurfwaffen': 'Throwing Weapons', 'TaSchleichen': 'Sneak', 'TaSelbstbeherrschung': 'Willpower', 'TaSinnenschaerfe': 'Perception', 'TaTaschendiebstahl': 'Pick Pocket', 'TaFallenstellen': 'Traps', 'TaWildnisleben': 'Survival', 'TaPflanzenkunde': 'Plant Lore', 'TaTierkunde': 'Animal Lore', 'TaMagiekunde': 'Arcane Lore', 'TaHeilkundeWunden': 'Treat Wounds', 'TaHeilkundeGift': 'Treat Poisons', 'TaGassenwissen': 'Streetwise', 'TaAlchimie': 'Alchemy', 'TaBogenbau': 'Bowyer', 'TaSchmieden': 'Blacksmith', 'TaSchloesser': 'Pick Locks', 'TaFallenEntschaerfen': 'Disarm Traps', 'TaBetoeren': 'Seduce', 'TaUeberreden': 'Fast Talk', 'TaFeilschen': 'Haggle', 'TaMenschenkenntnis': 'Human Nature', 'TaEtikette': 'Etiquette', 'TaEinschuechtern': 'Intimidate', 'TaRaufen': 'Brawling'})   # the game's own talent names (balance audit B13)
FOE = {'burning': 'burning', 'stun': 'stunned', 'overthrown': 'downed', 'corpofrigo': 'frozen', 'poison_weapon': 'poisoned', 'wound': 'wounded',
       'ArmDazed': 'dazed', 'ArmSundered': 'sundered', 'ArmBleeding': 'bleeding', 'ArmHexed': 'hexed', 'ArmShaken': 'shaken', 'blitzDichFind': 'blinded'}
FX_NAMES = {'fire': 'fire', 'magic': 'magic', 'physical': '', 'poison': 'poison'}
U = lambda *p: uuid.uuid5(uuid.NAMESPACE_URL, 'drakensang/' + '/'.join(p))
IDENT = bytes.fromhex(('0000803f' + '00' * 16) * 3 + '0000803f')

def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, uuid.UUID): v = v.bytes_le
    if isinstance(v, bytes): return "X'" + v.hex().upper() + "'"
    if isinstance(v, (int, float)): return repr(v)
    return "'" + str(v).replace("'", "''") + "'"
def insert(table, row, verb='INSERT'):
    return f"{verb} INTO {table} ({','.join(chr(34) + c + chr(34) for c in row)}) VALUES ({','.join(lit(v) for v in row.values())});"
def mods_text(m):
    """'TaSaebel +2 AT +1' -> 'Sabers +2, Attack +1' (negative freq shown as faster regeneration)."""
    out = []
    for a, sgn, n in re.findall(r'(\w+) ([+-])(\d+)', m):
        if a.endswith('_freq'): out.append(f"{'Faster' if sgn == '-' else 'Slower'} {ATTR[a].replace(' speed', '')} ({sgn}{n})")
        else: out.append(f"{ATTR.get(a, a)} {sgn}{n}")
    return ', '.join(out)

class Block:
    """One statement block in vanilla row order (children first). Refs are .NET GUID strings."""
    def __init__(self, key):
        self.key, self.n, self.st, self.co = key, 0, [], []
        self.guid = U(key, 'block'); self.ref = None
    def _g(self, tag): self.n += 1; return U(self.key, f'{tag}{self.n}')
    def stmt(self, typ, content):
        x = self._g('s'); self.st.append((x, typ, content, self.guid)); return x
    def action(self, text): return self.stmt('Action', text)
    def cond(self, atom, negate=False):
        blk = self._g('cb'); a = self._g('c'); self.co.append((a, 'Atom', atom, blk)); top = a
        if negate: n = self._g('c'); self.co.append((n, 'Not', str(a), blk)); top = n
        c = self._g('c'); self.co.append((c, 'Condition', str(top), blk))
        return self.stmt('Condition', f'{c};{blk}')
    def if_(self, atom, build_then, negate=False, build_else=None):
        """build_then/build_else: callables returning a list of child statement GUIDs (built after the Condition)."""
        c = self.cond(atom, negate)
        t = self.stmt('Then', ';'.join(map(str, build_then())))
        if build_else:
            e = self.stmt('Else', ';'.join(map(str, build_else())))
            return self.stmt('If', f'{c};{t};{e}')
        return self.stmt('If', f'{c};{t}')
    def begin(self, kids): self.ref = self.stmt('Begin', ';'.join(map(str, kids))); return self

# ---------------- effect DSL ----------------
# actions: ('st', id) target status | ('dmg', fixed, dice_n, type, fx) | ('heal', n) | ('asp', n) | ('buff', se_id) self status
#          ('vfx', effect, target) | ('hurtself', n)
# procs:   ('p', pct, [actions|procs]) chance  | ('if', status_id, [...]) target has status | ('race', race, [...])
def _action_text(a):
    k = a[0]
    if k == 'st':
        if a[1] == 'burning':  # mirror chargeble_burn: only if the target is not immune to fire
            return None
        return f'SetStatusEffect who="AimedEntity" id="{a[1]}" {ACT}'
    if k == 'dmg':
        _, fixed, n, typ, fx = a
        e = f' effect="{fx}"' if fx else ''
        t = f' damageType="{typ}"' if typ else ''
        return f'Hurt who="AimedEntity" fixedDamage="{fixed}" dice="6" diceAmount="{n}" showNoDamage="false"{e}{t} {ACT}'
    if k == 'heal': return f'Heal who="ActingEntity" fixedLE="{a[1]}" dice="6" diceAmount="0" effect="Heal_Impact" consoleOutputType="Item_Berry" {ACT}'
    if k == 'asp': return f'RestoreAsP who="ActingEntity" fixedAsP="{a[1]}" dice="6" diceAmount="0" effect="AttributoKL_Impact" consoleOutputType="Item_SpellPotion" actionSelection="script"; '
    if k == 'buff': return f'SetStatusEffect who="ActingEntity" id="{a[1]}" {ACT}'
    if k == 'raw': return a[1]
    if k == 'vfx': return f'PlayVisualEffect effect="{a[1]}" target="{a[2] if len(a) > 2 else "AimedEntity"}" fixedposition="false" {ACT}'
    raise ValueError(a)

def build_procs(b, items):
    """Return list of statement GUIDs for a list of actions/procs (consecutive plain actions share one Action row)."""
    out, run = [], []
    def flush():
        if run: out.append(b.action(''.join(run))); run.clear()
    for it in items:
        if it[0] in ('p', 'if', 'race', 'ifnot'):
            flush()
            kids = it[2]
            if it[0] == 'p':
                if it[1] >= 100: out += build_procs(b, kids); continue
                atom, neg = f'RandomChance percent="{it[1]}"; ', False
            elif it[0] == 'if': atom, neg = f'HasStatusEffect id="{it[1]}" who="AimedEntity"; ', False
            elif it[0] == 'ifnot': atom, neg = f'HasStatusEffect id="{it[1]}" who="AimedEntity"; ', True
            else: atom, neg = f'IsRace who="AimedEntity" race="{it[1]}"; ', False
            out.append(b.if_(atom, lambda kids=kids: build_procs(b, kids), negate=neg))
        elif it[0] == 'st' and it[1] == 'burning':
            flush()
            out.append(b.if_('HasStatusEffect category="immunToFire" who="AimedEntity"; ',
                             lambda: [b.action(f'SetStatusEffect who="AimedEntity" id="burning" {ACT}')], negate=True))
        else:
            run.append(_action_text(it))
    flush()
    return out

def procs_text(items, se_names, depth=0):
    """Human-readable effect lines for the item description."""
    lines = []
    def act(a):
        k = a[0]
        if k == 'st': return se_names.get(a[1], NATIVE_NAMES.get(a[1], a[1]))
        if k == 'dmg':
            _, f, n, typ, fx = a
            amt = (f'{n}d6' if n else '') + (f'+{f}' if f and n else (str(f) if f else ''))
            return f"+{amt} {FX_NAMES.get(typ, '')} damage".replace('  ', ' ')
        if k == 'heal': return f'heals the wielder {a[1]} LE'
        if k == 'asp': return f'restores {a[1]} AE to the wielder'
        if k == 'buff': return f'wielder gains {se_names[a[1]]}'
        return None
    for it in items:
        if it[0] in ('p', 'if', 'race', 'ifnot'):
            sub = [x for x in (act(k) for k in it[2] if k[0] not in ('p', 'if', 'race', 'ifnot')) if x]
            nested = procs_text([k for k in it[2] if k[0] in ('p', 'if', 'race', 'ifnot')], se_names, depth + 1)
            if it[0] == 'p': head = 'On hit' if it[1] >= 100 else f'{it[1]}% on hit'
            elif it[0] == 'if': head = f"Against {FOE.get(it[1], se_names.get(it[1], it[1]).lower())} foes"
            elif it[0] == 'ifnot': head = f"If the foe is not {FOE.get(it[1], se_names.get(it[1], it[1]).lower())}"
            else: head = {'Mittellaender': 'Against humans', 'Untoter': 'Against the undead', 'Ork': 'Against orcs',
                          'Goblin': 'Against goblins', 'Kultist': 'Against cultists', 'Oger': 'Against ogres', 'Grolm': 'Against Grolms'}.get(it[1], f'Against {it[1]}')
            if sub: lines.append(f"{head}: {', '.join(sub)}")
            lines += [f'{head}, {l[0].lower()}{l[1:]}' for l in nested]
        else:
            x = act(it)
            if x: lines.append(f'On hit: {x}')
    return lines

class Mod:
    def __init__(self, db, ns):
        self.db, self.ns = db, ns
        dec = lambda b: b.decode('cp1252', 'replace')
        def conn(n):
            c = sqlite3.connect(f'file:{db}/{n}?mode=ro', uri=True); c.text_factory = dec; c.row_factory = sqlite3.Row; return c
        self.s, self.g, self.l = conn('static.db4'), conn('game.db4'), conn('locale.db4')
        self.static, self.undo_static, self.game, self.undo_game = [], [], [], []
        self.locale, self.se_names, self.new_guids = {}, {}, []
        self.templates, self.instances, self.loot_edits, self.icons = [], [], [], []
        self.vanilla_edits = []
        self._loot, self._vanilla_locale, self._vanilla_new = {}, {}, {}

    # ---- scripts ----
    def emit_block(self, b):
        for x, typ, content, blk in b.st:
            self.static.append(insert('_Scripts_Statements', dict(StatementGUID=x, StatementType=typ, StatementContent=content, StatementBlockGUID=blk)))
        for x, typ, content, blk in b.co:
            self.static.append(insert('_Scripts_Conditions', dict(ConditionGUID=x, ConditionType=typ, ConditionContent=content, ConditionBlockGUID=blk)))
        self.undo_static.append(f"DELETE FROM _Scripts_Statements WHERE StatementBlockGUID={lit(b.guid)};")
        if b.co: self.undo_static.append(f"DELETE FROM _Scripts_Conditions WHERE ConditionGUID IN ({','.join(lit(c[0]) for c in b.co)});")
        self.new_guids += [x for x, *_ in b.st] + [x for x, *_ in b.co]

    def hit_script(self, name, procs):
        b = Block(f'{self.ns}/hit/{name}'); b.begin(build_procs(b, procs))
        sname = f'weapon_on_scripts.xml_{name}'
        self.static.append(f'-- on-hit {sname}')
        self.emit_block(b)
        self.static.append(insert('_Scripts_ActionScripts', dict(ScriptName=sname, StatementRef=b.ref, StatementBlock=b.guid)))
        self.undo_static.append(f"DELETE FROM _Scripts_ActionScripts WHERE ScriptName={lit(sname)};")
        return 'on:Hit:' + sname

    def status(self, sid, name, desc, start='', duration=None, ticks=None, state_effect='', hardpoint='',
               texture='status_fx_good_jewel', categories='permanentEffect', immunity='', stackable=1):
        """Permanent (duration None) or timed status effect. ticks: list of SE-script action strings run in sequence."""
        assert re.fullmatch(r'[A-Za-z0-9]+', sid), f'status id {sid!r}: letters/digits only (underscores break item tooltips)'
        st = Block(f'{self.ns}/se/{sid}/start')
        st.begin([st.action((f'ModifyAttribute modifier="{start}" actionSelection="script"; ' if start else '') +
                            '')] if start else [])
        tr = Block(f'{self.ns}/se/{sid}/trigger')
        if duration is None:
            tr.begin([tr.action('WaitAction duration="1" permanent="true" actionSelection="script"; ')])
        else:
            body = ''.join(ticks or []) + f'WaitAction duration="{duration}" permanent="false" actionSelection="script"; '
            tr.begin([tr.action(body)])
        self.static.append(f'-- status effect {sid}')
        Z = bytes(16)
        if start: self.emit_block(st)
        self.emit_block(tr)
        sg = U(self.ns, 'se', sid)
        self.static.append(insert('_Scripts_StatusEffectScripts', dict(Guid=sg, Id=sid, Name='',
            StatusEffectOnStartRef=st.ref if start else Z, StatusEffectOnStartBlock=st.guid if start else Z,
            StatusEffectOnTriggerRef=tr.ref, StatusEffectOnStopRef=Z, StatusEffectOnTriggerBlock=tr.guid, StatusEffectOnStopBlock=Z,
            StatusEffectCategories='', StatusEffectTexture='', StatusEffectStackable=stackable, StatusEffectPower=1)))
        self.static.append(insert('_Template_Statuseffects', dict(Id=sid, State_Effect=state_effect, State_Hardpoint=hardpoint,
            State_Sound='', State_Texture=f'textures:icons/{texture}.dds', State_Categories=categories,
            Name=f'{sid}_name', ShortDescription=f'{sid}_short', LongDescription=f'{sid}_long', State_Immunity=immunity)))
        self.undo_static += [f"DELETE FROM _Scripts_StatusEffectScripts WHERE Guid={lit(sg)};", f"DELETE FROM _Template_Statuseffects WHERE Id={lit(sid)};"]
        self.locale[f'{sid}_name'] = name; self.locale[f'{sid}_short'] = name; self.locale[f'{sid}_long'] = desc
        self.se_names[sid] = name
        self.new_guids.append(sg)
        return sid

    # ---- templates ----
    def template(self, typ, base, iid, name, desc, **over):
        row = self.s.execute(f'select * from _Template_{typ} where Id=?', (base,)).fetchone()
        assert row, (typ, base)
        t = dict(row)
        t.update(Id=iid, Name=iid, LookAtText=f'lookat_{iid}', InfoIdentified=f'infoid_{iid}')
        for k in ('LookAtUnidentified', 'InfoUnIdentified'):
            if k in t: t[k] = f'lookat_{iid}' if k.startswith('Look') else f'infoid_{iid}'
        for k, v in (('IsIdentified', 1), ('IdentificationDifficulty', 0)):
            if k in t: t[k] = v
        for k in list(over):
            assert k in t, (typ, k)
        t.update(over)
        self.static.append(f'-- {typ} {iid}')
        self.static.append(insert(f'_Template_{typ}', t))
        self.undo_static.append(f"DELETE FROM _Template_{typ} WHERE Id={lit(iid)};")
        self.locale[f'lookat_{iid}'] = name; self.locale[f'infoid_{iid}'] = desc
        self.templates.append((typ, iid, t))
        return t

    def edit_vanilla(self, typ, iid, **over):
        """Change columns of a vanilla template; undo restores the exact original values."""
        row = dict(self.s.execute(f'select * from _Template_{typ} where Id=?', (iid,)).fetchone())
        sets = ', '.join(f'{k}={lit(v)}' for k, v in over.items())
        back = ', '.join(f'{k}={lit(row[k])}' for k in over)
        self.static.append(f"UPDATE _Template_{typ} SET {sets} WHERE Id={lit(iid)};")
        self.undo_static.append(f"UPDATE _Template_{typ} SET {back} WHERE Id={lit(iid)};")
        self.vanilla_edits.append((typ, iid, over, {k: row[k] for k in over}))
        # existing world instances of this template (game.db4) get the same columns
        icols = {c[1] for c in self.g.execute(f'pragma table_info(_Instance_{typ})')}
        o2 = {k: v for k, v in over.items() if k in icols}
        if o2 and self.g.execute(f'select count(*) from _Instance_{typ} where Id=?', (iid,)).fetchone()[0]:
            self.game.append(f"UPDATE _Instance_{typ} SET {', '.join(f'{k}={lit(v)}' for k, v in o2.items())} WHERE Id={lit(iid)};")
            self.undo_game.append(f"UPDATE _Instance_{typ} SET {', '.join(f'{k}={lit(row[k])}' for k in o2)} WHERE Id={lit(iid)};")

    def text(self, key, value): self.locale[key] = value

    # ---- placement ----
    OWNER_TABLE = {'chest': '_Instance_Chest', 'npc': '_Instance_NPC', 'pc': '_Instance_PC'}
    def owner(self, kind, oid, level=None, index=0):
        q = f"select Guid, _Level, StorageContentCount from {self.OWNER_TABLE[kind]} where Id=?" + (" and _Level=?" if level else '') + " order by rowid"
        rows = self.g.execute(q, (oid, level) if level else (oid,)).fetchall()
        assert rows, (kind, oid, level)
        r = rows[index]
        assert r['StorageContentCount'] is not None, ('owner without explicit storage', oid)
        return r['Guid'], r['_Level']

    def place(self, typ, iid, kind, oid, level=None, stack=1, index=0, tag=''):
        tmpl = next(t for ty, i, t in self.templates if i == iid) if any(i == iid for _, i, _ in self.templates) \
            else dict(self.s.execute(f'select * from _Template_{typ} where Id=?', (iid,)).fetchone())
        og, lvl = self.owner(kind, oid, level, index)
        icols = [c[1] for c in self.g.execute(f'pragma table_info(_Instance_{typ})')]
        row = {c: tmpl.get(c) for c in icols}
        guid = U(self.ns, 'inst', iid, oid, lvl, str(index), tag).bytes
        row.update(Guid=guid, _ID='', _Level=lvl, _Layers='', Transform=IDENT, StorageGUID=og, Lootable=0)
        if 'StackCount' in row: row['StackCount'] = stack
        miss = [c for c in icols if row[c] is None and c not in tmpl]
        assert not miss, (typ, iid, miss)
        G, OT = lit(guid), self.OWNER_TABLE[kind]
        self.game += [f'-- {iid} -> {oid} ({lvl})',
                      f"UPDATE {OT} SET StorageContentCount=StorageContentCount+1 WHERE Guid={lit(og)} AND NOT EXISTS (SELECT 1 FROM _Instance_{typ} WHERE Guid={G});",
                      insert(f'_Instance_{typ}', row, 'INSERT OR IGNORE')]
        self.undo_game += [f"UPDATE {OT} SET StorageContentCount=StorageContentCount-1 WHERE Guid={lit(og)} AND EXISTS (SELECT 1 FROM _Instance_{typ} WHERE Guid={G});",
                           f"DELETE FROM _Instance_{typ} WHERE Guid={G};"]
        self.instances.append((typ, iid, guid, kind, oid, lvl))

    # Avestrue is the tutorial area (little money, little XP, no way back): whatever we put there is also sold in Ferdok
    MIRROR_OWNER = {'Jaeger_Kauzenstein': ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'),
                    'alchimistin_loc01': ('Dorfbewohnerin_loc02_haendler_praios_kraeuter', 'location02_praios'),
                    'bredo_bento_loc01': ('Haendler_3_loc02_haendler_praios_waffen', 'location02_praios')}
    MIRROR_TYPE = {'Weapon': ('Haendler_3_loc02_haendler_praios_waffen', 'location02_praios'), 'Ammo': ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios'),
                   'Recipe': ('Jaeger_Kauzenstein_loc02_trainer_praios_bogen', 'location02_praios')}
    MIRROR_DEFAULT = ('Dorfbewohner04_loc02_haendler_praios_gemischt', 'location02_praios')
    def mirror_early(self):
        ferdok = {i for _, i, _, _, _, l in self.instances if l.startswith(('location02', 'dungeon02'))}
        for typ, iid, _, kind, oid, lvl in list(self.instances):
            if kind == 'pc' or not (lvl == 'location01' or lvl.startswith('dungeon01')) or iid in ferdok: continue   # companion gifts stay personal
            o, l = self.MIRROR_OWNER.get(oid) or self.MIRROR_TYPE.get(typ, self.MIRROR_DEFAULT)
            self.place(typ, iid, 'npc', o, l, stack=20 if typ == 'Ammo' else 1, tag='ferdokmirror'); ferdok.add(iid)

    RECIPE_ICON_WEAPON = {'TaSaebel': 'recipe_weapon_saebel', 'TaSchwerter': 'recipe_weapon_crafted_kurzschwert', 'TaFechtwaffen': 'recipe_weapon_crafted_verbesserter_magierdegen',
                          'TaDolche': 'recipe_weapon_crafted_wurfmesser', 'TaWurfwaffen': 'recipe_wurfmesser', 'TaHiebwaffen': 'recipe_weapon_crafted_verbesserte_streitaxt',
                          'TaZwHiebwaffen': 'recipe_weapon_drachentoeterhammer', 'TaZwSchwerter': 'recipe_weapon_zweihaender', 'TaSpeere': 'recipe_weapon_speer',
                          'TaInfanteriewaffen': 'recipe_weapon_speer', 'TaStaebe': 'recipe_verb_knauf', 'TaBogen': 'recipe_langbogen', 'TaArmbrust': 'recipe_leichte_armbrust'}
    def recipe_icon(self, typ, iid, skill=''):
        assert skill in ('', 'TaSchmieden', 'TaBogenbau', 'TaAlchimie'), f'{iid}: no workbench exists for {skill} (only Forging, Bowcraft, Alchemy)'
        """Vanilla recipe icon matching what the recipe makes (instead of one icon for everything)."""
        t = next((t for ty, i, t in self.templates if i == iid), None) or dict(self.s.execute(f'select * from _Template_{typ} where Id=?', (iid,)).fetchone() or {})
        if typ == 'Weapon' and not t.get('TaAttr'):   # result from an earlier module (armory_v2): look at its base weapon's class via our naming
            t = {'TaAttr': {'arm_s_rondra_reprimand': 'TaSaebel', 'arm_s_mountain_patience': 'TaZwHiebwaffen', 'arm_s_nightsong': 'TaBogen',
                            'arm_d_black_widow': 'TaDolche'}.get(iid, '')}
        if typ == 'Weapon': name = self.RECIPE_ICON_WEAPON.get(t.get('TaAttr'), 'recipe_weapon_crafted_kurzschwert')
        elif typ == 'Armor': name = 'recipe_wattiertes_kettenhemd'
        elif typ == 'Shield': name = 'recipe_weapon_eisenschild'
        elif typ == 'Jewelry': name = 'recipe_diamantenschleifstein'
        elif typ == 'Ammo': name = 'recipe_kriegsbolzen' if 'olz' in (t.get('WpAmmoCategory') or '') + iid else 'recipe_kriegspfeil'
        elif t.get('TrapId'): name = 'recipe_baerenfalle'
        elif skill == 'TaMagiekunde': name = 'recipe_zaubertrank'
        elif skill == 'TaAlchimie': name = 'recipe_heiltrank'
        else: name = 'recipe_schleifstein'
        return f'icons/{name}'

    def loot(self, table, typ, iid, mode='all', chance=100, amount=1, value=0):
        """Queue a loot-table entry. mode 'all': raise the pick count so every entry (vanilla + ours) drops;
        'plus1': one extra pick; 'none': leave the pick count. Value-0 tables are always raised to every entry (0 does not roll them all)."""
        r = self.loot_tables().get(table)
        assert r, table
        st = self._loot.setdefault(table, dict(v=r[0], n=r[1].count(';'), entries=[], mode=mode))
        if mode != 'none': st['mode'] = mode
        st['entries'].append(f'{typ}/{iid}/{chance}/{amount}/{value}/;')
        self.loot_edits.append((table, st['entries'][-1], r[0]))

    def loot_tables(self):
        """All loot tables keyed by their cp1252-decoded name (names like skin_baer_groß cannot be looked up with a UTF-8 parameter)."""
        if not hasattr(self, '_lt_cache'):
            self._lt_cache = {r[0]: (r[1], r[2]) for r in self.s.execute('select LootTableName, LootTableValue, LootTableContent from _DSA_LootTables')}
        return self._lt_cache

    def emit_loot(self):
        """Idempotent against ANY prior state: strip each of our entries, append them once, set the pick count absolutely."""
        for table, st in self._loot.items():
            v, n, add = st['v'], st['n'], ''.join(st['entries'])
            strip = 'LootTableContent'
            for e in st['entries']: strip = f"REPLACE({strip},{lit(e)},'')"
            if v in ('0', ''):   # a value-0 table does not roll every entry: draw them all (vanilla + ours)
                newv = str(n + len(st['entries']))
            elif v.isdigit() and st['mode'] in ('all', 'plus1'):
                newv = str(max(int(v), n) + len(st['entries'])) if st['mode'] == 'all' else str(int(v) + len(st['entries']))
            else:
                newv = v
            self.static.append(f"UPDATE _DSA_LootTables SET LootTableValue={lit(newv)}, LootTableContent={strip}||{lit(add)} WHERE LootTableName={lit(table)};")
            self.undo_static.append(f"UPDATE _DSA_LootTables SET LootTableValue={lit(v)}, LootTableContent={strip} WHERE LootTableName={lit(table)};")

    def vanilla_text(self, key, value):
        """Replace a vanilla locale text; undo restores it."""
        r = self.l.execute('select LocaText from _Locale where LocaId=?', (key,)).fetchone()
        assert r, key
        self._vanilla_locale[key] = r[0]; self._vanilla_new[key] = value

    # ---- output ----
    def check_collisions(self):
        for x in self.new_guids:
            for t, c in (('_Scripts_Statements', 'StatementGUID'), ('_Scripts_Conditions', 'ConditionGUID'), ('_Scripts_StatusEffectScripts', 'Guid')):
                if self.s.execute(f'select count(*) from {t} where {c}=?', (x.bytes_le,)).fetchone()[0]:
                    raise SystemExit(f'GUID {x} already in {t}: uninstall the mod first, then rebuild')
        for typ, iid, _ in self.templates:
            if self.s.execute(f'select count(*) from _Template_{typ} where Id=?', (iid,)).fetchone()[0]:
                raise SystemExit(f'template {iid} already exists: uninstall the mod first, then rebuild')

    def write(self, out):
        os.makedirs(os.path.join(out, 'sql'), exist_ok=True)
        self.emit_loot()
        loc = [insert('_Locale', dict(LocaId=k, LocaText=v)) for k, v in {**self.locale, **self._vanilla_new}.items()]
        uloc = [f"DELETE FROM _Locale WHERE LocaId IN ({','.join(lit(k) for k in self.locale)});"] +                [insert('_Locale', dict(LocaId=k, LocaText=v)) for k, v in self._vanilla_locale.items()]
        files = {'static.sql': self.static, 'locale.sql': loc, 'game.sql': self.game,
                 'undo_static.sql': self.undo_static[::-1], 'undo_locale.sql': uloc,
                 'undo_game.sql': self.undo_game}  # keep order: each count update must run before its DELETE
        for name, lines in files.items():
            with open(os.path.join(out, 'sql', name), 'w', encoding='cp1252', newline='\r\n') as f:
                f.write('BEGIN;\n' + '\n'.join(lines) + '\nCOMMIT;\n')
        self.write_verify(out)

    def write_verify(self, out):
        g = self.g
        stor = [t for (t,) in g.execute("select name from sqlite_master where type='table' and name like '_Instance_%'")
                if 'StorageGUID' in [c[1] for c in g.execute(f'pragma table_info({t})')]]
        owned = lambda tbl: ' + '.join(f"(SELECT count(*) FROM {t} WHERE StorageGUID={tbl}.Guid)" for t in stor)
        types = sorted({t for t, *_ in self.instances})
        guids = {t: ','.join(lit(x) for ty, _, x, *_ in self.instances if ty == t) for t in types}
        n_inst = ' + '.join(f"(SELECT count(*) FROM _Instance_{t} WHERE Guid IN ({guids[t]}))" for t in types) or '0'
        vg = [f"SELECT 'placed items (expect {len(self.instances)}): ' || ({n_inst});"]
        for ot in ('_Instance_Chest', '_Instance_NPC', '_Instance_PC'):
            vg.append(f"SELECT '{ot[10:]} owners whose count differs from their items: ' || count(*) FROM {ot} WHERE StorageContentCount IS NOT NULL AND StorageContentCount <> ({owned(ot)});")
        vg += ["SELECT 'game.db4 integrity check:'; PRAGMA integrity_check;"]
        ttypes = sorted({t for t, *_ in self.templates})
        tc = ' + '.join(f"(SELECT count(*) FROM _Template_{t} WHERE Id IN ({','.join(lit(i) for ty, i, _ in self.templates if ty == t)}))" for t in ttypes) or '0'
        ses = [k[:-5] for k in self.locale if k.endswith('_name') and k[:-5] in self.se_names]
        vs = [f"SELECT 'new item templates (expect {len(self.templates)}): ' || ({tc});",
              f"SELECT 'new status effects (expect {len(ses)}): ' || (SELECT count(*) FROM _Scripts_StatusEffectScripts WHERE Id IN ({','.join(lit(x) for x in ses) or 'NULL'}));",
              f"SELECT 'loot entries (expect {len(self.loot_edits)}): ' || ({' + '.join(f'(SELECT count(*) FROM _DSA_LootTables WHERE LootTableName={lit(t)} AND LootTableContent LIKE {lit(chr(37) + e + chr(37))})' for t, e, _ in self.loot_edits) or '0'});",
              "SELECT 'static.db4 integrity check:'; PRAGMA integrity_check;"]
        vl = [f"SELECT 'texts (expect {len(self.locale)}): ' || (SELECT count(*) FROM _Locale WHERE LocaId IN ({','.join(lit(k) for k in self.locale)}));",
              "SELECT 'locale.db4 integrity check:'; PRAGMA integrity_check;"]
        for name, lines in (('verify_game.sql', vg), ('verify_static.sql', vs), ('verify_locale.sql', vl)):
            with open(os.path.join(out, 'sql', name), 'w', encoding='cp1252', newline='\r\n') as f: f.write('\n'.join(lines) + '\n')

# ---------------- icons ----------------
GLOW = {'regular': None, 'amazing': (80, 150, 255), 'superrare': (160, 95, 235), 'legendary': (245, 190, 70), 'mythic': (150, 18, 18), 'test': (255, 0, 200)}
HALO_ALPHA = {'amazing': 0.95, 'superrare': 0.95, 'legendary': 1.0, 'mythic': 1.0, 'test': 1.0}
def make_icon(src_dds, out_dds, tier, tint=None, header=None):
    """Native-style icon: dark contact shadow (light from top-left) + tight low-opacity tier halo (+ light tint)."""
    from PIL import Image, ImageFilter, ImageChops
    im = Image.open(src_dds).convert('RGBA') if isinstance(src_dds, str) else src_dds.convert('RGBA')
    if tint:
        r, g, b, a = im.split()
        grey = Image.merge('RGB', (r, g, b)).convert('L')
        col = Image.merge('RGB', [grey.point(lambda v, c=c: min(255, v * c // 200)) for c in tint])
        im = Image.merge('RGBA', (*Image.blend(Image.merge('RGB', (r, g, b)), col, 0.3).split(), a))
    a = im.split()[3]
    core = a.point(lambda v: 255 if v > 160 else 0)
    base = Image.new('RGBA', im.size, (0, 0, 0, 0))
    if GLOW.get(tier):
        halo = core.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * HALO_ALPHA[tier]))
        glow = Image.new('RGBA', im.size, GLOW[tier] + (0,)); glow.putalpha(halo)
        base = Image.alpha_composite(base, glow)
    sh = core.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.65))
    sh = ImageChops.offset(sh, 2, 2)
    shadow = Image.new('RGBA', im.size, (22, 12, 4, 0)); shadow.putalpha(sh)
    base = Image.alpha_composite(base, shadow)
    solid = im.copy(); solid.putalpha(ImageChops.multiply(a, a.point(lambda v: 255 if v > 40 else v * 6)))
    out = Image.alpha_composite(base, solid)
    with open(out_dds, 'wb') as f: f.write(VANILLA_ICON_HEADER + encode_dxt3(out))
    return out

# header of a vanilla icon (export_1.npk: textures/icons/loot_silberring.dds): 128x128 DXT3, no mips, flags 0x81007
VANILLA_ICON_HEADER = bytes.fromhex(
    '444453207c0000000710080080000000800000000040000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    '00000000000000000000000020000000040000004458543300000000000000000000000000000000000000000010000000000000000000000000000000000000')

def encode_dxt3(img):
    """DXT3 encoder: explicit 4-bit alpha + 4-colour block fitted along the principal axis of the visible pixels."""
    import numpy as np
    a = np.asarray(img.convert('RGBA'), dtype=np.float64)
    h, w = a.shape[:2]
    out = bytearray()
    def to565(c):
        r, g, b = (int(round(x)) for x in np.clip(c, 0, 255))
        return ((r * 31 + 127) // 255) << 11 | ((g * 63 + 127) // 255) << 5 | ((b * 31 + 127) // 255)
    def from565(v):
        r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
        return np.array([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)], dtype=np.float64)
    for by in range(0, h, 4):
        for bx in range(0, w, 4):
            blk = a[by:by + 4, bx:bx + 4].reshape(16, 4)
            al = blk[:, 3]; rgb = blk[:, :3]
            q = np.clip(np.round(al / 17.0), 0, 15).astype(int)
            ab = 0
            for i in range(16): ab |= int(q[i]) << (4 * i)
            out += ab.to_bytes(8, 'little')
            vis = al > 8
            pts = rgb[vis] if vis.any() else rgb
            mean = pts.mean(axis=0); d = pts - mean
            cov = d.T @ d
            axis = np.ones(3)
            for _ in range(8):
                nxt = cov @ axis; nn = np.linalg.norm(nxt)
                if nn < 1e-9: break
                axis = nxt / nn
            proj = d @ axis
            c0, c1 = to565(mean + axis * proj.max()), to565(mean + axis * proj.min())
            if c0 < c1: c0, c1 = c1, c0
            p0, p1 = from565(c0), from565(c1)
            pal = np.array([p0, p1, (2 * p0 + p1) / 3, (p0 + 2 * p1) / 3])
            idx = np.argmin(((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2), axis=1)
            if c0 == c1: idx[:] = 0
            bits = 0
            for i in range(16): bits |= int(idx[i]) << (2 * i)
            out += c0.to_bytes(2, 'little') + c1.to_bytes(2, 'little') + bits.to_bytes(4, 'little')
    return bytes(out)

def pack_names(root):
    """Display names of every item the pack defines (from the built mods' locale.sql), for recipe tooltips across modules."""
    import glob
    names = {}
    for f in glob.glob(os.path.join(root, 'mods', '*', 'sql', 'locale.sql')):
        for k, v in re.findall(r"VALUES \('lookat_(arm_[a-z0-9_]+)','((?:[^']|'')*)'\)", open(f, encoding='cp1252').read()):
            names[k] = v.replace("''", "'")
    return names
