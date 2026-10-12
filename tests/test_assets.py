import hashlib,json,unittest
from pathlib import Path
from zipfile import ZipFile
from scripts.package import source_files,ROOT,build

class AssetTests(unittest.TestCase):
    def test_font_artifacts_match_manifest_and_package_allowlist(self):
        folder=ROOT/'static/fonts'
        manifest=json.loads((folder/'manifest.json').read_text())
        self.assertEqual(manifest['source_codepoints'],manifest['subset_codepoints'])
        included={p.relative_to(ROOT).as_posix() for p in source_files()}
        for entry in manifest['artifacts']:
            path=folder/entry['file'];data=path.read_bytes()
            self.assertEqual(data[:4],b'wOF2')
            self.assertEqual(len(data),entry['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),entry['sha256'])
            self.assertIn(path.relative_to(ROOT).as_posix(),included)
        self.assertIn('static/fonts/OFL.txt',included)
        self.assertNotIn('.streamlit/secrets.toml',included)
        self.assertNotIn('.env',included)
        self.assertTrue(any(p.startswith('frontend/') for p in included))

    def test_zip_preserves_binary_resources_and_excludes_private_files(self):
        with ZipFile(build()) as archive:
            for p in source_files():
                self.assertEqual(archive.read('audit-inquiry-agent/'+p.relative_to(ROOT).as_posix()),p.read_bytes())
            self.assertFalse(any(name.endswith('/secrets.toml') or '/.local/' in name or name.endswith('/.env') for name in archive.namelist()))
