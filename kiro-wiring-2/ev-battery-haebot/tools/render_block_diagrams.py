"""Render matching English/Korean Rev B vector diagrams (SVG + embedded-font PDF).

Run with Python + ReportLab. Override Windows font paths with --font and --bold-font.
This script never reads or writes KiCad source files.
"""
from pathlib import Path
from html import escape
import argparse
import math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[1]
W,H=1600,1120
PWR='#a32c32'; MOT='#cb263b'; FIVE='#c56a05'; CTL='#26744b'; DATA='#6350a8'

class Drawing:
    def __init__(self, stem, korean=False):
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="294mm" viewBox="0 0 {W} {H}" font-family="Malgun Gothic, Noto Sans CJK KR, Arial, sans-serif">', '<rect width="1600" height="1120" fill="white"/>']
        self.pdf=canvas.Canvas(str(ROOT/'exports'/f'{stem}.pdf'),pagesize=(W*.75,H*.75))
        self.pdf.setTitle('HAEBOT EV Rev B - '+('한국어 전원 블록도' if korean else 'English power block diagram'))
        self.pdf.setAuthor('HAEBOT / KIRO project')
        self.pdf.scale(.75,.75)
        self.stem=stem
    def rect(self,x,y,w,h,fill='#ffffff',stroke='#b5c3cf',dash=False):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"'+(' stroke-dasharray="6 4"' if dash else '')+'/>')
        self.pdf.setFillColor(HexColor(fill)); self.pdf.setStrokeColor(HexColor(stroke)); self.pdf.setLineWidth(1.6)
        self.pdf.setDash([6,4] if dash else [])
        self.pdf.roundRect(x,H-y-h,w,h,8,stroke=1,fill=1)
    def text(self,x,y,s,size=16,bold=False,color='#183249',maxw=None):
        font='DiagramBold' if bold else 'Diagram'
        if maxw:
            size=min(size, maxw/pdfmetrics.stringWidth(s,font,size)*size) if s else size
        if size<10:
            raise ValueError(f'Text too small: {s}')
        assert 0<=x<=W and 0<=y<=H, s
        self.svg.append(f'<text x="{x}" y="{y}" font-size="{size:.2f}" font-weight="'+('bold' if bold else 'normal')+f'" fill="{color}">{escape(s)}</text>')
        self.pdf.setFillColor(HexColor(color)); self.pdf.setFont(font,size); self.pdf.drawString(x,H-y,s)
    def box(self,x,y,w,h,title,lines=(),color='#183249',fill='#f7fafc',dash=False):
        self.rect(x,y,w,h,fill,color,dash)
        self.text(x+14,y+28,title,18,True,color,maxw=w-28)
        for i,line in enumerate(lines): self.text(x+14,y+52+i*21,line,15,maxw=w-28)
    def line(self,points,color=PWR,dash=False,arrow=True):
        self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
        self.pdf.setStrokeColor(HexColor(color));self.pdf.setLineWidth(3);self.pdf.setDash([7,5] if dash else [])
        p=self.pdf.beginPath();p.moveTo(points[0][0],H-points[0][1])
        for x,y in points[1:]:p.lineTo(x,H-y)
        self.pdf.drawPath(p)
        if arrow:
            x,y=points[-1]; x0,y0=points[-2]; a=math.atan2(y-y0,x-x0)
            tri=[(x,y),(x-11*math.cos(a)+5*math.sin(a),y-11*math.sin(a)-5*math.cos(a)),(x-11*math.cos(a)-5*math.sin(a),y-11*math.sin(a)+5*math.cos(a))]
            self.svg.append('<polygon points="'+' '.join(f'{i:.2f},{j:.2f}' for i,j in tri)+f'" fill="{color}"/>')
            p=self.pdf.beginPath();p.moveTo(tri[0][0],H-tri[0][1])
            for i,j in tri[1:]:p.lineTo(i,H-j)
            p.close();self.pdf.setFillColor(HexColor(color));self.pdf.drawPath(p,stroke=0,fill=1)
    def dot(self,x,y):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{PWR}"/>')
        self.pdf.setFillColor(HexColor(PWR));self.pdf.circle(x,H-y,5,stroke=0,fill=1)
    def finish(self):
        self.svg.append('</svg>')
        (ROOT/'block-diagrams'/f'{self.stem}.svg').write_text('\n'.join(self.svg)+'\n',encoding='utf-8')
        self.pdf.showPage();self.pdf.save()

def render(ko):
    def t(en,kr):return kr if ko else en
    stem='HAEBOT_EV_BLOCK_DIAGRAM'+('_KO' if ko else '')
    d=Drawing(stem,ko)
    d.rect(25,24,1550,1055,stroke='#183249')
    d.text(48,66,t('HAEBOT / KIRO - EV battery wiring','HAEBOT / KIRO - EV 배터리 배선 구성도'),29,True)
    d.text(48,97,t('Rev B | 2026-11-26 | Both new arms: 12 V | One latching NC E-stop + DC contactor + Matek monitor','Rev B | 2026-11-26 | 새 로봇팔 2개: 12 V | 래칭 NC 비상정지 1개 + DC 접촉기 + Matek 모니터'),17,maxw=1490)
    d.text(48,122,t('PROPOSED: battery, coil duty/current, I2C hookup and final protection ratings still require verification.','제안 설계: 배터리, 코일 연속 통전/전류, I2C 연결 및 최종 보호 정격은 확인 필요.'),15,color=PWR)

    d.box(48,165,170,110,'BT1', [t('12 V / 45 Ah battery','12 V / 45 Ah 배터리'),t('Chemistry / BMS: TBD','화학계 / BMS: 미확인'),t('Range: verify label','전압 범위: 라벨 확인')],PWR, '#fff7ee',True)
    d.box(250,180,115,80,'F1',[t('40 A* main','40 A* 메인')],PWR)
    d.box(397,180,130,80,'SW1',[t('Disconnect','메인 차단기')],PWR)
    d.box(560,158,230,124,'U6 Matek I2C-INA-BM',[t('BAT+ → shunt → ESC+','BAT+ → 션트 → ESC+'),t('0-85 V / 150 A continuous','0-85 V / 연속 150 A'),t('Small pins: 5V G SDA SCL','소신호 핀: 5V G SDA SCL')],DATA)
    d.line([(218,220),(250,220)]);d.line([(365,220),(397,220)]);d.line([(527,220),(560,220)])
    d.line([(790,220),(825,220),(825,750)],arrow=False)
    d.text(851,231,t('BATT_MON: branch supply after monitor','BATT_MON: 모니터 뒤 분기 전원'),15,color=PWR)

    d.box(875,295,180,110,'K1',[t('Main NO contact','메인 NO 접점'),t('Photo: 500A DC12V','사진 라벨: 500A DC12V'),t('Duty / rating: TBD','연속 통전 / 정격 미확인')],MOT,'#fff5f5',True)
    d.box(1090,295,195,110,'U3',[t('12.0 V regulator','12.0 V 정전압 장치'),t('≥20 A* candidate','≥20 A* 후보'),t('Battery-dependent','배터리에 따라 필요')],MOT)
    d.box(1320,295,230,190,t('FB1: 12 V MOTION','FB1: 12 V 구동'),[
        t('F11 15 A → wheel adapter','F11 15 A → 바퀴 어댑터'),t('→ 4 wheel servos','→ 바퀴 서보 4개'),
        t('F12 10 A* → arm 1 adapter','F12 10 A* → 팔 1 어댑터'),t('→ new 12 V arm 1','→ 새 12 V 팔 1'),
        t('F13 10 A* → arm 2 adapter','F13 10 A* → 팔 2 어댑터'),t('→ new 12 V arm 2','→ 새 12 V 팔 2')],MOT,'#fff5f5')
    d.dot(825,350);d.line([(825,350),(875,350)]);d.line([(1055,350),(1090,350)],MOT);d.line([(1285,350),(1320,350)],MOT)
    d.text(875,443,t('K1 opens: wheels + BOTH arms lose motor power.','K1 개방: 바퀴와 양쪽 팔의 모터 전원 차단.'),17,True,MOT,maxw=420)
    d.text(875,468,t('U3 retained until full battery/servo voltage compatibility is verified.','배터리 전체 전압 범위와 서보 호환성 확인 전까지 U3 유지.'),14,maxw=420)

    d.box(875,523,410,93,t('F3 5 A → U20 Jetson Orin Nano Super','F3 5 A → U20 Jetson Orin Nano Super'),[
        t('DC jack: 9-20 V | cameras directly on USB','DC 잭: 9-20 V | 카메라는 USB 직접 연결'),t('I2C GPIO: physical pins / bus / driver TBD','I2C GPIO: 실제 핀 / 버스 / 드라이버 미확인')],DATA)
    d.dot(825,570);d.line([(825,570),(875,570)])
    d.line([(675,282),(675,595),(814,595)],DATA,True,False)
    d.line([(836,595),(875,595)],DATA,True)
    d.text(685,505,t('SDA / SCL + G reference','SDA / SCL + G 기준'),14,color=DATA,maxw=125)
    d.text(685,526,t('I2C, not USB','I2C, USB 아님'),14,color=DATA,maxw=125)

    d.box(875,674,260,109,'F4 10 A → U4 EA75-5V',[
        t('8-40 V input → 5 V / 15 A','8-40 V 입력 → 5 V / 15 A'),t('Stays on after E-stop','비상정지 후에도 전원 유지'),t('Measure 5.0-5.2 V first','먼저 5.0-5.2 V 측정')],FIVE,'#fff9ed')
    d.box(1170,674,380,130,t('FB2: 5 V ONLY','FB2: 5 V 전용'),[
        t('F21 3 A* → hub 1; F22 3 A* → hub 2','F21 3 A* → 허브 1; F22 3 A* → 허브 2'),
        t('Hub inputs / second hub presence: TBD','허브 입력 전압 / 허브 2 장착 여부: 미확인'),
        t('F23 2 A* → J5 → U6 5V + auxiliary','F23 2 A* → J5 → U6 5V + 보조 전원'),
        t('U6 logic: 5 V only; not battery voltage','U6 회로 전원: 5 V, 배터리 직결 금지')],FIVE,'#fff9ed')
    d.dot(825,730);d.line([(825,730),(875,730)]);d.line([(1135,730),(1170,730)],FIVE)
    d.text(875,831,t('USB data: Jetson ↔ hubs ↔ 3 servo adapters + lidar; no motor return through USB.','USB 데이터: Jetson ↔ 허브 ↔ 서보 어댑터 3개 + 라이다; USB로 모터 전류 귀환 금지.'),14,maxw=675)

    d.box(48,335,555,105,t('J2 CHARGING (unchanged)','J2 충전 (기존 구성 유지)'),[
        t('Charger → F2 15 A* → battery side of SW1','충전기 → F2 15 A* → SW1의 배터리 측'),
        t('Charge only with SW1 OFF and the matching charger.','SW1 OFF 상태에서 배터리에 맞는 충전기로만 충전.'),
        t('U6 placement measures discharge, not charging.','이 U6 위치는 방전만 측정하며 충전 전류는 측정하지 않음.')],PWR)
    d.box(48,470,555,165,t('POWER / SIGNAL NOTES','전원 / 신호 주의사항'),[
        t('Each return → POWER_GND star bus → battery negative.','각 장치 귀환선 → POWER_GND 스타 버스 → 배터리 음극.'),
        t('U6 high-current solder pads: main positive current only.','U6 대전류 납땜 패드: 메인 양극 전류 경로.'),
        t('JST pins: 5 V electronics + I2C only; ground at star bus.','JST 핀: 5 V 회로 전원과 I2C 전용; G는 음극 스타 버스.'),
        t('Check actual INA228/INA238, GPIO levels and pull-ups.','실제 INA228/INA238, GPIO 전압 및 풀업 확인 필요.'),
        t('Default I2C address: decimal 69 / hex 0x45.','기본 I2C 주소: 10진수 69 / 16진수 0x45.')],DATA)
    d.box(48,665,555,150,t('WHAT THE STOP DOES','비상정지 동작'),[
        t('Released NC → coil powered → motion power ON.','NC 해제 상태 → 코일 통전 → 구동 전원 ON.'),
        t('Push / lock → coil OFF → wheels + arms OFF.','누름 / 잠금 → 코일 OFF → 바퀴와 팔 전원 OFF.'),
        t('Mechanical latch holds OFF until twist release.','기계식 래치가 돌려 해제할 때까지 OFF 유지.'),
        t('Jetson, hubs and monitor remain ON.','Jetson, 허브 및 모니터 전원은 ON 유지.')],CTL,'#f2faf5')

    d.text(48,867,t('HARDWARE COIL CONTROL - one latching NC E-stop, no START / RESET or auxiliary holding loop','하드웨어 코일 제어 - 래칭 NC 비상정지 1개, START / RESET 버튼 및 보조 유지 회로 없음'),18,True,CTL,maxw=1490)
    d.box(48,891,205,75,'BATT_MON',[t('After main protection','메인 보호 장치 이후')],PWR)
    d.box(290,891,165,75,'F5 2 A*',[t('Coil fuse: TBD','코일 퓨즈: 확인 필요')],CTL)
    d.box(492,891,315,75,t('S1: latching NC E-STOP','S1: 래칭 NC 비상정지'),[t('Push to lock / twist to release','눌러 잠금 / 돌려 해제')],CTL,'#f2faf5')
    d.box(844,891,280,75,t('K1 COIL (small terminals)','K1 코일 (소형 단자)'),[t('Polarity / suppression: verify','극성 / 서지 억제 방식 확인')],CTL)
    d.box(1161,891,389,75,'POWER_GND',[t('Battery-negative star bus','배터리 음극 스타 버스')],CTL)
    for a,b in [(253,290),(455,492),(807,844),(1124,1161)]:d.line([(a,929),(b,929)],CTL)
    d.text(48,1004,t('TWIST RELEASE RESTORES MOTOR POWER IMMEDIATELY. No restart interlock. Arms may fall when torque is lost.','돌려 해제하면 모터 전원이 즉시 복구됩니다. 재시작 인터록 없음. 토크 상실 시 팔이 떨어질 수 있습니다.'),18,True,MOT,maxw=1490)
    d.text(48,1032,t('* Preliminary fuse/converter ratings. Single-contactor prototype power cut; not a validated safety system.','* 퓨즈 및 컨버터 정격은 잠정값. 단일 접촉기 시제품 전원 차단 구성으로 안전 기능 검증은 완료되지 않음.'),14,color=PWR,maxw=1490)
    d.text(48,1056,t('Source: project Rev B wiring table + Matek manufacturer specifications. Physical pins and final ratings require confirmation.','근거: 프로젝트 Rev B 배선표 + Matek 제조사 사양. 실제 핀 배열과 최종 정격 확인 필요.'),12,maxw=1490)
    d.finish()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--font',default='C:/Windows/Fonts/malgun.ttf')
    parser.add_argument('--bold-font',default='C:/Windows/Fonts/malgunbd.ttf')
    args=parser.parse_args()
    pdfmetrics.registerFont(TTFont('Diagram',args.font));pdfmetrics.registerFont(TTFont('DiagramBold',args.bold_font))
    for language in [False,True]:render(language)
    print('Rendered English/Korean SVG and embedded-font PDF diagrams.')
