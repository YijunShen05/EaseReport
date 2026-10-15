#!/usr/bin/env python3
"""Build the synthetic lab example from EaseReport CSS and explicit domain records."""
import argparse
import hashlib
import json
from pathlib import Path
from model import build_data,predictions,summarize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def render(data):
    if data.get('synthetic') is not True or type(data.get('schemaVersion')) is not int or data['schemaVersion']!=1:raise ValueError('Explicit synthetic v1 records required')
    if len({v['id'] for v in data['vials']})!=len(data['vials']):raise ValueError('Duplicate vial identity')
    specs={s['id']:s for s in data['experiments']}
    for v in data['vials']:
        if v['experiment'] not in specs:raise ValueError('Unknown experiment')
        if v['counts'] is not None and len(v['counts'])!=len(specs[v['experiment']]['classes']):raise ValueError('Wrong phenotype count length')
        if v['status']=='pending':
            if v['counts'] is not None or v['unclassified'] is not None:raise ValueError('Pending counts must remain missing')
        elif v['status'] in ('accepted','excluded'):
            if any(type(x) is not int or x<0 for x in v['counts']) or type(v['unclassified']) is not int or v['unclassified']<0:raise ValueError('Invalid count')
        else:raise ValueError('Unknown QC status')
    for s in data['experiments']:
        s['probabilities']=predictions(s)
        for key in ['all']+[v['id'] for v in data['vials'] if v['experiment']==s['id']]:
            if data['analysis'][s['id']+'|'+key]!=summarize(data,s['id'],key):raise ValueError('Analysis cache disagrees with raw records')
    data['sources']=json.loads((HERE/'sources.json').read_text())['sources']
    data['method']={'skill':'EaseReport','source':'SKILL.md','sha256':hashlib.sha256((ROOT/'SKILL.md').read_bytes()).hexdigest()}
    payload=json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':')).replace('<','\\u003c')
    return (HERE/'report-template.html').read_text().replace('__STYLE__',(ROOT/'assets/editorial-analytical.css').read_text()).replace('__PAYLOAD__',payload)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'demos/drosophila-mendel.html');p.add_argument('--regenerate-data',action='store_true');a=p.parse_args()
    if a.out.resolve() in {p.resolve() for p in HERE.iterdir() if p.is_file()}:p.error('Output must not overwrite example source files')
    data=build_data() if a.regenerate_data else json.loads((HERE/'data.json').read_text())
    if a.regenerate_data:(HERE/'data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    result=render(data);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(result);print(a.out)
if __name__=='__main__':main()
