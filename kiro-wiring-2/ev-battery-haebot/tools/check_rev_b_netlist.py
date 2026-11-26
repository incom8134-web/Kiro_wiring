"""Check the exported KiCad netlist against HAEBOT Rev B power-cut requirements.

Reads exports only, never edits KiCad source. Standard-library Python only.
"""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]

def parse(text):
    stack=[]; result=None
    for token in re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text):
        if token=='(':
            node=[]
            if stack:stack[-1].append(node)
            stack.append(node)
        elif token==')':
            result=stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack
    return result

def children(node,key):return [x for x in node if isinstance(x,list) and x and x[0]==key]
def one(node,key):
    found=children(node,key)
    assert len(found)==1,(key,found)
    return found[0]

root=parse((ROOT/'exports/HAEBOT_EV_NETLIST.net').read_text(encoding='utf-8-sig'))
components={one(c,'ref')[1]:c for c in children(one(root,'components'),'comp')}
assert 'SW2' not in components,'START must be absent'
assert {'K1','S1','U6','J6'}<=components.keys()
nets={}
for n in children(one(root,'nets'),'net'):
    name=one(n,'name')[1].removeprefix('/')
    nets[name]={(one(p,'ref')[1],one(p,'pin')[1]) for p in children(n,'node')}

def contains(net,*pins):
    assert set(pins)<=nets[net],f'{net}: missing {set(pins)-nets[net]}'
def has_refs(net,refs):
    assert set(refs)<={r for r,p in nets[net]},f'{net}: expected {refs}'

# Semantic functional port names are deliberate: no invented hardware pad numbering.
contains('BATT_SW',('U6','BAT'))
has_refs('BATT_SW',['SW1'])
contains('BATT_MON',('U6','LOAD'))
has_refs('BATT_MON',['F3','F4','F5','K1'])
assert len(nets['BATT_SW'])==2,'All load branches must be after the monitor'
contains('AUX_5V',('U6','V5'))
has_refs('AUX_5V',['FB2','J5'])
contains('I2C_SDA',('U6','SDA'),('J6','SDA'))
contains('I2C_SCL',('U6','SCL'),('J6','SCL'))
assert len(nets['I2C_SDA'])==len(nets['I2C_SCL'])==2
contains('POWER_GND',('U6','GND'),('J6','GND'))
coil=[(name,pins) for name,pins in nets.items() if any(r=='K1' and p in {'A1','COIL+'} for r,p in pins)]
assert len(coil)==1,coil
has_refs(coil[0][0],['S1'])
assert 'SW2' not in {r for pins in nets.values() for r,p in pins}
assert not any(r=='K1' and p in {'13','14'} for pins in nets.values() for r,p in pins),'No auxiliary contact'
has_refs('MOTION_RAW',['K1','U3'])
has_refs('MOTION_12V',['U3','FB1'])
has_refs('WHEEL_12V',['FB1','U30'])
has_refs('ARM1_12V',['FB1','U41'])
has_refs('ARM2_12V',['FB1','U42'])
for name in ['BATT_SW','BATT_MON','AUX_5V','I2C_SDA','I2C_SCL','MOTION_RAW','MOTION_12V','WHEEL_12V','ARM1_12V','ARM2_12V']:
    assert ('U6','GND') not in nets[name],f'{name} short to monitor ground'
assert len({frozenset(nets[n]) for n in ['BATT_SW','BATT_MON','MOTION_RAW','MOTION_12V','AUX_5V','POWER_GND']})==6

title=one(one(one(root,'design'),'sheet'),'title_block')
assert one(title,'rev')[1]=='B','Export must show revision B'
assert one(title,'date')[1]=='2026-11-26','Export must show current revision date'
print('PASS: Rev B metadata; no START/aux loop; main discharge monitoring; 5 V sensor supply; separate I2C; three fused motion branches after K1/U3.')
for name in ['BATT_SW','BATT_MON','AUX_5V','I2C_SDA','I2C_SCL',coil[0][0],'MOTION_RAW','MOTION_12V']:
    print(name,':',', '.join(f'{r}.{p}' for r,p in sorted(nets[name])))
