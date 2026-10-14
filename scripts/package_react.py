"""Portable React + native Python backup; source/build allowlist, never secrets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]

def source_files():
    files=[ROOT/name for name in ['README.md','requirements-api.txt','.env.example','.gitignore','THIRD_PARTY_NOTICES.md','package.json','pnpm-lock.yaml','pnpm-workspace.yaml','pyproject.toml','wrangler.jsonc','edgeone.json','docs/migration/mirror-plan.md','docs/react-experience.md','scripts/prepare_worker.py','scripts/package_react.py','web/index.html','web/package.json','web/tsconfig.json','web/vite.config.ts']]
    for folder in ['edge','inquiry','tests_next']:
        files.extend(sorted((ROOT/folder).glob('*.py')))
    files.append(ROOT/'edge/schema.sql')
    for folder in ['web/src','web/public','web/dist','edge-functions']:
        files.extend(sorted(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.ts','.tsx','.json','.css','.js','.html','.svg','.woff2','.txt'}))
    return files

def build():
    if not (ROOT/'web/dist/index.html').is_file():raise RuntimeError('Build the frontend before packaging.')
    output=ROOT/'dist/inquire-react-source.zip';output.parent.mkdir(exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for path in source_files():z.write(path,'inquire/'+path.relative_to(ROOT).as_posix())
    return output
if __name__=='__main__':print(build())
