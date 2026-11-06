"""Show what a save game holds compared to the vanilla world database.

A Drakensang save (`*.dsa`) and the profile's live `game.db4` are SQLite copies of export/db/game.db4 that
the engine has written back into (Mangalore DbServer::CreateSaveGame copies the file). This tool lists:
  * tables that exist only in the save (created at runtime, e.g. _PartyReceipes) or only in vanilla
  * columns added at runtime (dynamic attributes committed by the engine)
  * per-table row counts, vanilla vs save, and rows added/removed (by Guid where the table has one)
  * per-level instance counts (_Level), the current level and the story state tables in summary
  * typed-column problems: BLOB stored in a TEXT column (see ENGINE_REFERENCE §12)

Usage:  python save_diff.py <vanilla game.db4> <save .dsa or profile game.db4> [--rows TABLE]
        --rows TABLE  also print the Guid/_ID/_Level of rows added to TABLE
Read-only. stdlib only.
"""
import pathlib
import sqlite3
import sys


def connect(path):
    c = sqlite3.connect(pathlib.Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    c.text_factory = bytes
    return c


def tables(c):
    return {r[0].decode() for r in c.execute("select name from sqlite_master where type='table'")}


def columns(c, t):
    return [(r[1].decode(), (r[2] or b'').decode()) for r in c.execute(f'pragma table_info("{t}")')]


def dec(b):
    return b.decode('cp1252', 'replace') if isinstance(b, bytes) else b


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    van, sav = connect(argv[1]), connect(argv[2])
    show_rows = argv[argv.index('--rows') + 1] if '--rows' in argv else None
    tv, ts = tables(van), tables(sav)
    print('== tables only in save   :', sorted(ts - tv) or '-')
    print('== tables only in vanilla:', sorted(tv - ts) or '-')

    print('\n== row counts (changed tables only)')
    print(f'{"table":40s} {"vanilla":>8s} {"save":>8s} {"added":>6s} {"gone":>6s}  new columns')
    listing = []
    for t in sorted(tv & ts):
        cv, cs = columns(van, t), columns(sav, t)
        newcols = [n for n, _ in cs if n not in {m for m, _ in cv}]
        nv = van.execute(f'select count(*) from "{t}"').fetchone()[0]
        ns = sav.execute(f'select count(*) from "{t}"').fetchone()[0]
        added = gone = ''
        names = [n for n, _ in cs]
        if 'Guid' in names and 'Guid' in [n for n, _ in cv]:
            gv = {r[0] for r in van.execute(f'select Guid from "{t}"')}
            gs = {r[0] for r in sav.execute(f'select Guid from "{t}"')}
            added, gone = len(gs - gv), len(gv - gs)
            if show_rows == t:
                for row in sav.execute(f'select Guid, _ID, _Level from "{t}"'):
                    if row[0] in gs - gv:
                        listing.append(f'   + {row[0].hex()} {dec(row[1])} {dec(row[2])}')
        if nv != ns or newcols or added or gone:
            print(f'{t:40s} {nv:8d} {ns:8d} {added!s:>6s} {gone!s:>6s}  {", ".join(newcols)}')

    for line in listing:
        print(line)
    for t in sorted(ts - tv):
        n = sav.execute(f'select count(*) from "{t}"').fetchone()[0]
        print(f'{t:40s} {"-":>8s} {n:8d}  (runtime table) columns: {", ".join(c for c, _ in columns(sav, t))}')

    print('\n== typed-column check (BLOB in TEXT columns)')
    bad = 0
    for t in sorted(ts):
        for name, typ in columns(sav, t):
            if typ.upper() == 'TEXT':
                n = sav.execute(f'select count(*) from "{t}" where typeof("{name}")=\'blob\'').fetchone()[0]
                if n:
                    bad += 1
                    print(f'   {t}.{name}: {n} blob value(s)')
    print('   ok' if not bad else f'   {bad} column(s) with blobs')

    print('\n== instances per level (save)')
    per = {}
    for t in sorted(ts):
        if t.startswith('_Instance_') and '_Level' in [n for n, _ in columns(sav, t)]:
            for lvl, n in sav.execute(f'select _Level, count(*) from "{t}" group by _Level'):
                per[dec(lvl)] = per.get(dec(lvl), 0) + n
    for lvl in sorted(per, key=lambda x: (x or '')):
        print(f'   {lvl or "(none)":45s} {per[lvl]}')

    print('\n== story state (save)')
    if '_Story_Tasks' in ts:
        for state, n in sav.execute('select TaskState, count(*) from _Story_Tasks group by TaskState'):
            print(f'   tasks {dec(state):10s} {n}')
    if '_Story_Dialogs' in ts:
        n = sav.execute('select count(*) from _Story_Dialogs where DialogLocked != 0').fetchone()[0]
        print(f'   locked dialogs {n}')
    if '_Story_DialogTakeStatus' in ts:
        n = sav.execute('select count(*) from _Story_DialogTakeStatus where TakeStatus != 0').fetchone()[0]
        print(f'   takes already said {n}')
    if '_Globals' in ts:
        cur = sav.execute('select * from _Globals')
        names = [d[0] for d in cur.description]
        row = cur.fetchone()
        if row:
            g = dict(zip(names, row))
            for k in ('CurrentLevel', 'WorldMapStartLocation', 'WorldMapTargetLocation', 'XpMultiplicator', 'LevelCap'):
                if k in g:
                    print(f'   _Globals.{k} = {dec(g[k])}')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv))
