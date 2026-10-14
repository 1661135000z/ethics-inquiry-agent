"""Build a minimal Worker project for the current React frontend and Python API."""
import json
from pathlib import Path
import shutil
root=Path(__file__).resolve().parent.parent
project=root/'.inquire-ethics-lab'
project.mkdir(exist_ok=True)
target=project/'src'
target.mkdir(exist_ok=True)
for package,names in {'edge':['__init__.py','worker.py','service.py','policy.py','transport.py','store.py','d1.py'],
                      'inquiry':['__init__.py','core.py','examples.py','review_packet.py']}.items():
    (target/package).mkdir(exist_ok=True)
    for name in names: shutil.copy2(root/package/name,target/package/name)
shutil.copy2(root/'pyproject.toml',project/'pyproject.toml')
shutil.copy2(root/'edge'/'worker.py',target/'worker.py')
config=json.loads((root/'wrangler.jsonc').read_text())
config['main']='src/worker.py'
config['assets']['directory']='../web/dist'
(project/'wrangler.jsonc').write_text(json.dumps(config,indent=2))
print('Prepared minimal Worker project: .inquire-ethics-lab')
