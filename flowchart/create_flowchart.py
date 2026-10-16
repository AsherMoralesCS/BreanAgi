from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path
import math
OUT=Path(__file__).resolve().parent
c=canvas.Canvas(str(OUT/'TraverseCraft_Flowchart.pdf'),pagesize=(900,1200))
c.setTitle('TraverseCraft — Program Flowchart')
INK=HexColor('#182838'); BLUE=HexColor('#eaf1fb'); GRAY=HexColor('#f6f7f9')
def text(x,y,s,size=12):
    c.setFillColor(INK); c.setFont('Helvetica',size)
    for i,line in enumerate(s.split('\n')):c.drawCentredString(x,y+(len(s.split('\n'))-1)*size*.6-i*size*1.2,line)
def box(x,y,s,w=290,h=56,kind='process',size=12):
    c.setStrokeColor(INK);c.setLineWidth(1);c.setFillColor(BLUE if kind=='decision' else GRAY)
    if kind=='connector':c.setFillColor(white);c.circle(x,y,17,stroke=1,fill=1)
    elif kind=='term':c.roundRect(x-w/2,y-h/2,w,h,h/2,stroke=1,fill=1)
    elif kind=='decision':
        p=c.beginPath();p.moveTo(x,y+h/2);p.lineTo(x+w/2,y);p.lineTo(x,y-h/2);p.lineTo(x-w/2,y);p.close();c.drawPath(p,stroke=1,fill=1)
    elif kind=='io':
        p=c.beginPath();p.moveTo(x-w/2+12,y+h/2);p.lineTo(x+w/2,y+h/2);p.lineTo(x+w/2-12,y-h/2);p.lineTo(x-w/2,y-h/2);p.close();c.drawPath(p,stroke=1,fill=1)
    else:
        c.rect(x-w/2,y-h/2,w,h,stroke=1,fill=1)
        if kind=='sub':
            for d in [-w/2+7,w/2-7]:c.line(x+d,y-h/2,x+d,y+h/2)
    text(x,y-4,s,size)
def arrow(points,label=None,lpos=None):
    c.setStrokeColor(INK);c.setFillColor(INK);c.setLineWidth(1)
    p=c.beginPath();p.moveTo(*points[0])
    for q in points[1:]:p.lineTo(*q)
    c.drawPath(p)
    a,b=points[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);p=c.beginPath();p.moveTo(*b)
    for off in [-.45,.45]:p.lineTo(b[0]-7*math.cos(ang+off),b[1]-7*math.sin(ang+off))
    p.close();c.drawPath(p,fill=1,stroke=0)
    if label:
        x,y=lpos or ((a[0]+b[0])/2+20,(a[1]+b[1])/2);text(x,y,label,10)
def conn(x,y,label):box(x,y,label,kind='connector')
def page(n,title):
    c.setFillColor(INK);c.setFont('Helvetica-Bold',19);c.drawString(45,1150,title)
    c.setFont('Helvetica',10);c.drawString(45,1127,'TraverseCraft: Missing Data Calculator & Plotter')
    c.setStrokeColor(HexColor('#ccd5de'));c.line(45,1110,855,1110)
    text(450,35,f'{n} / 3  |  Matching lettered circles connect flow across pages.',10)
# 1
page(1,'User interface')
box(450,1060,'Start',w=110,h=36,kind='term')
box(450,985,'root = tk.Tk()\nTraverseApp(root)',kind='sub')
arrow([(450,1042),(450,1013)])
box(450,905,'show_menu()\nSelect the traverse case to work on',kind='io')
arrow([(450,957),(450,933)])
conn(220,905,'M');arrow([(237,905),(305,905)])
box(450,820,'open_case(index)\nreset()',kind='sub');arrow([(450,877),(450,848)])
box(450,715,'root.mainloop()',w=300,h=85,kind='decision');arrow([(450,792),(450,757.5)])
conn(220,715,'R');arrow([(237,715),(300,715)])
# action routes
for x,label,letter in [(120,'Add Line','A'),(360,'Solve Omitted Measurements','S'),(650,'Remove Selected','D')]:
    start= [(450,672.5),(450,625),(x,625),(x,565)] if x!=650 else [(600,715),(780,715),(780,625),(650,625),(650,565)]
    arrow(start,label,(x,642));conn(x,548,letter)
# other actions via right/left tracks
box(180,410,'reset()\nrefresh()',w=220,kind='sub');arrow([(450,625),(180,625),(180,438)],'Reset',(210,480));conn(180,327,'R');arrow([(180,382),(180,344)])
box(500,410,'clear_all()\nRemove every line from the table?\nThis can\'t be undone.',w=340,h=72,kind='sub');arrow([(450,625),(500,625),(500,446)],'Clear All',(530,495));conn(500,327,'R');arrow([(500,374),(500,344)])
box(720,230,'show_menu()',w=200,kind='sub');arrow([(450,672.5),(450,605),(845,605),(845,230),(820,230)],'Return',(790,300));conn(720,145,'M');arrow([(720,202),(720,162)])
box(180,145,'End',w=110,h=36,kind='term');arrow([(450,757.5),(450,775),(35,775),(35,145),(125,145)],'return',(72,180))
text(450,80,'Reset, Clear All and Remove Selected continue through their callbacks; see page 2.',10)
c.showPage()
#2
page(2,'Input and table actions')
conn(270,1060,'A');box(270,980,'Add a traverse line\n(use Unknown for omitted values)',kind='io',w=360)
arrow([(270,1043),(270,1008)])
box(270,880,'all(texts)',kind='decision',w=230,h=76);arrow([(270,952),(270,918)])
box(660,880,'Please fill in all input fields.',kind='io',w=300);arrow([(385,880),(510,880)],'False',(445,898));conn(660,800,'R');arrow([(660,852),(660,817)])
box(270,770,'Line.from_text(*texts)\nBearing.parse(bearing_text)',kind='sub',w=340);arrow([(270,842),(270,798)],'True',(296,817))
box(660,700,'Invalid input\nstr(error)',kind='io',w=260);arrow([(440,770),(660,770),(660,728)],'ValueError',(550,788));conn(660,620,'R');arrow([(660,672),(660,637)])
box(270,660,'self.traverse.add(line)\nself.solved = set()',w=340);arrow([(270,742),(270,688)])
box(270,565,'refresh()\ndraw_plot()',kind='sub',w=340);arrow([(270,632),(270,593)])
conn(270,485,'R');arrow([(270,537),(270,502)])
# bottom remove and clear details
conn(200,385,'D');box(200,310,'selected',w=210,h=68,kind='decision');arrow([(200,368),(200,344)])
box(200,205,'self.traverse.remove(selected)\nrefresh()',w=320,kind='sub');arrow([(200,276),(200,233)],'True',(227,251));conn(200,115,'R');arrow([(200,177),(200,132)])
conn(430,310,'R');arrow([(305,310),(413,310)],'False',(355,328))
box(660,365,'clear_all()',w=240,kind='sub')
box(660,270,'messagebox.askyesno()',w=290,h=78,kind='decision');arrow([(660,337),(660,309)])
box(660,175,'reset()\nrefresh()',w=240,kind='sub');arrow([(660,231),(660,203)],'True',(685,215));conn(660,95,'R');arrow([(660,147),(660,112)])
conn(835,270,'R');arrow([(805,270),(818,270)],'False',(822,300))
text(660,422,'self.traverse.lines',11)
text(660,398,'False: reset()    True: messagebox.askyesno()',10)
c.showPage()
#3
page(3,'Solve Omitted Measurements')
conn(450,1065,'S');box(450,1000,'self.traverse.solve()',kind='sub');arrow([(450,1048),(450,1028)])
box(450,925,'omitted',w=230,h=64,kind='decision');arrow([(450,972),(450,957)])
box(730,925,'No omitted measurements found -\nnothing to solve.',w=270,kind='io');arrow([(565,925),(595,925)],'False',(585,965));conn(730,850,'E');arrow([(730,897),(730,867)])
box(320,820,'line.components()\nclosing = (-known_lat, -known_dep)',w=350,kind='sub');arrow([(450,893),(450,870),(320,870),(320,848)],'True',(350,878))
box(320,730,'len(omitted)',w=240,h=70,kind='decision');arrow([(320,792),(320,765)])
box(130,620,'_solve_one_side(omitted[0], closing)',w=250,h=62,kind='sub',size=10);arrow([(200,730),(130,730),(130,651)],'1',(150,748))
box(510,620,'_solve_two_sides(omitted, closing)',w=310,h=62,kind='sub',size=11);arrow([(440,730),(510,730),(510,651)],'2',(485,748))
conn(780,730,'E');arrow([(440,730),(763,730)],'else',(705,748))
box(510,510,'kinds',w=210,h=64,kind='decision');arrow([(510,589),(510,542)])
for x,y,label,s in [(170,410,'{"length"}','_solve_two_lengths(i, j, closing)'),(510,410,'{"bearing"}','_solve_two_bearings(i, j, closing)'),(720,310,'{"length", "bearing"}','_solve_length_and_bearing(i, j, closing)')]:
    box(x,y,s,w=310 if x!=720 else 330,h=48,kind='sub',size=10)
    if x==170:arrow([(405,510),(170,510),(170,434)],label,(250,527))
    elif x==510:arrow([(510,478),(510,434)],label,(560,458))
    else:arrow([(615,510),(720,510),(720,334)],label,(740,540))
conn(825,450,'E');arrow([(720,510),(825,510),(825,467)],'else',(825,535))
box(320,205,"Prefer one that doesn't cross itself.\nself.is_simple(trial)\nself.lines[k] = line",w=350,h=74,kind='sub')
arrow([(130,589),(45,589),(45,260),(320,260),(320,242)])
arrow([(170,386),(170,260)])
arrow([(510,386),(510,260),(320,260)])
arrow([(720,286),(720,260),(510,260)])
box(320,110,'refresh()\ndraw_plot()',w=240,h=50,kind='sub');arrow([(320,168),(320,135)])
conn(490,110,'R');arrow([(440,110),(473,110)])
conn(635,205,'E');box(745,135,'Cannot solve\nstr(error)',w=210,h=56,kind='io');arrow([(652,205),(745,205),(745,163)]);conn(745,65,'R');arrow([(745,107),(745,82)])
text(345,65,'ValueError / not options: E',10)
c.save()
print(OUT/'TraverseCraft_Flowchart.pdf')
