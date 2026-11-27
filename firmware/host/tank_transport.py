"""Tank-v1 adapter for the reference bridge's send()/lines() interface.

No device discovery, serial open, daemon changes, or automatic motion on import.
The sole serial owner must call poll() at least every 100 ms while active.
"""
import hashlib
import re
import time

DURATION={'WORK':1.050,'DONE':1.350,'LEFT':.540,'RIGHT':.540,'FWD':.540,'BACK':.540}

def authorize(root,receipt,port,device_mac=None):
    """A new user-authorized tank receipt is required; old pet receipts cannot pass."""
    mac=receipt.get('expectedMAC','').lower()
    if (receipt.get('product')!='pet-tank' or not receipt.get('motionAuthorized')
        or not receipt.get('firmwareVerified') or not receipt.get('usbChecked')
        or not receipt.get('motorOutputsVerifiedOff') or device_mac!=mac
        or not re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',mac)
        or receipt.get('port')!=port or not receipt.get('candidateSourceShas')):
        raise ValueError('No separately authorized, verified tank firmware/device receipt')
    for name,sha in receipt['candidateSourceShas'].items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()/'firmware') or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('Tank sources changed after verification')
    return mac

def handshake(serial,expected_mac,clock=time.monotonic,timeout=3):
    if not re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',expected_mac):raise ValueError('Explicit target MAC required')
    serial.send('MOTOR STOP');serial.send('MOTOR CAPS');serial.send('MOTOR STATUS')
    found=False;off=False;end=clock()+timeout
    while clock()<end:
        for line in serial.lines(.05):
            if line.startswith('MOTOR CAPS'):
                fields=line.split()
                if ('tank-v1' not in fields or 'channels=7' not in fields or 'heartbeat=200ms' not in fields
                    or 'MAC='+expected_mac not in fields):raise ValueError('Wrong tank identity/capabilities')
                found=True
            if line.startswith('ERR MOTOR'):raise ValueError(line)
            if line.startswith('MOTOR OFF ') and 'armed=0' in line.split():off=True
            if found and off:return
    raise ValueError('Tank identity/OFF handshake timed out')

class TankMotion:
    """One bounded command at a time; ARM ACK then command ACK then confirmed OFF."""
    def __init__(self):
        self.phase='off';self.command=None;self.expected=None;self.deadline=0
        self.heartbeat=0;self.status_at=0;self.failed=None;self.sent=[]
    @property
    def active(self):return self.phase!='off'
    def request(self,command,now):
        if self.active or self.failed:raise ValueError('Tank busy or faulted')
        if command.startswith('MOTOR CUE ') and command[10:] in DURATION:duration=DURATION[command[10:]]
        elif command in ('MOTOR DRIVE FWD','MOTOR DRIVE BACK'):duration=2.0
        else:raise ValueError('Only bounded CUE/DRIVE requests supported here')
        self.command=command;self.duration=duration;self.phase='need-arm';self.deadline=now+2
    def receive(self,line,now):
        if line.startswith('ERR MOTOR'):
            self.failed=line;self.phase='need-stop';return
        if self.phase=='arm' and line=='ACK MOTOR ARM':self.phase='need-command'
        elif self.phase=='ack' and line.startswith(self.expected):
            self.phase='run';self.deadline=now+self.duration+2 # includes center/echo acquisition
        elif self.phase in ('run','stopping') and line.startswith('MOTOR OFF ') and 'armed=0' in line.split():
            self.phase='off';self.command=None
    def stop(self,send,now):
        if self.phase=='stopping':return
        send('MOTOR STOP');self.phase='stopping';self.deadline=now+1;self.status_at=now
    def poll(self,send,now):
        if self.phase=='off':return
        if self.phase=='need-stop':self.stop(send,now);return
        if now>=self.deadline:
            send('MOTOR STOP');self.failed='Tank ACK/OFF timeout';self.phase='off';return
        if self.phase=='need-arm':send('MOTOR ARM');self.phase='arm'
        elif self.phase=='need-command':
            send(self.command);self.phase='ack'
            self.expected='ACK '+self.command+' '+str(round(self.duration*1000))+'ms'
        if now>=self.heartbeat:send('MOTOR HEARTBEAT');self.heartbeat=now+.2
        if self.phase in ('run','stopping') and now>=self.status_at:send('MOTOR STATUS');self.status_at=now+.1

class MotionForwarder:
    """Reference poll/receive/stop API with quiet bounded cues and tank handshake.

    Instantiating this is not authorization. The bridge calls authorize/handshake
    first. A failed command latches this instance off; no retry or catch-up queue.
    """
    def __init__(self,now,quiet=True):
        self.transport=TankMotion();self.state=None;self.state_at=now;self.power='awake'
        self.warm_until=now+3;self.work_sent=False;self.turns=0;self.next_think=now
        self.seen=[];self.starts=[];self.next_at=now;self.pending_done=False
    @property
    def failed(self):return self.transport.failed
    def receive(self,line,now):self.transport.receive(line,now)
    def stop(self,send,now):
        if self.transport.active:self.transport.stop(send,now)
    def poll(self,state,completed,power,send,now,allow_start=True):
        fresh=[key for key in completed if key not in self.seen];self.seen=(self.seen+fresh)[-64:]
        if power!=self.power:
            self.power=power;self.pending_done=False
            if power=='awake':self.warm_until=now+3
        if state!=self.state:
            old=self.state;self.state=state;self.state_at=now
            if old=='idle' or state=='idle':self.work_sent=False;self.turns=0
            if state!='idle':self.pending_done=False
            # A state transition cancels an active cue before any new cue.
            self.stop(send,now)
        if power!='awake' or state in ('ask','cancelled'):
            self.pending_done=False;self.stop(send,now)
        elif state=='idle' and fresh:self.pending_done=True
        self.transport.poll(send,now)
        if self.transport.active or self.failed or not allow_start or power!='awake' or state in ('ask','cancelled') or now<self.warm_until or now<self.next_at:return
        self.starts=[at for at in self.starts if now-at<30]
        cue=None
        if state=='idle' and self.pending_done:cue='DONE';self.pending_done=False
        elif state=='processing' and now-self.state_at>=.6 and not self.work_sent:cue='WORK';self.work_sent=True
        elif state=='thinking' and now-self.state_at>=1 and self.turns<2 and now>=self.next_think:
            cue='FWD' if self.turns%2==0 else 'BACK';self.turns+=1;self.next_think=now+8
        if cue and len(self.starts)<4:
            self.transport.request('MOTOR CUE '+cue,now);self.transport.poll(send,now)
            self.starts.append(now);self.next_at=now+DURATION[cue]*2
