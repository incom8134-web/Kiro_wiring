"""Supplementary photo wiring guide. Original photographs remain unchanged.
PDF/SVG viewports crop pictures; every connection is a native vector line.
Use the same ReportLab runtime/fonts as render_block_diagrams.py.
"""
from pathlib import Path
import base64
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter
import render_block_diagrams as b

ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'photo-wiring'/'assets'
b.W,b.H=2400,1600
RED='#cb2537'; ORANGE='#d57800'; BLACK='#20272d'; GREEN='#168454'; BLUE='#2676bd'; PURPLE='#8552b3'
pdfmetrics.registerFont(TTFont('Diagram','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('DiagramBold','C:/Windows/Fonts/malgunbd.ttf'))

def picture(d,name,x,y,w,h,crop=None):
    path=A/name; im=Image.open(path); iw,ih=im.size
    crop=crop or (0,0,iw,ih); cx,cy,cw,ch=crop
    scale=min(w/cw,h/ch); vx=x+(w-cw*scale)/2;vy=y+(h-ch*scale)/2
    dx=vx-cx*scale;dy=vy-cy*scale
    clip='clip'+str(len(d.svg)); mime='image/png' if path.suffix=='.png' else 'image/jpeg'
    d.svg.append(f'<defs><clipPath id="{clip}"><rect x="{vx}" y="{vy}" width="{cw*scale}" height="{ch*scale}"/></clipPath></defs>')
    encoded=base64.b64encode(path.read_bytes()).decode()
    d.svg.append(f'<image x="{dx}" y="{dy}" width="{iw*scale}" height="{ih*scale}" href="data:{mime};base64,{encoded}" clip-path="url(#{clip})"/>')
    d.pdf.saveState(); p=d.pdf.beginPath();p.rect(vx,b.H-vy-ch*scale,cw*scale,ch*scale);d.pdf.clipPath(p,stroke=0,fill=0)
    d.pdf.drawImage(ImageReader(str(path)),dx,b.H-dy-ih*scale,iw*scale,ih*scale,mask='auto')
    d.pdf.restoreState()

def text(d,x,y,s,size=22,bold=False,color=BLACK,maxw=None):d.text(x,y,s,size,bold,color,maxw)
def wire(d,pts,color=RED,dash=False,width=5):
    d.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="9 7"' if dash else '')+'/>')
    d.pdf.setStrokeColor(HexColor(color));d.pdf.setLineWidth(width);d.pdf.setDash([9,7] if dash else [])
    path=d.pdf.beginPath();path.moveTo(pts[0][0],b.H-pts[0][1])
    for x,y in pts[1:]:path.lineTo(x,b.H-y)
    d.pdf.drawPath(path)

def photo_box(self,x,y,w,h,title,lines=(),color='#183249',fill='#f7fafc',dash=False):
    self.rect(x,y,w,h,fill,color,dash)
    self.text(x+16,y+34,title,26 if w>300 else 21,True,color,maxw=w-32)
    leading=max(20,min(38,(h-80)/max(1,len(lines)-1)))
    for i,line in enumerate(lines):self.text(x+16,y+64+i*leading,line,22 if w>300 else 18,maxw=w-32)
b.Drawing.box=photo_box
def port(d,x,y,label,color=RED,side='right'):
    d.pdf.setFillColor(HexColor('#ffffff'));d.pdf.setStrokeColor(HexColor(color));d.pdf.setLineWidth(3);d.pdf.circle(x,b.H-y,7,stroke=1,fill=1)
    d.svg.append(f'<circle cx="{x}" cy="{y}" r="7" fill="white" stroke="{color}" stroke-width="3"/>')
    if label:text(d,x+(12 if side=='right' else -120),y-12,label,19,True,color)
def n(d,x,y):
    wire(d,[(x,y),(x,y+40)],BLACK);port(d,x,y+40,'N',BLACK)
def fuse(d,x,y,label,w=130):
    d.rect(x,y,w,54,'#fff7ed','#846044');text(d,x+10,y+35,label,20,True,maxw=w-20)
def title(d,page,heading,sub):
    d.pdf.setTitle('HAEBOT Rev B photo wiring guide - '+heading)
    text(d,45,60,'HAEBOT / KIRO  |  PHOTO WIRING GUIDE',37,True)
    text(d,45,100,heading,28,True)
    text(d,45,134,sub,20,maxw=2300)
    text(d,2170,60,f'{page} / 3',24,True)
    wire(d,[(45,154),(2350,154)],'#9aadb8')
def footer(d):
    text(d,45,1510,'Rev B pictorial supplement | 2026-11-26 | * = provisional rating | Drawing positions do not establish terminal polarity.',18,color='#5b6570')
    text(d,45,1540,'Follow actual + / - / NC markings. Battery BMS, K1 continuous duty / coil / suppression and I2C pin mapping still need verification.',18,color=RED,maxw=2300)
def stop_icon(d,x,y):
    d.rect(x+28,y+65,135,70,'#333333','#333333')
    d.rect(x,y+8,190,78,'#cc2735','#92212b')
    text(d,x+37,y+57,'E-STOP',25,True,'#ffffff')
    text(d,x+15,y+165,'NC - LATCHING',21,True,GREEN)
def finish(d):
    d.finish()

# Sheet 1: big recognizable parts and the power harness.
d=b.Drawing('HAEBOT_EV_PHOTO_WIRING_01')
title(d,1,'1. Power harness - wheels + BOTH new 12 V arms','Selected battery: VOLTON 12 V 45 Ah lithium-ion. Red = battery/motion +; orange = 5 V +; black N = separate return to battery-negative bus.')
picture(d,'battery.png',45,190,240,340,(35,175,390,520))
text(d,45,565,'BT1: VOLTON 12 V / 45 Ah',23,True);text(d,45,595,'Selected product-family photo',17,color='#606e78')
port(d,285,370,'B+',RED);wire(d,[(285,370),(330,370)])
fuse(d,330,343,'F1 40 A*',130);wire(d,[(460,370),(500,370)])
d.box(500,330,150,82,'SW1',['Disconnect'],BLACK)
wire(d,[(650,370),(705,370)])
picture(d,'matek.jpg',705,245,300,180,(520,115,470,260))
text(d,705,225,'U6: MATEK I2C-INA-BM',23,True)
text(d,705,455,'BAT+ IN       ESC+ OUT',21,True,RED)
text(d,705,485,'Positive current passes through shunt',17)
wire(d,[(1005,370),(1040,370),(1040,1160)],RED)
text(d,950,535,'BATT_MON',20,True,RED,maxw=145)

picture(d,'contactor-user.png',1110,205,270,285,(1400,120,1350,1900))
text(d,1110,190,'K1: YOUR DC CONTACTOR',23,True)
text(d,1110,515,'Two LARGE studs = power path',19,True)
text(d,1110,544,'Small pair = coil; polarity TBD',18,color=GREEN)
wire(d,[(1040,370),(1110,370)])
wire(d,[(1380,370),(1430,370)])
d.box(1430,308,245,130,'U3: 12.0 V regulator',['Part / final current TBD','Keep until pack voltage verified','Connection labels: IN+ / OUT+'],RED,'#fff8f1',True)
n(d,1560,438)
text(d,1430,505,'IN- and OUT- → N',18)
wire(d,[(1675,370),(1730,370)])

d.box(1730,230,230,660,'FB1: 12 V MOTION',[],RED,'#fff8f8')
picture(d,'project-reference-render.png',1765,305,160,235,(820,555,190,380))
text(d,1750,565,'Reference render only',17,color='#667078')
text(d,1750,615,'F11 15 A  - WHEELS',20,True,RED,maxw=200)
text(d,1750,655,'F12 10 A* - ARM 1',20,True,RED,maxw=200)
text(d,1750,695,'F13 10 A* - ARM 2',20,True,RED,maxw=200)
text(d,1750,760,'Single positive input',18,maxw=200)
text(d,1750,790,'No negative bus inside',18,maxw=200)
text(d,1750,840,'Slot numbers: see labels',17,maxw=200)
for idx,y in enumerate([250,535,820]):
    picture(d,'adapter.jpg',2040,y,290,170)
    text(d,2040,y-15,['U30: WHEEL ADAPTER','U41: ARM 1 ADAPTER','U42: ARM 2 ADAPTER'][idx],23,True)
    wire(d,[(1960,370+idx*100),(2000+idx*10,370+idx*100),(2000+idx*10,y+160),(2040,y+160)])
    text(d,2040,y+195,'DC+ screw terminal',19,True,RED)
    text(d,2040,y+225,['To 4 wheel servos (2 chains)','To new 12 V arm 1 servos','To new 12 V arm 2 servos'][idx],18)
    n(d,2315,y+170)

# Always-on electronics stay before K1.
fuse(d,1110,675,'F3 5 A',130);wire(d,[(1040,702),(1110,702)])
wire(d,[(1240,702),(1340,702)])
picture(d,'jetson.png',1340,580,330,265)
text(d,1335,880,'U20: JETSON ORIN NANO',22,True,maxw=330)
text(d,1335,910,'SUPER DEVELOPER KIT',21,True,maxw=330)
text(d,1335,940,'DC jack 5.5 x 2.5 mm - centre +',19,maxw=330)
text(d,1335,970,'Stays powered after E-stop',19,True,GREEN,maxw=330)
n(d,1690,850)

# Coil feed is one NC mushroom; no reset module.
fuse(d,870,755,'F5 2 A*',130);wire(d,[(1040,782),(1000,782)],GREEN)
wire(d,[(870,782),(835,782),(835,850)],GREEN)
stop_icon(d,680,840)
wire(d,[(680,940),(625,940),(625,600),(1026,600)],GREEN)
wire(d,[(1054,600),(1150,600)],GREEN);port(d,1150,600,'K1 coil + (verify)',GREEN)
n(d,1300,600)
text(d,665,1050,'S1: push to LOCK / twist to RELEASE',23,True,GREEN)
text(d,665,1082,'Small coil current only - not motor current',18)

fuse(d,1080,1070,'F4 10 A',130);wire(d,[(1040,1097),(1080,1097)])
picture(d,'buck.jpg',1240,1000,290,245)
wire(d,[(1210,1097),(1240,1097)])
text(d,1225,1290,'U4: TOBSUN EA75-5V',23,True)
text(d,1225,1320,'IN+ / IN-  →  OUT+ 5 V / OUT-',19)
text(d,1225,1350,'Both IN- and OUT- → N',18,True)
wire(d,[(1530,1150),(1600,1150)],ORANGE)
d.box(1600,1050,260,290,'FB2: 5 V ONLY',[
    'F21 3 A* → hub 1','F22 3 A* → hub 2 (if fitted)',
    'F23 2 A* → U6 5V via J5','Hub inputs / plugs: VERIFY','Use no 12 V on this box'],ORANGE,'#fff9ee')
wire(d,[(1860,1150),(1910,1150)],ORANGE)
d.box(1910,1100,420,165,'HUBS / MONITOR 5 V',['Existing USB hub + optional second hub','U6 small 5V pin needs regulated 5 V','Detailed monitor wiring: sheet 3'],ORANGE,'#fff9ee')
n(d,1160,1245);n(d,1560,1245);n(d,2290,1265)

# Labelled star references keep the photograph layout uncluttered.
wire(d,[(170,535),(170,1385),(2290,1385)],BLACK)
text(d,230,1375,'N = BATTERY-NEGATIVE STAR BUS: one separate black wire from every device/converter return.',23,True,BLACK)
text(d,45,1435,'E-STOP PRESSED: wheels + both arms OFF. Jetson, hubs and monitor ON. Twist-release restores motor power immediately.',23,True,RED,maxw=2290)
text(d,45,1470,'Pictures show component appearance. Battery current limits, regulator model and actual terminal polarity are not inferred from appearance.',19,maxw=2290)
footer(d);finish(d)

# Sheet 2: exact circuit logic, photographed stud groups and NC behaviour.
d=b.Drawing('HAEBOT_EV_PHOTO_WIRING_02')
title(d,2,'2. E-stop + contactor - what connects where','One NC mechanically latching mushroom; no START button, auxiliary holding loop or reset controller.')
picture(d,'contactor-user.png',60,210,1000,650,(1150,80,1700,2050))
text(d,65,895,'Your photographed unit: label 500A DC12V',28,True)
text(d,65,935,'Identify the LARGE main studs and SMALL coil studs on the actual device.',22,maxw=1000)
text(d,65,970,'Do not assign + / - to a small stud from its left/right position in this picture.',22,True,RED,maxw=1000)

text(d,1160,225,'MAIN POWER - large studs',29,True,RED)
d.box(1160,265,420,110,'From protected BATT_MON',['After F1 + SW1 + Matek shunt'],RED)
d.box(1690,265,600,110,'K1 MAIN CONTACT → U3 → FB1',['Feed wheels, arm 1 and arm 2 from this path'],RED)
wire(d,[(1580,320),(1690,320)])
text(d,1160,445,'COIL CONTROL - small studs',29,True,GREEN)
fuse(d,1160,515,'F5 2 A*',160)
stop_icon(d,1410,465)
d.box(1720,490,570,145,'K1 COIL',['Positive: feed through the E-stop NC pair','Negative: return to battery-negative bus','Polarity / suppression / continuous duty: verify'],GREEN)
wire(d,[(1320,542),(1410,542)],GREEN)
wire(d,[(1600,542),(1720,542)],GREEN)
text(d,1160,475,'Fused control feed',21,True,GREEN)
wire(d,[(2230,635),(2230,730),(1160,730)],BLACK)
text(d,1160,768,'Battery negative / POWER_GND',23,True,BLACK)

d.box(65,1040,990,340,'USE THE NC CONTACT PAIR',[
    'Released/unpressed: NC contacts are CLOSED → coil receives power.',
    'Push: NC contacts OPEN → coil drops out → motor power is cut.',
    'Let go: mushroom stays locked down → motor power stays OFF.',
    'Twist to release: NC closes → coil energises → motor power returns.',
    'NC terminal numbers vary (for example 11-12 or 1-2). Read the block.',
    'Check continuity with all power disconnected before fitting the switch.'
],GREEN,'#f2faf5')
d.box(1160,870,1130,340,'BEFORE CONNECTING THE BATTERY',[
    'K1 must support continuous coil energisation at the actual pack voltage.',
    'Verify the coil current before accepting the 2 A control fuse / switch rating.',
    'D1 suppression is still TBD: follow the contactor manufacturer, not a guessed diode.',
    'The red mushroom is an illustration of the required type, not a selected product.',
    'This simple circuit has NO restart interlock; restoring supply also enables power.',
    'Arm holding torque disappears when power is cut; support arms during first tests.'
],RED,'#fff8f5')
text(d,1160,1280,'A 500 A label alone does not establish DC breaking capability.',23,True,RED)
text(d,1160,1325,'A welded K1 contact can defeat this single-contactor power cut.',23,True,RED)
footer(d);finish(d)

# Sheet 3: monitor and servo-board reference connectors.
d=b.Drawing('HAEBOT_EV_PHOTO_WIRING_03')
title(d,3,'3. Matek + servo adapter connection close-ups','Photographs identify the connectors. The monitor is I2C, not USB. Actual Jetson header pins / pull-ups / driver remain unverified.')
picture(d,'matek.jpg',60,230,1160,465)
text(d,60,210,'U6: BAT+ is the battery side; ESC+ is the load side',27,True,RED)
text(d,60,745,'BAT+ ← SW1 / main fuse       ESC+ → all discharge branches',24,True,RED)
text(d,60,785,'Black heavy cable in the manufacturer photo bypasses the positive shunt.',21)
text(d,60,820,'The included small JST harness is for electronics and I2C only.',21,True)
text(d,60,855,'Connector position varies with board orientation. Read 5V / G / SDA / SCL.',21)

labels=[('5V','FB2 F23 → J5 AUX_5V (regulated 5 V)',ORANGE),('G','POWER_GND / negative star bus',BLACK),('SDA','Jetson I2C SDA — actual header pin TBD',BLUE),('SCL','Jetson I2C SCL — actual header pin TBD',PURPLE)]
for i,(label,dest,color) in enumerate(labels):
    y=275+i*120
    d.box(1320,y,130,65,label,[],color)
    wire(d,[(1450,y+32),(1550,y+32)],color)
    text(d,1580,y+43,dest,23,True,color,maxw=720)
text(d,1320,825,'Default address 0x45; INA228 / INA238 fitted variant: verify.',22,True)
text(d,1320,865,'No raw battery voltage on 5V or any Jetson GPIO pin.',22,True,RED)
wire(d,[(50,905),(2340,905)],'#b0bdc6')

picture(d,'adapter.jpg',1140,940,640,480)
text(d,65,975,'U30 / U41 / U42 - same adapter type',28,True)
text(d,65,1020,'Use the GREEN SCREW TERMINAL for motor power.',24,True)
text(d,65,1070,'DC+ ← the correct FB1 fused output:',23,True,RED)
text(d,95,1112,'F11: wheels  |  F12: arm 1  |  F13: arm 2',22,True)
text(d,65,1162,'DC- → its own black wire to the negative star bus.',23,True)
text(d,65,1212,'USB-C ← USB hub (communication / board logic).',23)
text(d,65,1262,'White D / V / G ports → matched 3-wire servo leads.',23)
text(d,65,1312,'Wheels: port 1 → IDs 7 → 9; port 2 → IDs 8 → 10.',23)
text(d,65,1362,'Both arm adapters now feed NEW 12 V servos only.',23,True,RED)
text(d,1820,990,'REFERENCE BOARD PHOTO',22,True)
text(d,1820,1035,'Green terminal: DC+ / DC-',21)
text(d,1820,1075,'USB-C: data from hub',21)
text(d,1820,1115,'White connectors: servo bus',21)
text(d,1820,1170,'Verify actual board type',22,True,RED)
text(d,1820,1210,'and terminal markings.',22,True,RED)
text(d,65,1450,'Photo sources and unresolved hardware details are listed in photo-wiring/README.md. Charging remains a separate inlet before SW1.',19)
footer(d);finish(d)

writer=PdfWriter()
for i in range(1,4):
    for page in PdfReader(ROOT/'exports'/f'HAEBOT_EV_PHOTO_WIRING_0{i}.pdf').pages:writer.add_page(page)
writer.add_metadata({'/Title':'HAEBOT / KIRO - Photo Wiring Guide (Rev B supplement)','/Author':'HAEBOT / KIRO project'})
with (ROOT/'exports'/'HAEBOT_EV_PHOTO_WIRING_GUIDE.pdf').open('wb') as f:writer.write(f)
for i in range(1,4):
    (ROOT/'exports'/f'HAEBOT_EV_PHOTO_WIRING_0{i}.pdf').unlink()
print('Created 3-page photo guide and embedded-photo SVG sources; temporary page PDFs removed.')
