"""Gameplay Additions (mg979, v2.1b mild preset) as a module of the pack, plus the player's two pre-pack fixes that live in the
same baseline (the Witch Hat fix and the Ravenwing Saber).

    python -I tools/build_gameplay_additions.py <baseline dir> <mod dir>

The pack was built on top of mg979's mod; mg979 told the player to build on it and doesn't mind it being folded in (6 Nov).
This generates, from the difference between the truly vanilla databases (<game>/export/db_backup_original) and the baseline
(<game>/export/db/armory_backup), SQL that turns vanilla into the baseline:
  - changed rows: UPDATE of only the columns that differ (by the table's unique key), each value only where it still holds
    vanilla's value (so a rerun never undoes what a later module or another mg979 preset set),
  - new rows: INSERT OR IGNORE of the full row, removed rows: DELETE by key,
so it is a no-op on a game that already has mg979's mod and the pack installs on a clean game in one go.
Values are written exactly: text keeps its bytes (cp1252), reals are exact fractions (the bundled sqlite3.exe 3.6.1 misreads
17-digit decimals).
The mod's loose files (icons, the witch hat texture, the two character models that carry its skin, the cultist dagger
textures) are copied from the player's game into <mod dir>/loose and installed into <game>/export.
"""
import os, sys, sqlite3, shutil
GAME = os.environ.get('DRAKENSANG', r'D:/Steam/steamapps/common/Drakensang')
BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GAME, 'export', 'db', 'armory_backup')
OUT = sys.argv[2] if len(sys.argv) > 2 else 'mods/gameplay_additions'
VAN = os.environ.get('DRAKENSANG_VANILLA', os.path.join(GAME, 'export', 'db_backup_original'))
SQL = os.path.join(OUT, 'sql'); os.makedirs(SQL, exist_ok=True)

# mg979's loose files (all dated 2009-2010 in the player's export folder; the tree textures and the font there are not his)
LOOSE = ['textures/icons/' + f + '.dds' for f in ('armor_arme_lederschienen', 'ergo_dodge_amulet', 'ergo_druid_staff', 'ergo_elf_spear',
         'ergo_fencing_gloves', 'ergo_shadow_armor', 'ergo_silver_scimitar', 'ergo_small_sword', 'ergo_witch_hat', 'ergo_witch_robe',
         'ergo_wounding_dagger', 'weapon_drachenkultistendolch')] + \
        ['textures/armor/ergo_witch_hat_color.dds', 'textures/armor/beine_lederruestung_color.dds',
         'textures/weapons/drachenkultistendolch_bump.dds', 'textures/weapons/drachenkultistendolch_color.dds',
         'textures/weapons/drachenkultistendolch_spec.dds', 'gfxlib/characters/mensch_f.n2', 'gfxlib/characters/mensch_m.n2']


def lit(t, v):
    if v is None: return b'NULL'
    if t == 'integer': return str(v).encode()
    if t == 'real':   # the bundled sqlite3.exe rounds 17-digit decimals wrongly: write an exact fraction (integer / power of two)
        num, den = float(v).as_integer_ratio()
        if den == 1 or den > 2 ** 62 or abs(num) >= 2 ** 63: return repr(float(v)).encode()
        return f'(CAST({num} AS REAL)/{den})'.encode()
    if t == 'blob': return b"X'" + v.hex().encode() + b"'"
    return b"'" + v.replace(b"'", b"''") + b"'"


def guarded(col, old, new):
    """col = new, but only where it still holds the old value: a second run after the later modules (or a game with another
    mg979 preset) keeps whatever was changed since."""
    c = f'"{col}"'.encode()
    test = c + b' IS NULL' if old[1] is None else c + b' = ' + lit(*old)   # sqlite3.exe 3.6.1: IS only works with NULL
    return c + b' = CASE WHEN ' + test + b' THEN ' + lit(*new) + b' ELSE ' + c + b' END'


def rows(c, t, cols):
    sel = ', '.join(f'"{x}"' for x in cols) + ', ' + ', '.join(f'typeof("{x}")' for x in cols)
    out = []
    for r in c.execute(f'select {sel} from "{t}"'):
        n = len(cols)
        out.append(tuple((r[n + i].decode() if isinstance(r[n + i], bytes) else r[n + i], r[i]) for i in range(n)))
    return out


def key_col(c, t):
    for r in c.execute(f'pragma index_list("{t}")'):
        if r[2]:
            ic = [x[2] for x in c.execute(f'pragma index_info("{r[1].decode() if isinstance(r[1], bytes) else r[1]}")')]
            if len(ic) == 1: return ic[0].decode() if isinstance(ic[0], bytes) else ic[0]
    return None


stats, total = [], {'upd': 0, 'cells': 0, 'ins': 0, 'del': 0}
for db in ('static', 'game', 'locale'):
    v = sqlite3.connect(f'file:{VAN}/{db}.db4?mode=ro', uri=True); b = sqlite3.connect(f'file:{BASE}/{db}.db4?mode=ro', uri=True)
    v.text_factory = b.text_factory = bytes
    tabs = [r[0].decode() for r in b.execute("select name from sqlite_master where type='table' order by name")]
    do, undo, ver = [b'BEGIN;'], [b'BEGIN;'], []
    for t in tabs:
        cols = [r[1].decode() for r in b.execute(f'pragma table_info("{t}")')]
        assert cols == [r[1].decode() for r in v.execute(f'pragma table_info("{t}")')], f'{db}.{t}: columns differ'
        rv, rb = rows(v, t, cols), rows(b, t, cols)
        if sorted(rv, key=repr) == sorted(rb, key=repr): continue
        qt = f'"{t}"'.encode(); cl = b', '.join(f'"{x}"'.encode() for x in cols)
        k = key_col(b, t)
        if k is None:   # _Globals: one row, no key
            assert len(rv) == len(rb) == 1, f'{db}.{t}: no key and {len(rv)}/{len(rb)} rows'
            for (src, dst, lst) in ((rv[0], rb[0], do), (rb[0], rv[0], undo)):
                sets = [guarded(cols[i], src[i], dst[i]) for i in range(len(cols)) if src[i] != dst[i]]
                lst.append(b'UPDATE ' + qt + b' SET ' + b', '.join(sets) + b';')
            stats.append((db, t, 1, 0, 0)); total['upd'] += 1; continue
        ki = cols.index(k)
        mv = {r[ki][1]: r for r in rv}; mb = {r[ki][1]: r for r in rb}
        assert len(mv) == len(rv) and len(mb) == len(rb), f'{db}.{t}: duplicate keys'
        nu = ni = nd = 0
        for key in sorted(set(mv) & set(mb)):
            a, z = mv[key], mb[key]
            if a == z: continue
            diff = [i for i in range(len(cols)) if a[i] != z[i]]
            assert ki not in diff
            w = b' WHERE "' + k.encode() + b'" = ' + lit(*z[ki]) + b';'
            do.append(b'UPDATE ' + qt + b' SET ' + b', '.join(guarded(cols[i], a[i], z[i]) for i in diff) + w)
            undo.append(b'UPDATE ' + qt + b' SET ' + b', '.join(guarded(cols[i], z[i], a[i]) for i in diff) + w)
            nu += 1; total['cells'] += len(diff)
        for key in sorted(set(mb) - set(mv)):
            z = mb[key]
            do.append(b'INSERT OR IGNORE INTO ' + qt + b' (' + cl + b') VALUES (' + b', '.join(lit(*x) for x in z) + b');')
            undo.append(b'DELETE FROM ' + qt + b' WHERE "' + k.encode() + b'" = ' + lit(*z[ki]) + b';')
            ni += 1
        for key in sorted(set(mv) - set(mb)):
            a = mv[key]
            do.append(b'DELETE FROM ' + qt + b' WHERE "' + k.encode() + b'" = ' + lit(*a[ki]) + b';')
            undo.append(b'INSERT OR IGNORE INTO ' + qt + b' (' + cl + b') VALUES (' + b', '.join(lit(*x) for x in a) + b');')
            nd += 1
        if ni:
            ver.append(f"SELECT 'Gameplay Additions: {t} rows added (expect {ni}): ' || count(*) FROM {qt.decode()} WHERE \"{k}\" IN (".encode()
                       + b', '.join(lit(*mb[x][ki]) for x in sorted(set(mb) - set(mv))) + b');')
        if nd:
            ver.append(f"SELECT 'Gameplay Additions: {t} rows removed (expect 0): ' || count(*) FROM {qt.decode()} WHERE \"{k}\" IN (".encode()
                       + b', '.join(lit(*mv[x][ki]) for x in sorted(set(mv) - set(mb))) + b');')
        stats.append((db, t, nu, ni, nd)); total['upd'] += nu; total['ins'] += ni; total['del'] += nd
    ver.append(f"SELECT '{db}: integrity check'; PRAGMA integrity_check;".encode())
    for name, lines in ((f'{db}.sql', do), (f'undo_{db}.sql', undo)):
        with open(os.path.join(SQL, name), 'wb') as f: f.write(b'\n'.join(lines + [b'COMMIT;']) + b'\n')
    with open(os.path.join(SQL, f'verify_{db}.sql'), 'wb') as f: f.write(b'\n'.join(ver) + b'\n')

# loose files
LD = os.path.join(OUT, 'loose')
if os.path.isdir(LD): shutil.rmtree(LD)
for rel in LOOSE:
    src = os.path.join(GAME, 'export', *rel.split('/'))
    dst = os.path.join(LD, *rel.split('/')); os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
with open(os.path.join(OUT, 'loose_files.txt'), 'w', encoding='ascii', newline='\r\n') as f:
    f.write('\n'.join(r.replace('/', '\\') for r in LOOSE) + '\n')

for db, t, nu, ni, nd in stats: print(f'  {db:7} {t:34} changed {nu:5}  added {ni:4}  removed {nd:4}')
print(f"Gameplay Additions: {total['upd']} rows changed ({total['cells']} values), {total['ins']} added, {total['del']} removed, {len(LOOSE)} loose files")
