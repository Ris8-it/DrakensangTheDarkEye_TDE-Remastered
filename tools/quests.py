"""Quest/dialog/NPC builder on top of dsa.Mod (see docs/ENGINE_REFERENCE.md §11).

Dialog model (decoded from vanilla, e.g. Loc03BredoDialog):
  _Story_Dialogs(DialogGUID, DialogId, DialogName, DialogSpeaker=<NPC Name>, DialogGroup, DialogAsConversation)
  _Story_DialogTakes: one row per line. TakeType StartState | Take (NPC) | Response (player). Text lives in _Locale under
     str(uuid(bytes_le=TakeLocaId)). Unvoiced lines: TakeSound '', TakeSoundActiv 0, TakeTimeStamp 0.
  _Story_DialogTakeChildMapping(TakeGUID, TakeChildId, TakeChildPosition, DialogGUID): the tree (children by TakeId), no primary key.
     StartState children are tried in order; the first whose condition passes is shown. Takes never chain to Takes:
     companion interjections go Take -> Response '<Next>' -> Take (speaker = companion Name, condition IsPartyMember).
  _Story_DialogConditions: same shape as script conditions (Atom / Not / And / Or + top 'Condition' row, one block per take).
  _Story_DialogActions(TakeGUID, ActionContent): verbs run when the line is said.
  game.db4: _Story_Dialogs(DialogId, DialogLocked), _Story_DialogTakeStatus(DialogId+TakeId, 0).
Tasks: _Story_Tasks parent = quest (TaskParentGuid zero), children = steps. Open/close condition blocks in
  _Story_TaskOpenConditions / _Story_TaskCloseConditions with top row type OpenCondition / CloseCondition. game.db4 _Story_Tasks(TaskId, TaskState).
NPCs: instance row in game.db4 (_ID '|Level|Objects|NPC|<Id>' unique per level) + _Template_NPC. Carried items are instance rows with
  StorageGUID = NPC Guid (Lootable 1 = drops) mirrored in the template's SetupStorage ('Weapon/Brabakbengel/true/false;'); NPCs wield
  weapons from storage. Hostility: dialog action SetFaction faction="FaFeind" who="<Name>"; death: condition IsDead who="<Name>".
"""
import uuid, struct
from dsa import U, lit, insert, IDENT

Z = bytes(16)
ACTSEL = 'actionSelection="script,quest,dialog"; '

class Story:
    def __init__(self, mod, ns):
        self.m, self.ns = mod, ns

    # ---------- conditions ----------
    def _cond(self, table, key, atoms, top_type, combine='And'):
        """atoms: list of atom strings; prefix '!' = negated; a nested list = Or of its atoms. Returns (ref_guid, block_guid) or (Z, Z)."""
        if not atoms: return Z, Z
        blk = U(self.ns, key, 'cb'); n = [0]; rows = []
        def g():
            n[0] += 1; return U(self.ns, key, f'c{n[0]}')
        def build(a):
            if isinstance(a, (list, tuple)):
                kids = [build(x) for x in a]
                if len(kids) == 1: return kids[0]
                c = g(); rows.append((c, 'Or', ';'.join(map(str, kids)))); return c
            neg = a.startswith('!'); a = a.lstrip('!')
            x = g(); rows.append((x, 'Atom', a.strip() + ' ' if not a.endswith(' ') else a))
            if not neg: return x
            y = g(); rows.append((y, 'Not', str(x))); return y
        tops = [build(a) for a in atoms]
        if len(tops) > 1: c = g(); rows.append((c, combine, ';'.join(map(str, tops)))); tops = [c]
        ref = g(); rows.append((ref, top_type, str(tops[0])))
        for x, t, content in rows:
            self.m.static.append(insert(table, dict(ConditionGUID=x, ConditionType=t, ConditionContent=content, ConditionBlockGUID=blk)))
        self.m.undo_static.append(f"DELETE FROM {table} WHERE ConditionBlockGUID={lit(blk)};")
        return ref, blk

    # ---------- dialogs ----------
    def dialog(self, did, speaker, takes):
        """New dialog. takes: list of dicts(id, type, text, kids=[], cond=[atoms], act='', speaker=None). First must be StartState."""
        m = self.m
        dg = U(self.ns, 'dialog', did)
        m.static += [f"DELETE FROM _Story_Dialogs WHERE DialogId={lit(did)};",
                     insert('_Story_Dialogs', dict(DialogGUID=dg, DialogId=did, DialogName=did, DialogSpeaker=speaker, DialogGroup='', DialogAsConversation=0))]
        m.undo_static += [f"DELETE FROM _Story_Dialogs WHERE DialogId={lit(did)};", f"DELETE FROM _Story_DialogTakes WHERE DialogId={lit(did)};",
                          f"DELETE FROM _Story_DialogTakeChildMapping WHERE DialogGUID={lit(dg)};"]
        m.game += [f"DELETE FROM _Story_Dialogs WHERE DialogId={lit(did)};", insert('_Story_Dialogs', dict(DialogId=did, DialogLocked=0))]
        m.undo_game.append(f"DELETE FROM _Story_Dialogs WHERE DialogId={lit(did)};")
        self._takes(did, dg, speaker, takes)
        return dg

    def extend_dialog(self, did, attach, takes, position=20):
        """Add our takes to a VANILLA dialog and hang responses under existing vanilla takes: attach = {vanilla TakeId: [our response ids]}
        (appended after the vanilla answers). Undo removes exactly our rows; vanilla rows are never rewritten."""
        m = self.m
        dg, speaker = m.s.execute('select DialogGUID, DialogSpeaker from _Story_Dialogs where DialogId=?', (did,)).fetchone()
        vt = {r[0]: r[1] for r in m.s.execute('select TakeId, TakeGUID from _Story_DialogTakes where DialogId=?', (did,))}
        for take_id, kids in attach.items():
            tg = vt[take_id]
            for i, kid in enumerate(kids):
                m.static += [f"DELETE FROM _Story_DialogTakeChildMapping WHERE TakeGUID={lit(tg)} AND TakeChildId={lit(kid)};",
                             insert('_Story_DialogTakeChildMapping', dict(TakeGUID=tg, TakeChildId=kid, TakeChildPosition=position + i, DialogGUID=dg))]
                m.undo_static.append(f"DELETE FROM _Story_DialogTakeChildMapping WHERE TakeGUID={lit(tg)} AND TakeChildId={lit(kid)};")
        self._takes(did, dg, speaker, takes, own_dialog=False)
        return dg

    def _takes(self, did, dg, speaker, takes, own_dialog=True):
        m = self.m
        for t in takes:
            tg = U(self.ns, 'take', did, t['id'])
            ref, blk = self._cond('_Story_DialogConditions', f'{did}/{t["id"]}', t.get('cond', []), 'Condition')
            loca = U(self.ns, 'loca', did, t['id']) if t['type'] != 'StartState' else None
            spk = '' if t['type'] == 'StartState' else ('Player' if t['type'] == 'Response' else t.get('speaker', speaker))
            m.static += [f"DELETE FROM _Story_DialogTakes WHERE TakeGUID={lit(tg)};",
                         insert('_Story_DialogTakes', dict(TakeGUID=tg, DialogGUID=dg, DialogId=did, TakeId=t['id'], TakeSpeaker=spk, TakeType=t['type'],
                                TakeEmote='', TakeSound='', TakeSoundActiv=0, TakeText='', TakeShortText='', ConditionRef=ref, ConditionBlock=blk,
                                TakeLocaId=loca or Z, TakeTimeStamp=0.0, TakeShortTextLocaId=Z))]
            m.static.append(f"DELETE FROM _Story_DialogTakeChildMapping WHERE TakeGUID={lit(tg)};")
            if not own_dialog:
                m.undo_static += [f"DELETE FROM _Story_DialogTakes WHERE TakeGUID={lit(tg)};", f"DELETE FROM _Story_DialogTakeChildMapping WHERE TakeGUID={lit(tg)};"]
            for i, kid in enumerate(t.get('kids', [])):
                m.static.append(insert('_Story_DialogTakeChildMapping', dict(TakeGUID=tg, TakeChildId=kid, TakeChildPosition=i, DialogGUID=dg)))
            m.static.append(f"DELETE FROM _Story_DialogActions WHERE TakeGUID={lit(tg)};")
            if t.get('act'):
                m.static.append(insert('_Story_DialogActions', dict(TakeGUID=tg, ActionContent=t['act'])))
            m.undo_static.append(f"DELETE FROM _Story_DialogActions WHERE TakeGUID={lit(tg)};")
            if loca: m.text(str(loca), t['text'])
            m.game += [f"DELETE FROM _Story_DialogTakeStatus WHERE TakeId={lit(did + t['id'])};", insert('_Story_DialogTakeStatus', dict(TakeId=did + t['id'], TakeStatus=0))]
            m.undo_game.append(f"DELETE FROM _Story_DialogTakeStatus WHERE TakeId={lit(did + t['id'])};")

    # ---------- tasks ----------
    def task(self, tid, title, open_text, close_text, parent=None, state='locked', open_cond=(), close_cond=(), open_act='', close_act='', target=''):
        m = self.m
        tg = U(self.ns, 'task', tid)
        oref, oblk = self._cond('_Story_TaskOpenConditions', f'task/{tid}/open', list(open_cond), 'OpenCondition')
        cref, cblk = self._cond('_Story_TaskCloseConditions', f'task/{tid}/close', list(close_cond), 'CloseCondition')
        L = {k: U(self.ns, 'tasktext', tid, k) for k in ('title', 'open', 'close')}
        m.static += [f"DELETE FROM _Story_Tasks WHERE TaskId={lit(tid)};",
                     insert('_Story_Tasks', dict(TaskGUID=tg, TaskId=tid, TaskTitle=title, TaskParentGuid=U(self.ns, 'task', parent) if parent else Z, TaskState=state,
                            TaskOpenText=open_text, TaskCloseText=close_text, TaskFailedText='', CloseConditionBlock=cblk, CloseConditionRef=cref,
                            OpenConditionBlock=oblk, OpenConditionRef=oref, TaskTargetEntity=target, TaskTitleLocaId=L['title'], TaskOpenTextLocaId=L['open'],
                            TaskCloseTextLocaId=L['close'], TaskFailedTextLocaId=Z))]
        m.undo_static.append(f"DELETE FROM _Story_Tasks WHERE TaskId={lit(tid)};")
        for tbl, a in (('_Story_TaskOpenActions', open_act), ('_Story_TaskCloseActions', close_act)):
            m.static.append(f"DELETE FROM {tbl} WHERE TaskGUID={lit(tg)};")
            if a: m.static.append(insert(tbl, dict(TaskGUID=tg, ActionContent=a)))
            m.undo_static.append(f"DELETE FROM {tbl} WHERE TaskGUID={lit(tg)};")
        m.text(str(L['title']), title); m.text(str(L['open']), open_text); m.text(str(L['close']), close_text)
        m.game += [f"DELETE FROM _Story_Tasks WHERE TaskId={lit(tid)};", insert('_Story_Tasks', dict(TaskId=tid, TaskState=state))]
        m.undo_game.append(f"DELETE FROM _Story_Tasks WHERE TaskId={lit(tid)};")
        return tg

    # ---------- NPCs ----------
    def npc(self, nid, display, clone, level, anchor, offset=(0.0, 0.0, 0.0), merchant=False, park=False, **over):
        """Clone an existing NPC (template + instance; `clone` = instance Id or Name) as a new character placed at
        `anchor` = (instance table, Name) in `level`, e.g. ('NPC', 'Jaeger_Kauzenstein') or ('MarkerPoint', 'Loc03_Marker_Burg'), plus `offset` metres.
        `over`: columns set on both template and instance (stats, Behaviour, LootTable, ...).
        park=True: the NPC (and its stock) starts in the '_graveyard_' level, like vanilla's parked characters, and an entry point
        '<nid>_entry' marks its real spot; bring it in with arrive(nid)."""
        m = self.m
        src = m.g.execute('select * from _Instance_NPC where (Id=? or Name=?) and _Level=? order by rowid', (clone, clone, level)).fetchone() \
            or m.g.execute('select * from _Instance_NPC where Id=? or Name=? order by rowid', (clone, clone)).fetchone()
        assert src, (clone, level)
        src = dict(src)
        tmpl = dict(m.s.execute('select * from _Template_NPC where Id=?', (src['Id'],)).fetchone())
        tmpl.update(Id=nid, Name=nid, LookAtText=f'lookat_{nid}', StolenGoodsTable='', SetupStorage='', CanRob=0)
        a = self._anchor(anchor, level)
        assert a, (anchor, level)
        mat = list(struct.unpack('<16f', a)); mat[12] += offset[0]; mat[13] += offset[1]; mat[14] += offset[2]
        row = dict(src)
        row.update(Guid=U(self.ns, 'npc', nid).bytes, _ID=f'|Level|Objects|NPC|{nid}', _Level=level, Id=nid, Name=nid, LookAtText=f'lookat_{nid}',
                   Transform=struct.pack('<16f', *mat), StorageContentCount=0, CanRob=0, StolenGoodsTable='', Faction='FaAllFriendly', CanTalk=1,
                   BaseActionScript='', BaseAction='', CurrAction='v*;2;false;false;')   # idle: the clone's routine/saved action (patrol paths of its home level) crashes elsewhere
        tmpl['BaseActionScript'] = ''
        if merchant: row.update(RetailFactor=1.0, PurchaseFactor=0.5)
        for k, v in over.items():
            assert k in row or k in tmpl, (nid, k)
            if k in row: row[k] = v
            if k in tmpl: tmpl[k] = v
        m.static += [f"DELETE FROM _Template_NPC WHERE Id={lit(nid)};", insert('_Template_NPC', tmpl)]
        m.undo_static.append(f"DELETE FROM _Template_NPC WHERE Id={lit(nid)};")
        if park:
            donor = m.g.execute("select * from _Instance_Entry where _Level=? and Id='EntryPortalObject' order by rowid", (level,)).fetchone() \
                or m.g.execute("select * from _Instance_Entry where Id='EntryPortalObject' order by rowid").fetchone()   # object entry, never a party portal
            ent = dict(donor)
            ename = f'{nid}_entry'
            ent.update(Guid=U(self.ns, 'entry', nid).bytes, _ID=f'|Level|Objects|Entry|{ename}', _Level=level, Name=ename, Transform=row['Transform'])
            m.game += [f"DELETE FROM _Instance_Entry WHERE Guid={lit(ent['Guid'])};", insert('_Instance_Entry', ent)]
            m.undo_game.insert(0, f"DELETE FROM _Instance_Entry WHERE Guid={lit(ent['Guid'])};")
            m._arrivals = getattr(m, '_arrivals', {}); m._arrivals[nid] = (level, ename)
            row['_Level'] = '_graveyard_'
        m.game += [f"DELETE FROM _Instance_NPC WHERE Guid={lit(row['Guid'])};", insert('_Instance_NPC', row)]
        m.undo_game.insert(0, f"DELETE FROM _Instance_NPC WHERE Guid={lit(row['Guid'])};")
        m.text(f'lookat_{nid}', display)
        m._npc_rows = getattr(m, '_npc_rows', {}); m._npc_rows[nid] = (row['Guid'], row['_Level'])
        return row['Guid']

    def arrive(self, nid):
        """Dialog/task action that moves a parked NPC (npc(park=True)) from '_graveyard_' to its entry point."""
        level, ename = self.m._arrivals[nid]
        return f'TransferEntity entity="{nid}" location="{level}" entryPoint="{ename}" track="0" {ACTSEL}'

    def _anchor(self, anchor, level):
        """anchor = (instance table, value[, column='Name']) -> Transform blob."""
        tbl, val, col = (tuple(anchor) + ('Name',))[:3]
        a = self.m.g.execute(f'select Transform from _Instance_{tbl} where "{col}"=? and _Level=?', (val, level)).fetchone()
        assert a, (anchor, level)
        return a[0]

    def monster(self, mid, display, base, level, anchor, offset=(0.0, 0.0, 0.0), info='', **over):
        """A one-off placed monster (no respawn): template clone of `base` with `over` (stats, LootTable, ...) and an instance at `anchor`."""
        m = self.m
        tmpl = dict(m.s.execute('select * from _Template_Monster where Id=?', (base,)).fetchone())
        for k in over: assert k in tmpl, (mid, k)
        tmpl.update(Id=mid, Name=mid, LookAtAliveText=f'lookat_{mid}', LookAtDeathText=f'lookatdead_{mid}', **over)
        if info: tmpl['InfoIdentified'] = f'infoid_{mid}'; m.text(f'infoid_{mid}', info)
        m.text(f'lookatdead_{mid}', f'Dead {display}')
        m.static += [f"DELETE FROM _Template_Monster WHERE Id={lit(mid)};", insert('_Template_Monster', tmpl)]
        m.undo_static.append(f"DELETE FROM _Template_Monster WHERE Id={lit(mid)};")
        donor = m.g.execute('select * from _Instance_Monster where Id=? order by rowid', (base,)).fetchone() or m.g.execute('select * from _Instance_Monster order by rowid').fetchone()
        donor = dict(donor)
        mat = list(struct.unpack('<16f', self._anchor(anchor, level))); mat[12] += offset[0]; mat[13] += offset[1]; mat[14] += offset[2]
        row = {c: tmpl.get(c, donor[c]) for c in donor}
        row.update(Guid=U(self.ns, 'monster', mid).bytes, _ID=donor['_ID'].rsplit('|', 1)[0] + '|' + mid, _Level=level, _Layers=donor['_Layers'],
                   Transform=struct.pack('<16f', *mat))
        m.game += [f"DELETE FROM _Instance_Monster WHERE Guid={lit(row['Guid'])};", insert('_Instance_Monster', row)]
        m.undo_game.insert(0, f"DELETE FROM _Instance_Monster WHERE Guid={lit(row['Guid'])};")
        m.text(f'lookat_{mid}', display)

    def spawn_template(self, nid, display, clone_template, **over):
        """A _Template_NPC for CreateEntity category="NPC" how="spawnAtEntity" (no instance). Gear via SetupStorage/SetupEquipment in `over`."""
        m = self.m
        tmpl = dict(m.s.execute('select * from _Template_NPC where Id=?', (clone_template,)).fetchone())
        tmpl.update(Id=nid, Name=nid, LookAtText=f'lookat_{nid}', StolenGoodsTable='', CanRob=0)
        for k, v in over.items():
            assert k in tmpl, (nid, k); tmpl[k] = v
        m.static += [f"DELETE FROM _Template_NPC WHERE Id={lit(nid)};", insert('_Template_NPC', tmpl)]
        m.undo_static.append(f"DELETE FROM _Template_NPC WHERE Id={lit(nid)};")
        m.text(f'lookat_{nid}', display)

    def stock(self, nid, typ, iid, n=1, lootable=0):
        """Item in the storage of an NPC made by npc(): merchant stock (lootable=0) or carried gear that drops (lootable=1,
        mirrored into the template's SetupStorage like vanilla)."""
        m = self.m
        guid, level = m._npc_rows[nid]
        t = next((t for ty, i, t in m.templates if i == iid), None) or self._template_row(typ, iid)
        icols = [c[1] for c in m.g.execute(f'pragma table_info(_Instance_{typ})')]
        row = {c: t.get(c) for c in icols}
        ig = U(self.ns, 'stock', nid, iid).bytes
        row.update(Guid=ig, _ID='', _Level=level, _Layers='', Transform=IDENT, StorageGUID=guid, Lootable=lootable)
        if 'StackCount' in row: row['StackCount'] = n
        m._npc_stock = getattr(m, '_npc_stock', {}); m._npc_stock[nid] = m._npc_stock.get(nid, 0) + 1
        # our own NPC row is recreated on every install, so the count is absolute, not incremental
        m.game += [insert(f'_Instance_{typ}', row, 'INSERT OR REPLACE'),
                   f"UPDATE _Instance_NPC SET StorageContentCount={m._npc_stock[nid]} WHERE Guid={lit(guid)};"]
        m.undo_game.insert(0, f"DELETE FROM _Instance_{typ} WHERE Guid={lit(ig)};")
        if lootable:
            entry = f"{typ}/{iid}{':' + str(n) if n > 1 else ''}/true/false;"
            m.static.append(f"UPDATE _Template_NPC SET SetupStorage=SetupStorage||{lit(entry)} WHERE Id={lit(nid)};")

    def _template_row(self, typ, iid):
        """Template of an item from an earlier module (armory_v2 / remastered) or vanilla: read from the installed-mod snapshot if given."""
        r = self.m.s.execute(f'select * from _Template_{typ} where Id=?', (iid,)).fetchone()
        if r: return dict(r)
        snap = getattr(self, 'templates_from', None)
        assert snap, (typ, iid, 'not in source DB; set Story.templates_from to a DB with the earlier modules installed')
        r = snap.execute(f'select * from _Template_{typ} where Id=?', (iid,)).fetchone()
        assert r, (typ, iid)
        return dict(r)

    def loot_table(self, name, entries, picks=0):
        """New loot table. entries: (Type, Id, chance%, amount, value) like vanilla ('Money/Geld/100/200/1/;' = 200 heller).
        picks 0 = every entry rolls on its own chance."""
        m = self.m
        content = ''.join(f'{t}/{i}/{c}/{n}/{v}/;' for t, i, c, n, v in entries)
        m.static += [f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(name)};",
                     insert('_DSA_LootTables', dict(LootTableName=name, LootTableValue=str(picks), LootTableContent=content))]
        m.undo_static.append(f"DELETE FROM _DSA_LootTables WHERE LootTableName={lit(name)};")
        return name
