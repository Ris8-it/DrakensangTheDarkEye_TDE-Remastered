"""Layers 14 and 17: patch the game's runtime XML tables as LOOSE files (never shipped: built from the player's own archives).

The engine reads data/tables/*.xml (effects, sound, xp, materials, blueprints ...) at runtime from the .npk archives; a file
under export/ with the same path should win over the archive copy (proven for textures/icons, **to be tested** for data/).
This repository must not contain game files, so a module ships only a small patch spec; the patched file is produced on the
player's machine from their own archives:

  * Python:      python -I tools/loosefiles.py apply  <spec.json> "<game folder>"      (writes export/data/tables/...)
                 python -I tools/loosefiles.py remove <spec.json> "<game folder>"
  * no Python:   the module's LooseFiles_Install.bat / LooseFiles_Uninstall.bat call loosefiles.ps1 (same logic, PowerShell 2+)
  * modders:     python -I tools/loosefiles.py ps1 <spec.json> <out.ps1>   regenerates the PowerShell script with the spec inside

Spec (JSON list of patches):
  {"file": "data/tables/effects.xml", "sheet": "Tabelle1", "rows": [["MyEffect", "effects/balsam", 15, 0, "comment"]]}
      append rows to a worksheet (strings/numbers typed automatically; ExpandedRowCount is raised to match)
  {"file": "data/tables/blueprints.xml", "properties": {"MonsterLarge": ["HealthBarGraphicsProperty"]},
   "entities": {"MyShrine": ["TransformableProperty", "GraphicsProperty", ...]}}
      add <Property> lines before the last property of an entity type (LevelSwitchableProperty must stay last), add entity types
Every patched file carries the marker comment <!-- TDE-Remastered loosefiles: <id> --> so remove only deletes our own files.
"""
import json, os, re, struct, sys

ARCHIVES = ['patch1.npk', 'export.npk', 'export_1.npk', 'export_2.npk', 'export_3.npk']   # first hit wins (patch1 overrides)
MARK = '<!-- TDE-Remastered loosefiles: {} -->'


def npk_find(game, rel):
    """Return the bytes of export/<rel> from the archives (patch1.npk first)."""
    want = ('export/' + rel).lower()
    for a in ARCHIVES:
        p = os.path.join(game, a)
        if not os.path.exists(p):
            continue
        with open(p, 'rb') as f:
            magic, _blen, dataoff = struct.unpack('<4sII', f.read(12))
            assert magic == b'0KPN', magic
            stack = []
            while True:
                tag, _ln = struct.unpack('<4sI', f.read(8))
                if tag == b'_RID':
                    n = struct.unpack('<H', f.read(2))[0]; stack.append(f.read(n).decode('latin1'))
                elif tag == b'ELIF':
                    off, size, n = struct.unpack('<IIH', f.read(10)); name = f.read(n).decode('latin1')
                    if '/'.join(stack + [name]).lower() == want:
                        f.seek(dataoff + 8 + off); return f.read(size)
                elif tag == b'DNED':
                    stack.pop()
                    if not stack: break
                else:
                    raise ValueError(tag)
    raise FileNotFoundError(rel)


def cell(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f'<Cell><Data ss:Type="Number">{v}</Data></Cell>'
    s = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'<Cell><Data ss:Type="String">{s}</Data></Cell>' if s else '<Cell/>'


def patch_text(text, patch, pid):
    if 'rows' in patch:
        m = re.search(r'<Worksheet ss:Name="' + re.escape(patch['sheet']) + r'">', text)
        assert m, patch['sheet']
        t0 = text.index('<Table', m.end()); t1 = text.index('</Table>', t0)
        head_end = text.index('>', t0) + 1
        head = text[t0:head_end]
        n = len(patch['rows'])
        head2 = re.sub(r'ss:ExpandedRowCount="(\d+)"', lambda x: f'ss:ExpandedRowCount="{int(x.group(1)) + n}"', head)
        rows = ''.join('   <Row>' + ''.join(cell(v) for v in r) + '</Row>\n' for r in patch['rows'])
        text = text[:t0] + head2 + text[head_end:t1] + rows + text[t1:]
    for etype, props in patch.get('properties', {}).items():
        m = re.search(r'<Entity type="' + re.escape(etype) + r'"[^>]*>(.*?)</Entity>', text, re.S)
        assert m, etype
        body = m.group(1)
        for p in props:
            assert f'<Property type="{p}"/>' not in body, (etype, p)
        lines = ''.join(f'        <Property type="{p}"/>\n' for p in props)
        last = body.rfind('<Property type="LevelSwitchableProperty"/>')   # must stay the last property
        pos = m.start(1) + body.rfind('\n', 0, last) + 1 if last >= 0 else m.end(1)
        text = text[:pos] + lines + text[pos:]
    for etype, props in patch.get('entities', {}).items():
        assert f'<Entity type="{etype}"' not in text, etype
        block = f'    <Entity type="{etype}" cppclass="Entity">\n' + ''.join(f'        <Property type="{p}"/>\n' for p in props) + '    </Entity>\n'
        i = text.rindex('</BluePrints>')
        text = text[:i] + block + text[i:]
    if MARK.format(pid) not in text:
        i = text.index('?>') + 2 if text.startswith('<?xml') else 0
        text = text[:i] + '\n' + MARK.format(pid) + text[i:]
    return text


def group(spec):
    files = {}
    for p in spec['patches']:
        files.setdefault(p['file'], []).append(p)
    return files


def apply(spec, game):
    for rel, patches in group(spec).items():
        raw = npk_find(game, rel)
        text = raw.decode('cp1252')
        for p in patches:
            text = patch_text(text, p, spec['id'])
        out = os.path.join(game, 'export', *rel.split('/'))
        if os.path.exists(out):
            old = open(out, encoding='cp1252', errors='replace').read()
            if MARK.format(spec['id']) not in old:
                raise SystemExit(f'{out} exists and is not ours: not overwritten')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='cp1252', newline='') as f:
            f.write(text)
        print('written', out)


def remove(spec, game):
    for rel in group(spec):
        out = os.path.join(game, 'export', *rel.split('/'))
        if os.path.exists(out) and MARK.format(spec['id']) in open(out, encoding='cp1252', errors='replace').read():
            os.remove(out); print('removed', out)


PS1 = r'''# Generated by tools/loosefiles.py: builds/removes loose data files from the game's own .npk archives. PowerShell 2+.
param([string]$Game = $env:DRAKENSANG, [switch]$Remove)
$ErrorActionPreference = 'Stop'
if (-not $Game) { $Game = 'D:\Steam\steamapps\common\Drakensang' }
$Spec = @'
__SPEC__
'@
$Mark = '<!-- TDE-Remastered loosefiles: __ID__ -->'
$enc = [System.Text.Encoding]::GetEncoding(1252)
function Find-InNpk([string]$rel) {
  $want = ('export/' + $rel).ToLower()
  foreach ($a in @('patch1.npk','export.npk','export_1.npk','export_2.npk','export_3.npk')) {
    $p = Join-Path $Game $a
    if (-not (Test-Path $p)) { continue }
    $fs = [System.IO.File]::OpenRead($p); $br = New-Object System.IO.BinaryReader($fs)
    try {
      $magic = $enc.GetString($br.ReadBytes(4)); $null = $br.ReadUInt32(); $dataoff = $br.ReadUInt32()
      if ($magic -ne '0KPN') { throw "bad npk $p" }
      $stack = New-Object System.Collections.ArrayList
      while ($true) {
        $tag = $enc.GetString($br.ReadBytes(4)); $null = $br.ReadUInt32()
        if ($tag -eq '_RID') { $n = $br.ReadUInt16(); [void]$stack.Add($enc.GetString($br.ReadBytes($n))) }
        elseif ($tag -eq 'ELIF') {
          $off = $br.ReadUInt32(); $size = $br.ReadUInt32(); $n = $br.ReadUInt16(); $name = $enc.GetString($br.ReadBytes($n))
          if ((($stack -join '/') + '/' + $name).ToLower() -eq $want) { $fs.Seek($dataoff + 8 + $off, 'Begin') | Out-Null; return $enc.GetString($br.ReadBytes($size)) }
        }
        elseif ($tag -eq 'DNED') { $stack.RemoveAt($stack.Count - 1); if ($stack.Count -eq 0) { break } }
        else { throw "bad tag $tag" }
      }
    } finally { $br.Close() }
  }
  throw "not found in archives: $rel"
}
function Esc([string]$s) { $s.Replace('&','&amp;').Replace('<','&lt;').Replace('>','&gt;') }
function Cell($v) {
  if ($v -is [int] -or $v -is [double] -or $v -is [decimal]) { return '<Cell><Data ss:Type="Number">' + $v + '</Data></Cell>' }
  if ("$v" -eq '') { return '<Cell/>' }
  return '<Cell><Data ss:Type="String">' + (Esc "$v") + '</Data></Cell>'
}
$patches = __PATCHES_PS__
$files = @{}
foreach ($p in $patches) { if (-not $files.ContainsKey($p.file)) { $files[$p.file] = @() }; $files[$p.file] += ,$p }
foreach ($rel in $files.Keys) {
  $out = Join-Path (Join-Path $Game 'export') ($rel -replace '/', '\')
  if ($Remove) {
    if ((Test-Path $out) -and ([System.IO.File]::ReadAllText($out, $enc).Contains($Mark))) { Remove-Item $out; Write-Host "removed $out" }
    continue
  }
  $text = Find-InNpk $rel
  foreach ($p in $files[$rel]) {
    if ($p.rows) {
      $ws = $text.IndexOf('<Worksheet ss:Name="' + $p.sheet + '">'); if ($ws -lt 0) { throw "sheet $($p.sheet)" }
      $t0 = $text.IndexOf('<Table', $ws); $t1 = $text.IndexOf('</Table>', $t0); $he = $text.IndexOf('>', $t0) + 1
      $head = $text.Substring($t0, $he - $t0); $n = $p.rows.Count
      $head2 = [regex]::Replace($head, 'ss:ExpandedRowCount="(\d+)"', { param($m) 'ss:ExpandedRowCount="' + ([int]$m.Groups[1].Value + $n) + '"' })
      $rows = ''
      foreach ($r in $p.rows) { $rows += '   <Row>' + (($r | ForEach-Object { Cell $_ }) -join '') + "</Row>`r`n" }
      $text = $text.Substring(0, $t0) + $head2 + $text.Substring($he, $t1 - $he) + $rows + $text.Substring($t1)
    }
    if ($p.properties) {
      foreach ($et in $p.properties.Keys) {
        $m = [regex]::Match($text, '<Entity type="' + [regex]::Escape($et) + '"[^>]*>', 'Singleline'); if (-not $m.Success) { throw "entity $et" }
        $end = $text.IndexOf('</Entity>', $m.Index); $body = $text.Substring($m.Index, $end - $m.Index)
        $lines = ''; foreach ($pp in $p.properties[$et]) { $lines += '        <Property type="' + $pp + '"/>' + "`r`n" }
        $last = $body.LastIndexOf('<Property type="LevelSwitchableProperty"/>')
        if ($last -ge 0) { $pos = $m.Index + $body.LastIndexOf("`n", $last) + 1 } else { $pos = $end }
        $text = $text.Substring(0, $pos) + $lines + $text.Substring($pos)
      }
    }
    if ($p.entities) {
      foreach ($et in $p.entities.Keys) {
        $block = '    <Entity type="' + $et + '" cppclass="Entity">' + "`r`n"
        foreach ($pp in $p.entities[$et]) { $block += '        <Property type="' + $pp + '"/>' + "`r`n" }
        $block += "    </Entity>`r`n"; $i = $text.LastIndexOf('</BluePrints>'); $text = $text.Substring(0, $i) + $block + $text.Substring($i)
      }
    }
  }
  if (-not $text.Contains($Mark)) { if ($text.StartsWith('<?xml')) { $i = $text.IndexOf('?>') + 2 } else { $i = 0 }; $text = $text.Substring(0, $i) + "`r`n" + $Mark + $text.Substring($i) }
  if ((Test-Path $out) -and -not ([System.IO.File]::ReadAllText($out, $enc).Contains($Mark))) { throw "$out exists and is not ours" }
  New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
  [System.IO.File]::WriteAllText($out, $text, $enc); Write-Host "written $out"
}
'''


def ps_value(v):
    if isinstance(v, dict):
        return '@{' + '; '.join(f"'{k}' = {ps_value(x)}" for k, x in v.items()) + '}'
    if isinstance(v, list):
        return '@(' + ', '.join((',' if isinstance(x, list) else '') + ps_value(x) for x in v) + ')'
    if isinstance(v, bool):
        return '$true' if v else '$false'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def ps1(spec):
    return PS1.replace('__SPEC__', json.dumps(spec, indent=1)).replace('__ID__', spec['id']).replace('__PATCHES_PS__', ps_value(spec['patches']))


def write_module_files(spec, out):
    """Write <out>/loosefiles.json, loosefiles.ps1 and the two .bat wrappers (CRLF)."""
    with open(os.path.join(out, 'loosefiles.json'), 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=1)
    with open(os.path.join(out, 'loosefiles.ps1'), 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(ps1(spec))
    import shutil
    shutil.copy(os.path.abspath(__file__), os.path.join(out, 'loosefiles.py'))
    for name, flag, cmd, what in (('LooseFiles_Install.bat', '', 'apply', 'Builds'), ('LooseFiles_Uninstall.bat', ' -Remove', 'remove', 'Removes')):
        with open(os.path.join(out, name), 'w', encoding='ascii', newline='\r\n') as f:
            f.write(f'@echo off\n:: {what} the loose data files of this module from your own game archives (nothing from the game is shipped).\n'
                    ':: Uses Python if installed (tested path), otherwise Windows PowerShell (same logic, loosefiles.ps1).\n'
                    'if not defined DRAKENSANG set "DRAKENSANG=D:\\Steam\\steamapps\\common\\Drakensang"\n'
                    'where py >nul 2>nul && ( py -3 -I "%~dp0loosefiles.py" ' + cmd + ' "%~dp0loosefiles.json" "%DRAKENSANG%" & goto end )\n'
                    'where python >nul 2>nul && ( python -I "%~dp0loosefiles.py" ' + cmd + ' "%~dp0loosefiles.json" "%DRAKENSANG%" & goto end )\n'
                    f'"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0loosefiles.ps1" -Game "%DRAKENSANG%"{flag}\n'
                    ':end\nif /i not "%~1"=="nopause" pause\n')


if __name__ == '__main__':
    cmd, spec_path = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path, encoding='utf-8'))
    if cmd == 'apply': apply(spec, sys.argv[3])
    elif cmd == 'remove': remove(spec, sys.argv[3])
    elif cmd == 'ps1': open(sys.argv[3], 'w', encoding='utf-8-sig', newline='\r\n').write(ps1(spec))
    else: print(__doc__)
