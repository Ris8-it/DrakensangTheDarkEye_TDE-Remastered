"""Read-only Nebula2 .npk reader. Usage: python -I npk.py <archive.npk> list <substring> | extract <substring> <outdir>"""
import struct, sys, os
def toc(path):
    f = open(path, 'rb'); magic, blen, dataoff = struct.unpack('<4sII', f.read(12))
    assert magic == b'0KPN', magic
    stack, out = [], []
    while True:
        tag, ln = struct.unpack('<4sI', f.read(8))
        if tag == b'_RID':
            n = struct.unpack('<H', f.read(2))[0]; stack.append(f.read(n).decode('latin1'))
        elif tag == b'ELIF':
            off, size, n = struct.unpack('<IIH', f.read(10)); name = f.read(n).decode('latin1')
            out.append(('/'.join(stack + [name]), off, size))
        elif tag == b'DNED':
            stack.pop()
            if not stack: break
        else:
            raise ValueError(tag)
    return dataoff, out
if __name__ == '__main__':
    path, cmd, sub = sys.argv[1:4]
    dataoff, files = toc(path)
    hits = [x for x in files if sub.lower() in x[0].lower()]
    if cmd == 'list':
        print(len(files), 'files,', len(hits), 'match'); [print(n, s) for n, o, s in hits[:40]]
    else:
        outdir = sys.argv[4]; os.makedirs(outdir, exist_ok=True)
        with open(path, 'rb') as f:
            for n, o, s in hits:
                f.seek(dataoff + 8 + o); data = f.read(s)
                with open(os.path.join(outdir, os.path.basename(n)), 'wb') as g: g.write(data)
        print('extracted', len(hits))
