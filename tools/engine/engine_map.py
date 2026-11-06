"""Map entities -> properties -> attributes from blueprints.xml and the databases.

Produces two generated glossaries:
  properties.md   every property class in blueprints.xml: which entity types use it, and the attributes
                  (db columns) most likely owned by it (inferred, see below)
  attributes.md   every attribute in _Attributes: type, read/write, dynamic flag, which categories carry
                  it, value examples and the inferred owning property
and prints a consistency report (categories without blueprint, blueprints without category, ...).

Ownership inference: an attribute is assigned to the property whose set of entity types is the smallest
superset of the set of categories that carry the attribute as a column.  It is a heuristic (several
properties often share the same entity set), so the result is labelled "inferred".

Usage:  python engine_map.py <db_dir> <blueprints.xml> <out_dir>
stdlib only, read-only on the databases.
"""
import collections
import os
import pathlib
import sqlite3
import sys
import xml.etree.ElementTree as ET

# blueprint type -> category name, where the two differ
BP_TO_CAT = {'Light': 'Light', 'MonsterLarge': 'MonsterLarge'}


def connect(path):
    c = sqlite3.connect(pathlib.Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    c.text_factory = lambda b: b.decode('cp1252', 'replace')
    return c


def cols(con, table):
    return [r[1] for r in con.execute(f'pragma table_info("{table}")')]


def load(db_dir, bp_path):
    s = connect(os.path.join(db_dir, 'static.db4'))
    g = connect(os.path.join(db_dir, 'game.db4'))
    bps = collections.OrderedDict()
    for e in ET.parse(bp_path).getroot():
        if e.tag == 'Entity':
            bps[e.get('type')] = [p.get('type') for p in e if p.tag == 'Property']
    cats = {}
    for name, virt, spec, tt, it in s.execute('select * from _Categories'):
        cats[name] = dict(virtual=virt, special=spec, template=tt, instance=it)
    attrs = {}
    for n, t, rw, dyn in s.execute('select * from _Attributes'):
        attrs[n] = dict(type=t, rw=rw, dyn=dyn)
    cat_cols = {}
    rows = {}
    for name, c in cats.items():
        cc = set()
        if c['template'] and s.execute("select 1 from sqlite_master where name=?", (c['template'],)).fetchone():
            cc |= set(cols(s, c['template']))
            rows[(name, 'T')] = s.execute(f'select count(*) from "{c["template"]}"').fetchone()[0]
        if c['instance'] and g.execute("select 1 from sqlite_master where name=?", (c['instance'],)).fetchone():
            cc |= set(cols(g, c['instance']))
            rows[(name, 'I')] = g.execute(f'select count(*) from "{c["instance"]}"').fetchone()[0]
        cat_cols[name] = cc
    return s, g, bps, cats, attrs, cat_cols, rows


def examples(s, g, cats, attr, limit=3):
    seen = []
    for name, c in cats.items():
        for con, tbl in ((s, c['template']), (g, c['instance'])):
            if not tbl:
                continue
            try:
                if attr not in cols(con, tbl):
                    continue
                q = f'select distinct "{attr}" from "{tbl}" where "{attr}" is not null and "{attr}" != \'\' limit 6'
                for (v,) in con.execute(q):
                    if isinstance(v, bytes):
                        v = '0x' + v[:8].hex() + ('…' if len(v) > 8 else '')
                    v = str(v).replace('|', '/').replace('\n', ' ')
                    if len(v) > 40:
                        v = v[:40] + '…'
                    if v not in seen:
                        seen.append(v)
                    if len(seen) >= limit:
                        return seen
            except sqlite3.OperationalError:
                pass
    return seen


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 1
    db_dir, bp_path, out = argv[1], argv[2], argv[3]
    os.makedirs(out, exist_ok=True)
    s, g, bps, cats, attrs, cat_cols, rows = load(db_dir, bp_path)

    # ---- consistency report ----
    print('== consistency')
    inst_cats = {n for n, c in cats.items() if c['instance']}
    print('categories with instances but no blueprint:', sorted(n for n in inst_cats if n not in bps))
    print('blueprints with no category:', sorted(b for b in bps if b not in cats))
    print('virtual categories (template only):', sorted(n for n, c in cats.items() if c['virtual']))
    print('special categories:', sorted(n for n, c in cats.items() if c['special']))
    empty = sorted(b for b, p in bps.items() if not p)
    print('blueprints with no property:', empty)

    # ---- property -> entity types ----
    prop_types = collections.OrderedDict()
    for bp, props in bps.items():
        for p in props:
            prop_types.setdefault(p, []).append(bp)

    # ---- attribute -> categories carrying it (only categories that have a blueprint) ----
    attr_cats = collections.defaultdict(set)
    for cat, cc in cat_cols.items():
        if cat in bps:
            for a in cc:
                attr_cats[a].add(cat)
    # group properties by identical entity-type sets; an attribute belongs to the group whose set is the
    # smallest superset of the categories carrying it
    groups = collections.OrderedDict()
    for p, types in prop_types.items():
        groups.setdefault(frozenset(types), []).append(p)
    owner = {}
    for a, cs in attr_cats.items():
        best = None
        for ts in groups:
            if cs <= ts and (best is None or len(ts) < len(best)):
                best = ts
        owner[a] = best
    by_group = collections.defaultdict(list)
    for a, ts in owner.items():
        by_group[ts].append(a)

    def label(ts):
        if ts is None:
            return ''
        ps = groups[ts]
        return ps[0] if len(ps) == 1 else '{' + ', '.join(ps[:3]) + (f' +{len(ps) - 3}' if len(ps) > 3 else '') + '}'

    # ---- properties.md ----
    lines = ['# Property glossary (generated by tools/engine/engine_map.py)', '',
             'Every property class named in `data/tables/blueprints.xml`, grouped by the exact set of entity types that',
             'carry it. Under each group: the db columns (attributes) **inferred** to belong to that group, i.e. columns',
             'whose set of categories is covered most tightly by this group\'s entity set. When a group holds several',
             'properties the data alone cannot say which one reads the column; the README gives the hand-checked meaning',
             'of the important ones.', '',
             f'{len(prop_types)} property classes in {len(groups)} entity-set groups, {len(bps)} entity types.', '',
             '## Index', '']
    for p, types in sorted(prop_types.items()):
        lines.append(f'- `{p}`: ' + ', '.join(types))
    lines.append('')
    for ts, ps in sorted(groups.items(), key=lambda x: (len(x[0]), sorted(x[0]))):
        lines.append('## ' + ', '.join(sorted(ts)))
        lines.append('')
        lines.append('- properties: ' + ', '.join(f'`{p}`' for p in ps))
        own = sorted(by_group.get(ts, []), key=str.lower)
        if own:
            lines.append(f'- inferred attributes ({len(own)}): ' + ', '.join(f'`{a}`' for a in own))
        lines.append('')
    unowned = sorted((a for a, ts in owner.items() if ts is None), key=str.lower)
    lines += ['## Columns with no covering property group', '',
              'Columns spread over categories that share no property (bookkeeping columns such as `Guid`/`_Level`, or',
              'attributes read by managers rather than properties):', '',
              ', '.join(f'`{a}`' for a in unowned), '']
    with open(os.path.join(out, 'properties.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    # ---- attributes.md ----
    lines = ['# Attribute glossary (generated by tools/engine/engine_map.py)', '',
             'All rows of `_Attributes` (identical in static.db4 and game.db4). `rw` = AttrReadWrite, `dyn` = AttrDynamic',
             '(1 = registered from the database at start-up rather than compiled into the exe: **inferred** from the',
             'Mangalore attribute system). "categories" = entity categories whose template/instance table has the column;',
             '"owner" = inferred property (see properties.md).', '',
             '| attribute | type | rw | dyn | categories | owner (inferred) | examples |', '|---|---|---|---|---|---|---|']
    for a in sorted(attrs, key=str.lower):
        info = attrs[a]
        cs = sorted(c for c, cc in cat_cols.items() if a in cc)
        cs_txt = ', '.join(cs) if len(cs) <= 6 else ', '.join(cs[:6]) + f' +{len(cs) - 6}'
        ex = '; '.join(examples(s, g, cats, a)) if cs else ''
        lines.append(f'| `{a}` | {info["type"]} | {info["rw"]} | {info["dyn"]} | {cs_txt} | {label(owner.get(a))} | {ex} |')
    with open(os.path.join(out, 'attributes.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')

    # ---- entity table summary to stdout ----
    print('\n== entity types')
    for bp, props in bps.items():
        c = cats.get(bp, {})
        print(f'{bp:22s} props={len(props):2d} templates={rows.get((bp, "T"), "-")!s:>5} '
              f'instances={rows.get((bp, "I"), "-")!s:>5} cols={len(cat_cols.get(bp, ()))}')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv))
