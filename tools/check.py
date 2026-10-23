"""Small structural check. Does not claim to test an LLM or a human onboarding."""
from pathlib import Path
from zipfile import ZipFile
import json, re, tempfile, csv
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
def check_links(root):
    for p in root.rglob('*.md'):
        if '.git' in p.parts or 'workspace' in p.parts: continue
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            if re.match(r'^[a-z]+:',target) or target.startswith('#'):continue
            assert (p.parent/target.split('#')[0]).exists(),(p,target)
def main():
    check_links(ROOT)
    expected=json.loads((ROOT/'tools/release-files.json').read_text())
    with ZipFile(ROOT/'dist/alpes-agent-starter-kit.zip') as z:
        assert sorted(z.namelist())==sorted('alpes-agent-starter-kit/'+x for x in expected)
        assert all(not any(x in n.split('/') for x in ('.git','workspace','.env','__pycache__')) for n in z.namelist())
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp)
            extracted=Path(tmp)/'alpes-agent-starter-kit'
            check_links(extracted)
            for p in extracted.rglob('*'):
                if p.suffix in ('.md','.txt','.csv'):
                    text=p.read_text()
                    assert '/Users/' not in text and 'BEGIN PRIVATE KEY' not in text, p
            rows=list(csv.DictReader((extracted/'examples/supply-check/input.csv').open()))
            actual=[]
            for row in rows:
                if row['status']=='Завершён':result='completed'
                elif not row['planned_date']:result='missing'
                else:result=(date(2026,10,23)-date.fromisoformat(row['planned_date'])).days
                actual.append((row['id'],result))
            assert actual==[('TEST-01',2),('TEST-02','completed'),('TEST-03','missing')],actual
            print('Extracted fixture:',actual)
    chat=(ROOT/'CHATGPT-START.txt').read_text()
    for name in ['AGENTS.md','templates/task.md','templates/workflow.md','templates/checks.md']:
        assert (ROOT/name).read_text() in chat, name
    print('PASS: links, explicit archive manifest, clean extraction, fixture arithmetic, shared ChatGPT rules')
if __name__=='__main__':main()
