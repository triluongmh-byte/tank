"""Extract the phone page <script> and syntax-check it with node (skipped only if node is absent)."""
import pathlib, re, shutil, subprocess, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
class PageTest(unittest.TestCase):
    def test_script_parses(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'node required to check page script')
        src = (ROOT/'firmware/tank/page.h').read_text()
        m = re.search(r'<script>(.*?)</script>', src, re.S)
        self.assertTrue(m)
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d)/'page.js'; f.write_text(m.group(1))
            r = subprocess.run([node, '--check', str(f)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
if __name__ == '__main__': unittest.main()
