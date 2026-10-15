"""Synchronise public preset context and bilingual facet definitions with the Python source."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from inquiry.examples import EXAMPLES
from inquiry.analysis import seed_case,DEFINITIONS
from inquiry.progress import POLICY
for path,data in [('cases.json',[{**c,'analysis_en':seed_case(c,'English'),'analysis_zh':seed_case(c,'中文')} for c in EXAMPLES]),('dimensions.json',DEFINITIONS),('readiness-policy.json',POLICY)]:
 (ROOT/'web/src'/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Synchronized source-checked presets and dimension definitions.')
