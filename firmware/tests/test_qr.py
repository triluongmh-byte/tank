"""Independent QR read-back: format BCH, unmask, zigzag codewords, Reed-Solomon syndromes, payload."""
import pathlib, subprocess, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
BIN = ROOT / 'build/firmware/tests/qr_dump'
def build():
    src = ROOT / 'firmware/tests/qr_dump.cpp'
    BIN.parent.mkdir(parents=True, exist_ok=True)
    if not BIN.exists() or BIN.stat().st_mtime < max(src.stat().st_mtime, (ROOT/'firmware/tank/qr.h').stat().st_mtime):
        subprocess.run(['clang++', '-std=c++17', '-I', str(ROOT/'firmware/tank'), str(src), '-o', str(BIN)], check=True)
def dump(text):
    out = subprocess.run([str(BIN), text], check=True, capture_output=True, text=True).stdout.split('\n')
    size = int(out[0].split()[0]); return size, [[c == '1' for c in row] for row in out[1:1+size]]
EXP = [0]*512; LOG = [0]*256
x = 1
for i in range(255):
    EXP[i] = x; LOG[x] = i; x <<= 1
    if x & 0x100: x ^= 0x11D
for i in range(255, 512): EXP[i] = EXP[i-255]
def mul(a, b): return EXP[LOG[a]+LOG[b]] if a and b else 0
def fmt_ok(v):
    d = v >> 10; r = d
    for _ in range(10): r = (r << 1) ^ ((r >> 9) * 0x537)
    return ((d << 10) | (r & 0x3FF)) == v
def read(size, m):
    ver = (size-17)//4
    bits = [m[i][8] if i < 6 else m[7][8] if i == 6 else m[8][8] if i == 7 else m[8][7] if i == 8 else m[8][14-i] for i in range(15)]
    f1 = sum(int(b) << i for i, b in enumerate(bits))
    bits2 = [m[8][size-1-i] if i < 8 else m[size-15+i][8] for i in range(15)]
    f2 = sum(int(b) << i for i, b in enumerate(bits2))
    assert f1 == f2, 'format copies differ'
    v = f1 ^ 0x5412; assert fmt_ok(v), 'format BCH'
    assert (v >> 13) == 1, 'ECC level must be L'
    mask = (v >> 10) & 7
    fn = [[False]*size for _ in range(size)]
    def mk(x0, y0, w, h):
        for y in range(y0, y0+h):
            for x in range(x0, x0+w):
                if 0 <= x < size and 0 <= y < size: fn[y][x] = True
    mk(0, 0, 9, 9); mk(size-8, 0, 8, 9); mk(0, size-8, 9, 8)
    for i in range(size): fn[6][i] = fn[i][6] = True
    if ver >= 2: mk(size-9, size-9, 5, 5)
    bs = []
    right = size-1
    while right >= 1:
        if right == 6: right = 5
        for vert in range(size):
            for j in range(2):
                x = right-j; up = ((right+1) & 2) == 0; y = size-1-vert if up else vert
                if not fn[y][x]:
                    b = m[y][x]
                    inv = [(x+y) % 2 == 0, y % 2 == 0, x % 3 == 0, (x+y) % 3 == 0, (x//3+y//2) % 2 == 0, x*y % 2 + x*y % 3 == 0, (x*y % 2 + x*y % 3) % 2 == 0, ((x+y) % 2 + x*y % 3) % 2 == 0][mask]
                    bs.append(b ^ inv)
        right -= 2
    cw = [sum(int(bs[i*8+k]) << (7-k) for k in range(8)) for i in range(len(bs)//8)]
    return ver, cw
class QrTest(unittest.TestCase):
    def test_roundtrip(self):
        build()
        for text in ['WIFI:T:nopass;S:XeTang-ABCD;;', 'http://192.168.4.1/', 'http://192.168.100.200/', 'WIFI:T:nopass;S:XeTang-0000;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;']:
            size, m = dump(text)
            ver, cw = read(size, m)
            nd = {1: 19, 2: 34, 3: 55, 4: 80}[ver]; ne = {1: 7, 2: 10, 3: 15, 4: 20}[ver]
            cw = cw[:nd+ne]
            for i in range(ne):   # syndromes of the received polynomial must be zero
                s = 0
                for c in cw: s = mul(s, EXP[i]) ^ c
                self.assertEqual(s, 0, (text, i))
            bits = ''.join(f'{c:08b}' for c in cw[:nd])
            self.assertEqual(bits[:4], '0100'); n = int(bits[4:12], 2); self.assertEqual(n, len(text))
            data = bytes(int(bits[12+8*i:20+8*i], 2) for i in range(n)); self.assertEqual(data.decode(), text)
    def test_too_long(self):
        build(); r = subprocess.run([str(BIN), 'x'*79], capture_output=True, text=True); self.assertEqual(r.returncode, 1)
if __name__ == '__main__': unittest.main()
