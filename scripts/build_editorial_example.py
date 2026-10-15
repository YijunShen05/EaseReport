#!/usr/bin/env python3
"""Render explicit demo/config data as one offline report; no discovery or publication."""
import argparse
import html
import json
import math
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def validate(data):
    if type(data.get('exampleSchemaVersion')) is not int or data['exampleSchemaVersion'] != 1:raise ValueError('Unsupported exampleSchemaVersion; migrate explicitly')
    for name in ('title', 'summary', 'idField'):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError('Expected nonempty string: '+name)
    if not isinstance(data.get('rows'), list) or not isinstance(data.get('columns'), list) or not data['columns']:
        raise ValueError('rows and nonempty columns arrays required')
    fields=[]
    for c in data['columns']:
        if not isinstance(c,dict) or not isinstance(c.get('field'),str) or not isinstance(c.get('label'),str) or not c['field'] or not c['label']:
            raise ValueError('Each column needs nonempty field and label strings')
        fields.append(c['field'])
    if len(set(fields))!=len(fields):raise ValueError('Duplicate columns')
    for key in ('facet','drilldown'):
        spec=data.get(key)
        if key=='drilldown' and spec is None:continue
        if not isinstance(spec,dict) or not spec.get('field') or not spec.get('label'):
            raise ValueError(key+' needs explicit field and label')
    ids=set()
    for row in data['rows']:
        if not isinstance(row,dict):raise ValueError('Each row must be an object')
        ident=row.get(data['idField'])
        if type(ident) not in (str,int) or not str(ident).strip() or str(ident) in ids:raise ValueError('Unique nonempty row identity required')
        ids.add(str(ident))
        for c in data['columns']:
            v=row.get(c['field'])
            if c.get('numeric') and v is not None and (type(v) not in (int,float) or not math.isfinite(v)):
                raise ValueError('Numeric cells must be finite numbers or null')
        if data.get('sourcesField'):
            sources=row.get(data['sourcesField'],[])
            if not isinstance(sources,list) or any(not isinstance(x,dict) or not isinstance(x.get('url'),str) for x in sources):
                raise ValueError('Sources must be an array of URL records')
    c=data.get('comparison')
    if c is not None:
        if not isinstance(c,dict) or c.get('direction') not in ('higher','lower') or not isinstance(c.get('pairingNote'),str) or not c['pairingNote'].strip():
            raise ValueError('Comparison requires direction and explicit pairingNote')
        for key in ('unit','deltaUnit'):
            if not isinstance(c.get(key),str):raise ValueError('Comparison unit string required')
        if type(c.get('precision')) is not int or not 0<=c['precision']<=8:raise ValueError('precision must be 0..8')
        for side in ('baseline','candidate'):
            m=c.get(side)
            if not isinstance(m,dict) or not m.get('field') or not m.get('label'):raise ValueError('Comparison mapping missing')
            if m.get('statusField') and 'validStatus' not in m:raise ValueError('Explicit validStatus required')
    if type(data.get('pageSize',8)) is not int or data.get('pageSize',8)<1:raise ValueError('pageSize must be positive integer')
    allowed={'background','surface','text','muted','line','accent','soft'}
    for key,value in data.get('theme',{}).items():
        if key not in allowed or not isinstance(value,str) or not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?',value):
            raise ValueError('Theme accepts only known semantic colors in hex form')
    json.dumps(data,allow_nan=False)

def render(data):
    validate(data)
    css=(ROOT/'assets/editorial-analytical.css').read_text()
    template=(ROOT/'assets/editorial-analytical.html').read_text()
    theme=''.join('--report-'+k+':'+v+';' for k,v in data.get('theme',{}).items())
    payload=json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    return template.replace('__TITLE__',html.escape(data['title'])).replace('__STYLE__',css).replace('__THEME__',theme).replace('__PAYLOAD__',payload)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.data.resolve()==a.out.resolve():p.error('Output must not overwrite source data')
    result=render(json.loads(a.data.read_text()));a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(result);print(a.out)
if __name__=='__main__':main()
