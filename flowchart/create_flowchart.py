"""Generate the source-based A4 flowchart. Requires reportlab."""
from pathlib import Path
from xml.sax.saxutils import escape
import math

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = A4
MARGIN = 73.0  # 72 points = one inch; allow for border strokes.
CENTER = WIDTH / 2
INK = '#203249'
PALETTE = {
    'term': ('#dcfce7', '#15803d'),
    'process': ('#dbeafe', '#2563eb'),
    'sub': ('#ede9fe', '#6d28d9'),
    'decision': ('#fef3c7', '#96630a'),
    'io': ('#ccfbf1', '#0f766e'),
    'error': ('#ffe4e6', '#be123c'),
    'raise': ('#ffe4e6', '#be123c'),
}
CONNECTOR_COLORS = {
    'R': ('#1d4ed8', '#ffffff'),  # Return to the event loop
    'Z': ('#facc15', '#203249'),  # Reset
    'M': ('#7c3aed', '#ffffff'),  # Return to the menu
    'A': ('#047857', '#ffffff'),  # Add Line
    'S': ('#0e7490', '#ffffff'),  # Solve
    'D': ('#c2410c', '#ffffff'),  # Remove Selected
    'C': ('#be185d', '#ffffff'),  # Clear All
    'V': ('#475569', '#ffffff'),  # Refresh table and plot
    'P': ('#854d0e', '#ffffff'),  # Candidate solution selection
    'E': ('#b91c1c', '#ffffff'),  # ValueError handling
    'K': ('#4d7c0f', '#ffffff'),  # Open the selected case
    'L': ('#4338ca', '#ffffff'),  # One omitted side
    'T': ('#075985', '#ffffff'),  # Two omitted sides
}
C = canvas.Canvas(str(OUT / 'TraverseCraft_Flowchart.pdf'), pagesize=A4)
C.setTitle('Program flowchart')
C.setAuthor('')
BOUNDS = []
NODES = []
PAGE = 0
RADIUS = 10
STEP_STYLE = ParagraphStyle('steps', fontName='Helvetica', fontSize=10,
                            leading=12.5, textColor=HexColor(INK))


def wrap(value, width, size=10.5, font='Helvetica'):
    result = []
    for paragraph in value.split('\n'):
        line = ''
        for word in paragraph.split():
            trial = f'{line} {word}'.strip()
            if line and stringWidth(trial, font, size) > width:
                result.append(line)
                line = word
            else:
                line = trial
        result.append(line)
    assert all(stringWidth(line, font, size) <= width + .01 for line in result), value
    return result


def record(x0, y0, x1, y1):
    BOUNDS.append((x0, y0, x1, y1))


def text(x, baseline, value, size=10.5, color=INK, font='Helvetica', center=True):
    C.setFillColor(HexColor(color))
    C.setFont(font, size)
    if center:
        C.drawCentredString(x, baseline, value)
        half = stringWidth(value, font, size)/2
        record(x-half, baseline-3, x+half, baseline+size)
    else:
        C.drawString(x, baseline, value)
        record(x, baseline-3, x+stringWidth(value, font, size), baseline+size)


def node(x, y, label, ref='', w=190, h=65, kind='process'):
    fill, stroke = PALETTE[kind]
    C.setFillColor(HexColor(fill)); C.setStrokeColor(HexColor(stroke)); C.setLineWidth(1)
    if kind == 'term':
        C.roundRect(x-w/2, y-h/2, w, h, h/2, stroke=1, fill=1)
    elif kind == 'decision':
        p=C.beginPath(); p.moveTo(x,y+h/2)
        for pt in [(x+w/2,y),(x,y-h/2),(x-w/2,y)]:p.lineTo(*pt)
        p.close();C.drawPath(p,stroke=1,fill=1)
    elif kind in ('io','error'):
        p=C.beginPath();p.moveTo(x-w/2+7,y+h/2)
        for pt in [(x+w/2,y+h/2),(x+w/2-7,y-h/2),(x-w/2,y-h/2)]:p.lineTo(*pt)
        p.close();C.drawPath(p,stroke=1,fill=1)
    else:
        C.roundRect(x-w/2,y-h/2,w,h,3,stroke=1,fill=1)
        if kind=='sub':
            for dx in (-w/2+5,w/2-5):C.line(x+dx,y-h/2+3,x+dx,y+h/2-3)
    main=wrap(label, w-20 if kind!='decision' else w*.65)
    refs=wrap(ref,w-18,10) if ref else []
    total=len(main)*13.1 + (4+len(refs)*12.5 if refs else 0)
    assert total<=h-9,(PAGE,label,total,h)
    baseline=y+total/2-10.5
    for i,line in enumerate(main):text(x,baseline-i*13.1,line)
    for i,line in enumerate(refs):text(x,baseline-len(main)*13.1-4-i*12.5,line,10,stroke)
    record(x-w/2-.5,y-h/2-.5,x+w/2+.5,y+h/2+.5)
    NODES.append((x-w/2,y-h/2,x+w/2,y+h/2,label))


def connector(x,y,label):
    fill,letter=CONNECTOR_COLORS[label]
    C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(fill));C.setLineWidth(1)
    C.circle(x,y,RADIUS,stroke=1,fill=1)
    text(x,y-3.5,label,10.5,letter,'Helvetica-Bold')
    record(x-RADIUS-.5,y-RADIUS-.5,x+RADIUS+.5,y+RADIUS+.5)
    NODES.append((x-RADIUS,y-RADIUS,x+RADIUS,y+RADIUS,label))


def edge(points,label='',at=None,color=INK,arrow=True):
    C.setStrokeColor(HexColor(color));C.setFillColor(HexColor(color));C.setLineWidth(.85)
    p=C.beginPath();p.moveTo(*points[0])
    for pt in points[1:]:p.lineTo(*pt)
    C.drawPath(p)
    if arrow:
        a,b=points[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0])
        p=C.beginPath();p.moveTo(*b)
        for off in (-.45,.45):p.lineTo(b[0]-5*math.cos(angle+off),b[1]-5*math.sin(angle+off))
        p.close();C.drawPath(p,stroke=0,fill=1)
    for x,y in points:record(x-.5,y-.5,x+.5,y+.5)
    if label:
        for i,line in enumerate(label.split('\n')):text(at[0],at[1]-i*12.5,line,10,color)


def page(title,steps):
    global PAGE
    PAGE+=1
    text(MARGIN,752,f'{PAGE}  {title}',16,font='Helvetica-Bold',center=False)
    C.setStrokeColor(HexColor('#cbd5e1'));C.setLineWidth(.6)
    C.line(MARGIN,742,WIDTH-MARGIN,742);record(MARGIN-.3,741.7,WIDTH-MARGIN+.3,742.3)
    # A bordered content section, not a page footer.
    x,y,w,h=MARGIN,73,WIDTH-2*MARGIN,150
    C.setStrokeColor(HexColor('#94a3b8'));C.setFillColor(HexColor('#f8fafc'));C.setLineWidth(.65)
    C.roundRect(x,y,w,h,3,stroke=1,fill=1)
    record(x-.325,y-.325,x+w+.325,y+h+.325)
    text(x+10,y+h-17,'NUMBERED STEPS',10,font='Helvetica-Bold',center=False)
    col_w=(w-30)/2
    for i,(heading,description) in enumerate(steps):
        col=i//2;row=i%2
        assert col<2
        paragraph=Paragraph(f'<b>{i+1}. {escape(heading)}</b> {escape(description)}',STEP_STYLE)
        _,ph=paragraph.wrap(col_w,120)
        px=x+10+col*(col_w+10);top=y+h-30-row*55
        assert ph<=52,(PAGE,i,ph)
        paragraph.drawOn(C,px,top-ph)
        record(px,top-ph,px+col_w,top)


def finish():
    for x0,y0,x1,y1 in BOUNDS:
        assert 72<=x0<=x1<=WIDTH-72,(PAGE,'horizontal margin',(x0,x1))
        assert 72<=y0<=y1<=HEIGHT-72,(PAGE,'vertical margin',(y0,y1))
    for i,a in enumerate(NODES):
        for b in NODES[i+1:]:
            overlap_x=min(a[2],b[2])-max(a[0],b[0])
            overlap_y=min(a[3],b[3])-max(a[1],b[1])
            assert overlap_x<=0 or overlap_y<=0,(PAGE,'overlap',a[4],b[4])
    BOUNDS.clear();NODES.clear();C.showPage()


page('User interface',[
    ('Start.','Create root = tk.Tk(), then TraverseApp(root); show_menu() displays the menu.'),
    ('User interface.','Run root.mainloop() before any case-selection or button callback.'),
    ('Select the traverse case to work on.','K opens a case; A, S, D, Z and C perform the selected action.'),
    ('Return / End.','M shows the menu. R resumes the event loop. Close window is the only path to End.'),
])
node(CENTER,724,'Start',w=76,h=24,kind='term')
node(CENTER,660,'Main window: switches between the menu screen and the solver screen.',
     'root = tk.Tk()\nTraverseApp(root) | show_menu()',w=276,h=80,kind='sub')
edge([(CENTER,712),(CENTER,700)])
node(CENTER,573,'User interface','root.mainloop()',w=265,h=48)
edge([(CENTER,620),(CENTER,597)])
node(CENTER,490,'MenuScreen / SolverScreen',w=170,h=66,kind='decision')
edge([(CENTER,549),(CENTER,523)])
connector(104,573,'R');edge([(114,573),(140,573),(140,535),(CENTER,535)])
edge([(CENTER-85,490),(83,490),(83,255)],arrow=False)
edge([(CENTER+85,490),(512,490),(512,255)],arrow=False)
for y,label,key in [(420,'Select the traverse case\nto work on','K'),(365,'Add Line','A'),(310,'Solve Omitted Measurements','S'),(255,'Remove Selected','D')]:
    connector(260,y,key);edge([(83,y),(250,y)])
    words=wrap(label,152,10)
    for i,line in enumerate(words):text(166.5,y+5+(len(words)-1-i)*12.5,line,10)
for y,label,key in [(420,'Return','M'),(365,'Reset','Z'),(310,'Clear All','C')]:
    connector(335,y,key);edge([(512,y),(345,y)],label,(430,y+8))
node(335,255,'End',w=65,h=24,kind='term')
edge([(512,255),(367.5,255)],'Close window',(440,267))
finish()

page('Add Line',[
    ('Add a traverse line.','Enter Line, Bearing and Length (m). Use Unknown for omitted values.'),
    ('Input fields.','all(texts) rejects empty fields: Please fill in all input fields.'),
    ('Build a Line from the entry boxes.','Line.from_text() and Bearing.parse() validate the entries; ValueError shows Invalid input.'),
    ('Add Line.','self.traverse.add(line) saves the line; clear the entry boxes and continue at V.'),
])
connector(215,720,'A')
node(215,650,'Add a traverse line (use Unknown for omitted values)',
     'name_entry | bearing_entry | length_entry',w=264,h=70,kind='io')
edge([(215,710),(215,685)])
node(215,550,'all input fields\nall(texts)',w=182,h=64,kind='decision');edge([(215,615),(215,582)])
node(430,550,'Please fill in all input fields.',w=170,h=56,kind='error')
edge([(306,550),(345,550)],'False',(325,565));connector(430,480,'R');edge([(430,522),(430,490)])
node(215,440,'Build a Line from the entry boxes.\nBuild a Bearing from user text.',
     'Line.from_text() | Bearing.parse()',w=264,h=84,kind='sub')
edge([(215,518),(215,482)],'True',(239,497))
node(435,365,'Invalid input','str(error)',w=160,h=66,kind='error')
edge([(347,440),(435,440),(435,398)],'ValueError',(458,420),color='#be123c')
connector(435,290,'R');edge([(435,332),(435,300)])
node(215,325,'Add Line','self.traverse.add(line)\nentry.delete(0, tk.END)',w=264,h=70)
edge([(215,398),(215,360)])
connector(215,255,'V');edge([(215,290),(215,265)])
finish()

page('MenuScreen / SolverScreen',[
    ('Select the traverse case to work on.','open_case(index) switches to SolverScreen, sets the case and calls reset().'),
    ('Return / Reset.','show_menu() returns to the menu. reset(): Empty the table and the entry boxes.'),
    ('Remove Selected.','With selected rows, remove them and refresh at V. Without selected rows, return at R.'),
    ('Clear All.','An empty table resets directly. Otherwise, confirm Clear all: True resets at Z; False returns at R.'),
])
for x,label in [(132,'K'),(300,'M'),(455,'Z')]:connector(x,718,label)
node(132,650,'Select the traverse case to work on','open_case(index)',w=116,h=86,kind='sub')
edge([(132,708),(132,693)]);connector(132,570,'Z');edge([(132,607),(132,580)])
node(300,650,'Start screen where the user picks which case to work on.','show_menu()',w=142,h=86,kind='sub')
edge([(300,708),(300,693)]);connector(300,570,'R');edge([(300,607),(300,580)])
node(455,650,'Empty the table and the entry boxes.','reset()',w=130,h=86,kind='sub')
edge([(455,708),(455,693)]);connector(455,570,'V');edge([(455,607),(455,580)])
connector(155,510,'D');node(155,440,'Remove Selected\nselected',w=145,h=70,kind='decision');edge([(155,500),(155,475)])
connector(285,440,'R');edge([(227.5,440),(275,440)],'False',(250,454))
node(155,342,'Removed selected line(s)','self.traverse.remove()',w=148,h=72,kind='sub')
edge([(155,405),(155,378)],'True',(179,393));connector(155,255,'V');edge([(155,306),(155,265)])
connector(410,510,'C');node(410,440,'self.traverse.lines',w=160,h=60,kind='decision');edge([(410,500),(410,470)])
connector(510,440,'Z');edge([(490,440),(500,440)],'False',(500,458))
node(410,335,'Clear all','messagebox.askyesno()',w=170,h=100,kind='decision')
edge([(410,410),(410,385)],'True',(436,396))
connector(285,335,'R');edge([(325,335),(295,335)],'False',(306,351))
connector(410,255,'Z');edge([(410,285),(410,265)],'True',(435,271))
finish()

page('Solve Omitted Measurements',[
    ('Fill in the omitted measurements in place.','Call self.traverse.solve(); SolverScreen.solve() catches ValueError through E.'),
    ('omitted.','No omitted measurements found - nothing to solve. Otherwise, continue with the known lines.'),
    ('closing.','Use line.components() for complete lines; closing = (-known_lat, -known_dep).'),
    ('len(omitted).','One omitted side follows L; two follow T. Any other count follows E. The menu case does not choose the solver.'),
])
connector(215,720,'S')
node(215,650,'Fill in the omitted measurements in place.','self.traverse.solve()',w=260,h=70,kind='sub')
edge([(215,710),(215,685)]);connector(460,650,'E');edge([(345,650),(450,650)],'ValueError',(397,665),color='#be123c')
node(215,553,'omitted\nmeasurements',w=180,h=64,kind='decision');edge([(215,615),(215,585)])
node(430,553,'No omitted measurements found - nothing to solve.','raise ValueError',w=170,h=80,kind='raise')
edge([(305,553),(345,553)],'False',(325,568));connector(430,480,'E');edge([(430,513),(430,490)])
node(215,439,'The omitted sides must add up to this vector for the traverse to close.',
     'closing = (-known_lat, -known_dep)',w=260,h=78)
edge([(215,521),(215,478)],'True',(239,497))
node(215,340,'omitted\nlen(omitted)',w=180,h=64,kind='decision');edge([(215,400),(215,372)])
connector(85,340,'L');edge([(125,340),(95,340)],'1',(109,354))
connector(410,340,'T');edge([(305,340),(400,340)],'2',(352,354))
connector(215,255,'E');edge([(215,308),(215,265)],'else',(239,282))
finish()

page('Omitted measurements',[
    ('Case I.','One side has neither bearing nor length: _solve_one_side(). Other one-side combinations raise ValueError.'),
    ('Case III.','Both bearings known, so solve two simultaneous equations: _solve_two_lengths().'),
    ('Case IV.','Both lengths known, so intersect two circles (two mirror solutions): _solve_two_bearings().'),
    ('Case II.','One side is missing its length, the other its bearing: _solve_length_and_bearing(). Unsupported kinds follow E.'),
])
connector(155,720,'L')
node(155,650,'Case I: one side has neither bearing nor length.','_solve_one_side()',w=160,h=92,kind='sub')
edge([(155,710),(155,696)]);connector(155,565,'P');edge([(155,604),(155,575)])
connector(425,720,'T');node(425,655,'bearing / length\nkinds',w=160,h=64,kind='decision');edge([(425,710),(425,687)])
node(155,455,'Case III: both bearings known, so solve two simultaneous equations.',
     '_solve_two_lengths()',w=160,h=100,kind='sub')
edge([(345,655),(295,655),(295,535),(155,535),(155,505)],'{"length"}',(265,672))
node(425,485,'Case IV: both lengths known, so intersect two circles (two mirror solutions).',
     '_solve_two_bearings()',w=176,h=112,kind='sub')
edge([(425,623),(425,541)],'{"bearing"}',(472,582))
connector(510,575,'E');edge([(505,655),(510,655),(510,585)],'else',(496,672))
node(155,285,'Case II: one side is missing its length, the other its bearing.',
     '_solve_length_and_bearing()',w=160,h=90,kind='sub')
edge([(385,639),(315,639),(315,360),(155,360),(155,330)],'{"length", "bearing"}',(250,589))
connector(155,375,'P');edge([(155,405),(155,385)])
connector(425,385,'P');edge([(425,429),(425,395)])
connector(285,285,'P');edge([(235,285),(275,285)])
finish()

page('Traverse Data & Solved Results',[
    ('options.','No valid solution - check the input data. Empty options raise ValueError and follow E.'),
    ('chosen.','Prefer one that doesn\'t cross itself. Start with options[0]; keep it when no is_simple(trial) option is found.'),
    ('Fill in the omitted measurements in place.','Save chosen lines in self.lines[k], then refresh at V.'),
    ('Traverse Data & Solved Results.','refresh() updates the table and Traverse Plot. Cannot solve shows str(error); R resumes the event loop.'),
])
connector(177,720,'P');node(177,657,'options',w=175,h=62,kind='decision');edge([(177,710),(177,688)])
connector(300,657,'E');edge([(264.5,657),(290,657)],'False',(280,674))
node(177,550,"Prefer one that doesn't cross itself.",'chosen = options[0]\nself.is_simple(trial)',w=195,h=100,kind='sub')
edge([(177,626),(177,600)],'True',(202,611))
node(177,427,'Fill in the omitted measurements in place.','self.lines[k] = line',w=195,h=70)
edge([(177,500),(177,462)]);connector(177,345,'V');edge([(177,392),(177,355)])
connector(430,720,'E');node(430,657,'Cannot solve','str(error)\nStatus: could not solve',w=170,h=82,kind='error')
edge([(430,710),(430,698)]);connector(430,570,'R');edge([(430,616),(430,580)])
connector(410,525,'V')
node(410,450,'Traverse Data & Solved Results','refresh() | table_values()',w=200,h=70,kind='io')
edge([(410,515),(410,485)])
node(410,340,'Traverse Plot','draw_plot() | vertices()\ndraw_edges(points)',w=200,h=80,kind='io')
edge([(410,415),(410,380)]);connector(410,255,'R');edge([(410,300),(410,265)])
finish()
C.save()
print(OUT / 'TraverseCraft_Flowchart.pdf')
