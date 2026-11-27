#!/usr/bin/env python3
"""Fail closed before publishing a public-only GitHub Pages artifact."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'id','title','platform','format','agencies','src','poster','width','height','duration'}
catalog=json.loads((ROOT/'catalog.json').read_text())
sources=set()
for p in catalog['periods']:
    assert set(p)<= {'id','start','end','label','materials'}
    assert p['id']==p['start']+'_'+p['end']
    for m in p['materials']:
        assert set(m)<=ALLOWED
        assert m['format'] in ('image','video') and m['platform'] in ('web','app')
        for key in ('src','poster'):
            if key in m:
                assert re.fullmatch(r'media/[a-f0-9]{24}\.(jpg|mp4)',m[key])
                assert (ROOT/m[key]).is_file()
                sources.add(m[key])
for name in ('index.html','internal.html','catalog.json'):
    raw=(ROOT/name).read_text()
    for forbidden in ('spend_cents','creative_names','source_rows','scale_reason','paid_share','/spark/','feishuapp.com/app/','166,609.96','39,308.65'):
        assert forbidden not in raw, (name,forbidden)
actual={'media/'+p.name for p in (ROOT/'media').iterdir() if p.is_file()}
assert actual==sources
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
print(json.dumps({'public_materials':sum(len(p['materials']) for p in catalog['periods']),'public_media':len(sources),'allowlist':'passed','private_fields':'absent'},ensure_ascii=False))
