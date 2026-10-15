"""Prepare isolated synthetic fixtures only; does not access production data."""
import argparse
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build_editorial_example.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
def prepare(out):
 out.mkdir(parents=True,exist_ok=True)
 for name in ['release-quality','supplier-delivery']:
  data=json.loads((ROOT/'examples'/(name+'.json')).read_text());(out/(name+'.html')).write_text(B.render(data))
 data=json.loads((ROOT/'examples/supplier-delivery.json').read_text());data['synthetic']=False;data['comparison']=None;data.pop('drilldown');(out/'no-comparison.html').write_text(B.render(data));data['rows']=[];(out/'empty.html').write_text(B.render(data))
 data=json.loads((ROOT/'examples/supplier-delivery.json').read_text());data['rows'][0]['order_no']='=2+2';data['rows'][0]['audit_note']='</script><script>window.HOSTILE_EXECUTED=true</script>';data['rows'][0]['carrier']='Long-identifier-without-break-'+('verylong'*15);data['rows'][0]['references']=[{'url':'javascript:alert(1)','label':'bad link'}];data['rows'][0]['delay_a']=-2;(out/'hostile.html').write_text(B.render(data))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args();prepare(args.out);print(args.out)
