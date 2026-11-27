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
        assert re.fullmatch(r'[IV]-(WEB|APP)-[A-F0-9]{10}',m['id'])
        assert m['title']==('Web' if m['platform']=='web' else 'App')+' '+('图片' if m['format']=='image' else '视频')+' · '+m['id'].split('-')[-1][:6], 'Public titles must remain neutral material identifiers'
        assert isinstance(m.get('agencies'),list) and m['agencies']
        assert all(isinstance(label,str) and (re.fullmatch(r'代理商[1-9][0-9]*',label) or label in ('自供','来源待确认')) for label in m['agencies']), 'Public agency labels must be anonymous aliases'
        for key in ('src','poster'):
            if key in m:
                assert re.fullmatch(r'media/[a-f0-9]{24}\.(jpg|mp4)',m[key])
                assert (ROOT/m[key]).is_file()
                sources.add(m[key])
for name in ('index.html','internal.html','catalog.json'):
    raw=(ROOT/name).read_text()
    for forbidden in ('spend_cents','creative_names','source_rows','private-ordering','consumption_cents','scale_reason','paid_share','/spark/','feishuapp.com/app/','166,609.96','39,308.65'):
        assert forbidden not in raw, (name,forbidden)
inline=re.search(r'<script id="catalog-data" type="application/json">(.*?)</script>',(ROOT/'index.html').read_text(),re.S)
assert inline and json.loads(inline.group(1))==catalog, 'HTML catalog differs from the verified public catalog'
actual={'media/'+p.name for p in (ROOT/'media').iterdir() if p.is_file()}
assert actual==sources
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
print(json.dumps({'public_materials':sum(len(p['materials']) for p in catalog['periods']),'public_media':len(sources),'allowlist':'passed','private_fields':'absent','agency_labels':'anonymous_only'},ensure_ascii=False))
