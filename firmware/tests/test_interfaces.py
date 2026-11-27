import importlib.util,pathlib,tempfile,unittest
root=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('reconcile',root/'firmware/reconcile.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestPcbMeasurement(unittest.TestCase):
 def test_measures_connector_pad_nets(self):
  text='''(kicad_pcb (version 20241229) (net 1 "GND") (net 2 "I2C_SDA")
  (footprint "Local:Header" (property "Reference" "J_CTRL")
   (pad "1" thru_hole rect (at 0 0) (net 1 "GND"))
   (pad "3" thru_hole circle (at 2.54 0) (net 2 "I2C_SDA"))
   (pad "12" thru_hole circle (at 5.08 0))))'''
  path=root/'build/firmware/tests/mock-main.kicad_pcb';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
  measured=m.measure(path);self.assertEqual(measured['J_CTRL'],{'1':'GND','3':'I2C_SDA','12':'NC'})
 def test_duplicate_pad_mismatch_fails(self):
  path=root/'build/firmware/tests/mock-duplicate.kicad_pcb';path.write_text('(kicad_pcb (footprint "X" (property "Reference" "J_CTRL") (pad "1" thru_hole rect (net 1 "GND")) (pad "1" thru_hole rect (net 2 "5V"))))')
  with self.assertRaises(ValueError):m.measure(path)
 def test_kicad10_name_only_nets(self):
  path=root/'build/firmware/tests/mock-kicad10.kicad_pcb'
  path.write_text('(kicad_pcb (version 20260206) (footprint "X" (property "Reference" "J_FAN") (pad "1" thru_hole rect (net "LOAD_5V")) (pad "2" thru_hole circle (net "GND"))))')
  self.assertEqual(m.measure(path),{'J_FAN':{'1':'LOAD_5V','2':'GND'}})
 def buffered_fixture(self):
  measured={'J_FAN':{'1':'LOAD_5V','2':'GND'},'J_PCA':{},'U1':{'1':'PCA_OE_N','19':'PCA_OE_N','10':'GND','20':'SERVO_3V3'}};pins=[]
  for ch,(name,(a,b)) in enumerate(zip(('LF','LM','LR','RF','RM','RR','TURRET'),((2,18),(4,16),(6,14),(8,12),(11,9),(13,7),(15,5)))):
   net='PWM_'+name;pad=str(ch+6);measured['J_PCA'][pad]=net+'_RAW'
   measured['U1'][str(a)]=net+'_RAW';measured['U1'][str(b)]=net;measured['J_S'+str(ch)]={'3':net}
   pins.append({'device':'J_PCA','pin':pad,'net':net})
  return measured,pins
 def test_all_buffered_paths_and_crossed_channel(self):
  measured,pins=self.buffered_fixture();errors,_,paths=m.compare_board(measured,pins)
  self.assertEqual(errors,[]);self.assertEqual(len(paths),7)
  measured['U1']['16']='PWM_LF'
  self.assertIn('J_PCA.7: buffered path through U1 differs',m.compare_board(measured,pins)[0])
 def test_buffer_disable_and_supply_must_match(self):
  for pad in ('1','19','10','20'):
   measured,pins=self.buffered_fixture();measured['U1'][pad]='WRONG'
   self.assertEqual(len(m.compare_board(measured,pins)[0]),7)
 def test_named_nc_must_be_isolated(self):
  measured,pins=self.buffered_fixture();net='unconnected-(J_CTRL-Pin_12-Pad12)'
  measured['J_CTRL']={'12':net};pins.append({'device':'J_CTRL','pin':'12','net':'NC'})
  self.assertEqual(m.compare_board(measured,pins)[0],[])
  measured['OTHER']={'1':net}
  self.assertTrue(any('J_CTRL.12' in error for error in m.compare_board(measured,pins)[0]))
 def test_fan_must_not_use_switched_servo_rail(self):
  measured,pins=self.buffered_fixture();measured['J_FAN']['1']='SERVO_5V'
  self.assertIn('J_FAN.1: PCB SERVO_5V, release notes LOAD_5V',m.compare_board(measured,pins)[0])
if __name__=='__main__':unittest.main()
