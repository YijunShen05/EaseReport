import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build_editorial_example.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
class BuilderTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/'examples/supplier-delivery.json').read_text())
 def test_two_domain_configs(self):
  for name in ['release-quality','supplier-delivery']:
   data=json.loads((ROOT/'examples'/(name+'.json')).read_text());page=B.render(data)
   self.assertIn(data['title'],page);self.assertNotIn('__PAYLOAD__',page)
 def test_payload_roundtrip_and_script_end_escape(self):
  self.data['rows'][0]['audit_note']='</script><script>window.bad=true</script> __STYLE__'
  page=B.render(self.data);payload=page.split('<script id="report-data" type="application/json">')[1].split('</script>')[0]
  self.assertEqual(json.loads(payload),self.data);self.assertNotIn('</script>',payload)
 def test_effective_zero_preserved(self):
  B.validate(self.data);self.assertEqual(self.data['rows'][1]['delay_b'],0)
 def test_missing_preserved(self):
  B.validate(self.data);self.assertIsNone(self.data['rows'][2]['delay_a'])
 def test_unknown_example_version_rejected(self):
  self.data['exampleSchemaVersion']=2
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_duplicate_id_rejected(self):
  self.data['rows'][1]['order_no']='P1'
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_duplicate_column_rejected(self):
  self.data['columns'].append(copy.deepcopy(self.data['columns'][0]))
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_direction_not_inferred(self):
  self.data['comparison'].pop('direction')
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_pairing_note_required(self):
  self.data['comparison']['pairingNote']=''
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_status_validity_explicit(self):
  self.data['comparison']['baseline'].pop('validStatus')
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_theme_injection_rejected(self):
  self.data['theme']['accent']='red;} body{display:none'
  with self.assertRaises(ValueError):B.render(self.data)
 def test_nonfinite_rejected(self):
  self.data['rows'][0]['delay_a']=float('nan')
  with self.assertRaises(ValueError):B.validate(self.data)
 def test_no_comparison_no_drilldown(self):
  self.data['comparison']=None;self.data.pop('drilldown');B.render(self.data)
 def test_empty_dataset_supported(self):
  self.data['rows']=[];B.render(self.data)
if __name__=='__main__':unittest.main()
