"""Read Radon Labs' Excel-2003 XML tables (data/tables/*.xml, data/tables/db/*.xml).

Usage:
  python xltable.py <file.xml>                      list worksheets, columns, row counts
  python xltable.py <file.xml> <sheet> [N]          print the first N rows (default 20) as TSV
  python xltable.py <file.xml> <sheet> all > x.tsv  dump a whole sheet

Notes
  * The first row of each sheet is the header (attribute names); Radon's tools treat rows/cols whose
    header starts with '#' or is empty as comments.
  * Handles ss:Index (sparse cells) and ss:MergeAcross.  stdlib only.
"""
import sys
import xml.etree.ElementTree as ET

NS = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}
SS = '{urn:schemas-microsoft-com:office:spreadsheet}'


def sheets(path):
    root = ET.parse(path).getroot()
    out = {}
    for ws in root.findall('ss:Worksheet', NS):
        name = ws.get(SS + 'Name')
        rows = []
        for row in ws.findall('ss:Table/ss:Row', NS):
            vals = []
            for cell in row.findall('ss:Cell', NS):
                idx = cell.get(SS + 'Index')
                if idx:
                    while len(vals) < int(idx) - 1:
                        vals.append('')
                data = cell.find('ss:Data', NS)
                vals.append(''.join(data.itertext()) if data is not None else '')
                for _ in range(int(cell.get(SS + 'MergeAcross', 0))):
                    vals.append('')
            rows.append(vals)
        out[name] = rows
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    data = sheets(argv[1])
    if len(argv) == 2:
        for name, rows in data.items():
            hdr = [h for h in (rows[0] if rows else []) if h]
            print(f'[{name}] {max(len(rows) - 1, 0)} rows, {len(hdr)} cols: {", ".join(hdr)}')
        return 0
    rows = data[argv[2]]
    n = len(rows) if len(argv) > 3 and argv[3] == 'all' else int(argv[3]) if len(argv) > 3 else 20
    for r in rows[:n + 1]:
        print('\t'.join(c.replace('\t', ' ').replace('\n', '\\n') for c in r))
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv))
