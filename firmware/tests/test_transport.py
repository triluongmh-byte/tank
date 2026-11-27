import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'host/tank_transport.py'
spec=importlib.util.spec_from_file_location('tank_transport',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestTransport(unittest.TestCase):
 def test_order_heartbeat_off(self):
  t=m.TankMotion();sent=[];t.request('MOTOR CUE WORK',0);t.poll(sent.append,0)
  self.assertEqual(sent,['MOTOR ARM','MOTOR HEARTBEAT']);t.receive('ACK MOTOR ARM',.01);t.poll(sent.append,.01)
  self.assertEqual(sent[-1],'MOTOR CUE WORK');t.receive('ACK MOTOR CUE WORK 1050ms',.02);t.poll(sent.append,.21);self.assertIn('MOTOR HEARTBEAT',sent)
  t.receive('MOTOR OFF mode=0 armed=0 yaw=0 reason=deadline',1.9);self.assertFalse(t.active)
 def test_timeout_stops(self):
  t=m.TankMotion();sent=[];t.request('MOTOR DRIVE BACK',0);t.poll(sent.append,0);t.poll(sent.append,2);self.assertEqual(sent[-1],'MOTOR STOP');self.assertTrue(t.failed)
  with self.assertRaises(ValueError):t.request('MOTOR CUE WORK',3)
 def test_denial_stops_no_retry(self):
  t=m.TankMotion();sent=[];t.request('MOTOR DRIVE FWD',0);t.poll(sent.append,0);t.receive('ERR MOTOR sonar',.1);t.poll(sent.append,.1);self.assertEqual(sent[-1],'MOTOR STOP');self.assertTrue(t.failed)
 def test_no_unbounded_requests(self):
  for command in ('AUTO ON','MOTOR TEST 0 +','MOTOR CUE FWD junk'):
   with self.assertRaises(ValueError):m.TankMotion().request(command,0)
 def test_legacy_receipt_rejected(self):
  with self.assertRaises(ValueError):m.authorize(p.parent,{'expectedMAC':'e0:72:a1:6c:d3:f8','firmwareVerified':True},'/dev/fake')
 def test_handshake_identity(self):
  class Port:
   def __init__(self,cap):self.sent=[];self.cap=cap
   def send(self,line):self.sent.append(line)
   def lines(self,_):return [self.cap,'MOTOR OFF mode=0 armed=0 yaw=0 reason=stop']
  mac='00:11:22:33:44:55';port=Port('MOTOR CAPS tank-v1 channels=7 heartbeat=200ms MAC='+mac)
  m.handshake(port,mac);self.assertNotIn('MOTOR ARM',port.sent)
  with self.assertRaises(ValueError):m.handshake(Port('MOTOR CAPS cues-v3 MAC='+mac),mac)
 def test_no_motion_on_sleep_ask(self):
  f=m.MotionForwarder(0);sent=[]
  for at in range(10):f.poll('ask',[], 'awake',sent.append,at)
  self.assertFalse(sent)
if __name__=='__main__':unittest.main()
