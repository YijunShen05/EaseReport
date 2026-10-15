import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'examples/drosophila-mendel'
spec=importlib.util.spec_from_file_location('mendel_model',HERE/'model.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
sys.path.insert(0,str(HERE))
try:
 spec=importlib.util.spec_from_file_location('mendel_builder',HERE/'build_report.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
finally:sys.path.pop(0)
class MendelTests(unittest.TestCase):
 def setUp(self):self.data=M.build_data()
 def test_probabilities_from_gamete_enumeration(self):
  expected=[[.75,.25],[9/16,3/16,3/16,1/16],[.25]*4]
  self.assertEqual([M.predictions(s) for s in self.data['experiments']],expected)
 def test_seed_replays_raw_observations_without_resampling(self):
  stored=json.loads((HERE/'data.json').read_text());self.assertEqual(self.data,stored)
 def test_complete_classified_denominator(self):
  self.assertEqual(sum(self.data['analysis'][s['id']+'|all']['n'] for s in self.data['experiments']),1060)
 def test_exclusions_unknown_and_pending_separated(self):
  a=self.data['analysis']['dihybrid|all'];self.assertEqual((a['n'],a['unclassified'],a['excluded_classified'],a['excluded_unclassified'],a['pending_vials']),(496,10,48,2,1))
 def test_pending_is_not_a_zero_observation(self):
  self.assertIsNone(next(v for v in self.data['vials'] if v['id']=='D-06')['counts'])
  a=self.data['analysis']['dihybrid|D-06'];self.assertEqual(a['n'],0);self.assertIsNone(a['chi2']);self.assertIsNone(a['p'])
 def test_small_vial_kept_but_p_approximation_suppressed(self):
  a=self.data['analysis']['testcross|T-04'];self.assertEqual(a['n'],12);self.assertFalse(a['approximation_valid']);self.assertIsNone(a['p'])
  self.assertEqual(self.data['analysis']['testcross|all']['n'],264)
 def test_known_chi_square_upper_tail_values(self):
  # For 3:1 counts [75+d,25-d], chi2 = d^2*(1/75+1/25).
  x=3.841458820694124;delta=(x/(1/75+1/25))**.5
  self.assertAlmostEqual(M.chi_square([75+delta,25-delta],[.75,.25])['p'],.05,places=11)
  x=7.814727903251179;delta=(x/2)**.5*5
  self.assertAlmostEqual(M.chi_square([25+delta,25-delta,25,25],[.25]*4)['p'],.05,places=11)
 def test_exact_fit_and_zero_observation(self):
  self.assertAlmostEqual(M.chi_square([75,25],[.75,.25])['p'],1)
  r=M.chi_square([30,0],[.75,.25]);self.assertEqual(r['n'],30);self.assertTrue(r['approximation_valid']);self.assertGreater(r['chi2'],0)
 def test_pending_cannot_be_rewritten_as_zero(self):
  d=copy.deepcopy(self.data);next(v for v in d['vials'] if v['id']=='D-06')['counts']=[0]*4
  with self.assertRaises(ValueError):B.render(d)
 def test_wrong_category_vector_rejected(self):
  self.data['vials'][0]['counts'].append(0)
  with self.assertRaises(ValueError):B.render(self.data)
 def test_stale_cache_rejected(self):
  self.data['analysis']['dihybrid|all']['n']+=1
  with self.assertRaises(ValueError):B.render(self.data)
 def test_explicit_synthetic_and_schema_required(self):
  self.data['synthetic']=False
  with self.assertRaises(ValueError):B.render(self.data)
 def test_embedded_original_source_escaped(self):
  self.data['vials'][0]['note']='</script><script>window.bad=true</script>'
  page=B.render(self.data);payload=page.split('<script id="report-data" type="application/json">')[1].split('</script>')[0]
  self.assertEqual(json.loads(payload)['vials'][0]['note'],self.data['vials'][0]['note'])
if __name__=='__main__':unittest.main()
