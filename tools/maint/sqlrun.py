"""Run a module's SQL on a set of databases, like its Install.bat / Uninstall.bat (no Windows needed).

    python -I tools/maint/sqlrun.py <db folder> <mod folder> install|uninstall|verify

Uses tools/bin/sqlite3.exe on Windows (exactly what the installers use) and Python's sqlite3 elsewhere; the fallback writes the
same cp1252 bytes as the exe (non-ASCII literals become CAST(X'..' AS TEXT)). Only for COPIES of the game databases.
"""
import os, sqlite3, subprocess, sys

def _bytes_literals(data):
    """sqlite3.exe stores the cp1252 bytes of a literal as-is; Python's sqlite3 would re-encode them as UTF-8. Rewrite every
    literal with a byte > 127 as CAST(X'..' AS TEXT) so the Python fallback writes exactly the same bytes as the exe."""
    out, i, n = bytearray(), 0, len(data)
    while i < n:
        c = data[i]
        if c == 0x27:
            j = i + 1; lit = bytearray()
            while True:
                if data[j] == 0x27:
                    if j + 1 < n and data[j + 1] == 0x27: lit.append(0x27); j += 2; continue
                    break
                lit.append(data[j]); j += 1
            if any(b > 127 for b in lit): out += b"CAST(X'" + lit.hex().upper().encode() + b"' AS TEXT)"
            else: out += data[i:j + 1]
            i = j + 1
        elif c == 0x2d and data[i:i + 2] == b'--':
            j = data.find(b'\n', i); j = n if j < 0 else j
            out += data[i:j]; i = j
        else:
            out.append(c); i += 1
    return bytes(out)

def run_sql(db, script, exe=None):
    """Run a .sql file on a database like the installers do; returns the printed output (errors included as 'Error: ...')."""
    if exe and os.name == 'nt' and os.path.exists(exe):
        with open(script, 'rb') as f:
            r = subprocess.run([exe, db], stdin=f, capture_output=True)
        return r.stdout.decode('cp1252', 'replace') + r.stderr.decode('cp1252', 'replace')
    # fallback (Linux/macOS, or no sqlite3.exe): Python's sqlite3, one statement at a time like the shell, results printed
    data = _bytes_literals(open(script, 'rb').read()).decode('latin-1')
    con = sqlite3.connect(db, isolation_level=None); con.text_factory = lambda b: b.decode('cp1252', 'replace')
    out, buf = [], ''
    for ch in data:
        buf += ch
        if ch != ';' or not sqlite3.complete_statement(buf): continue
        st = '\n'.join(l for l in buf.strip().splitlines() if not l.lstrip().startswith('--')).strip(); buf = ''
        if not st or st == ';': continue
        try:
            if st.upper().startswith('PRAGMA INTEGRITY_CHECK'):
                out += [r[0] for r in con.execute('PRAGMA integrity_check')]; continue
            for r in con.execute(st):
                out.append('|'.join('' if v is None else str(v) for v in r))
        except sqlite3.Error as e:
            out.append(f'Error: {e} in: {st[:200]}')
    con.close()
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    dbdir, mod, cmd = sys.argv[1:4]
    exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'sqlite3.exe')
    prefix = {'install': '', 'uninstall': 'undo_', 'verify': 'verify_'}[cmd]
    for d in ('static', 'locale', 'game'):
        p = os.path.join(mod, 'sql', f'{prefix}{d}.sql')
        if os.path.exists(p):
            out = run_sql(os.path.join(dbdir, f'{d}.db4'), p, exe)
            print(f'== {prefix}{d}.sql'); print(out.strip()[-3000:] if cmd == 'verify' else '\n'.join(l for l in out.splitlines() if 'rror' in l) or 'ok')
