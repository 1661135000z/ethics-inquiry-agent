"""Create a source-only portable backup, using an explicit allowlist."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]

def source_files():
    files = [ROOT / p for p in (
        'app.py', 'requirements.txt', 'README.md', '.gitignore',
        '.streamlit/config.toml', '.streamlit/secrets.toml.example',
        'docs/evaluation.md', 'docs/experience-design.md', 'scripts/package.py', '.env.example', 'THIRD_PARTY_NOTICES.md',
    )]
    for folder in ('inquiry', 'tests'):
        files.extend(sorted((ROOT / folder).glob('*.py')))
    for folder in ('frontend', 'static/fonts'):
        files.extend(sorted(p for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in {'.css','.js','.woff2','.txt','.json'}))
    if (ROOT / 'scripts/build_fonts.py').exists(): files.append(ROOT / 'scripts/build_fonts.py')
    return files

def build():
    output = ROOT / 'dist' / 'ethics-inquiry-source.zip'
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in source_files():
            archive.write(path, 'audit-inquiry-agent/' + path.relative_to(ROOT).as_posix())
    return output

if __name__ == '__main__':
    print(build())
