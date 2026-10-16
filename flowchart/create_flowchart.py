"""Generate the color-coded program flowchart. Requires reportlab."""
from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 900, 1200
INK = '#203249'
PALETTE = {
    'term': ('#dcfce7', '#15803d'),
    'process': ('#dbeafe', '#2563eb'),
    'sub': ('#ede9fe', '#7c3aed'),
    'decision': ('#fef3c7', '#b77908'),
    'io': ('#ccfbf1', '#0f766e'),
    'error': ('#ffe4e6', '#be123c'),
    'connector': ('#ffffff', '#64748b'),
}
C = canvas.Canvas(str(OUT / 'TraverseCraft_Flowchart.pdf'), pagesize=(WIDTH, HEIGHT))
C.setTitle('Program flowchart')
NODE_BOUNDS = []


def wrapped(value, width, font, size):
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
    return result


def lines(x, y, value, size=13, font='Helvetica', color=INK):
    C.setFillColor(HexColor(color))
    C.setFont(font, size)
    for k, line in enumerate(value):
        C.drawCentredString(x, y - k * size * 1.27, line)


def node(x, y, label, ref='', w=300, h=68, kind='process', size=13):
    fill, stroke = PALETTE[kind]
    C.setFillColor(HexColor(fill))
    C.setStrokeColor(HexColor(stroke))
    C.setLineWidth(1.25)
    if kind == 'connector':
        C.circle(x, y, 18, stroke=1, fill=1)
        lines(x, y - 4.5, [label], 13, 'Helvetica-Bold')
        return
    if kind == 'term':
        C.roundRect(x-w/2, y-h/2, w, h, h/2, stroke=1, fill=1)
    elif kind == 'decision':
        p = C.beginPath()
        for i, (px, py) in enumerate([(x,y+h/2), (x+w/2,y), (x,y-h/2), (x-w/2,y)]):
            (p.moveTo if i == 0 else p.lineTo)(px,py)
        p.close()
        C.drawPath(p, stroke=1, fill=1)
    elif kind in ('io', 'error'):
        p = C.beginPath()
        pts = [(x-w/2+12,y+h/2),(x+w/2,y+h/2),(x+w/2-12,y-h/2),(x-w/2,y-h/2)]
        for i,(px,py) in enumerate(pts):
            (p.moveTo if i == 0 else p.lineTo)(px,py)
        p.close()
        C.drawPath(p,stroke=1,fill=1)
    else:
        C.roundRect(x-w/2,y-h/2,w,h,5,stroke=1,fill=1)
        if kind == 'sub':
            for offset in (-w/2+7,w/2-7):
                C.line(x+offset,y-h/2+5,x+offset,y+h/2-5)
    inner_width = w * .65 if kind == 'decision' else w-36
    main = wrapped(label, inner_width, 'Helvetica', size)
    refs = wrapped(ref, w-28, 'Helvetica', 10.5) if ref else []
    total = len(main)*size*1.27 + (len(refs)*13.3+7 if refs else 0)
    assert total <= h-8, (label,total,h)
    assert all(stringWidth(t,'Helvetica',size) <= inner_width for t in main), label
    start = y + total/2 - size
    lines(x,start,main,size)
    if refs:
        lines(x,start-len(main)*size*1.27-7,refs,10.5,color=stroke)
    NODE_BOUNDS.append((x-w/2,y-h/2,x+w/2,y+h/2))


def edge(points, label='', at=None, color=INK, arrow=True):
    C.setStrokeColor(HexColor(color))
    C.setFillColor(HexColor(color))
    C.setLineWidth(1.15)
    path=C.beginPath(); path.moveTo(*points[0])
    for p in points[1:]: path.lineTo(*p)
    C.drawPath(path)
    if arrow:
        a,b=points[-2:]
        angle=math.atan2(b[1]-a[1],b[0]-a[0])
        p=C.beginPath();p.moveTo(*b)
        for offset in (-.45,.45):p.lineTo(b[0]-7*math.cos(angle+offset),b[1]-7*math.sin(angle+offset))
        p.close();C.drawPath(p,stroke=0,fill=1)
    if label:
        x,y=at
        lines(x,y,[label],10.5,color=color)


def connector(x,y,label):node(x,y,label,kind='connector')


def page(title):
    C.setFillColor(HexColor(INK));C.setFont('Helvetica-Bold',22)
    C.drawString(45,1150,title)
    C.setStrokeColor(HexColor('#d6dee8'));C.line(45,1126,855,1126)


def finish():
    for x0,y0,x1,y1 in NODE_BOUNDS:
        assert 24 <= x0 < x1 <= WIDTH-24 and 35 <= y0 < y1 <= 1105
    NODE_BOUNDS.clear()
    C.showPage()


# Main window and callback dispatch. Lettered connectors replace long return lines.
page('1  User interface')
node(450,1070,'Start',w=120,h=40,kind='term')
node(450,970,'Main window: switches between the menu screen and the solver screen.',
     'root = tk.Tk()  |  TraverseApp(root)',w=440,h=100,kind='sub')
edge([(450,1050),(450,1020)])
node(450,845,'Select the traverse case to work on','show_menu()  |  open_case(index)  |  reset()',w=440,h=86,kind='io')
edge([(450,920),(450,888)])
connector(160,845,'M');edge([(178,845),(230,845)])
node(450,710,'User interface','root.mainloop()',w=300,h=100,kind='decision')
edge([(450,802),(450,760)])
connector(160,780,'R');edge([(178,780),(220,780),(220,710),(300,710)])
edge([(300,710),(55,710),(55,295)],arrow=False)
edge([(600,710),(845,710),(845,295)],arrow=False)
for x,y,label,key in [(250,565,'Add Line','A'),(250,430,'Solve Omitted Measurements','S'),(250,295,'Remove Selected','D'),(650,565,'Reset','Z'),(650,430,'Clear All','C'),(650,295,'Return','M')]:
    node(x,y,label,w=260,h=62,kind='io')
    if x==250:
        edge([(55,y),(120,y)]);edge([(380,y),(392,y)]);connector(410,y,key)
    else:
        edge([(845,y),(780,y)]);edge([(520,y),(508,y)]);connector(490,y,key)
node(450,105,'End',w=120,h=40,kind='term')
edge([(450,660),(450,125)],'return',(483,175))
finish()

# Add Line and the shared display refresh reached by successful changes.
page('2  Add Line')
connector(280,1070,'A')
node(280,975,'Add a traverse line (use Unknown for omitted values)',
     'Line (e.g. BC)  |  Bearing (e.g. N 48°50\'10\'\' E)  |  Length (m)',w=440,h=88,kind='io')
edge([(280,1052),(280,1019)])
node(280,850,'all(texts)',w=250,h=80,kind='decision');edge([(280,931),(280,890)])
node(690,850,'Please fill in all input fields.',w=300,h=68,kind='error')
edge([(405,850),(540,850)],'False',(466,867));connector(690,770,'R');edge([(690,816),(690,788)])
node(280,715,'Build a Line from the entry boxes.\nBuild a Bearing from user text.',
     'Line.from_text(*texts)  |  Bearing.parse(bearing_text)',w=440,h=100,kind='sub')
edge([(280,810),(280,765)],'True',(305,785))
node(690,635,'Invalid input','str(error)',w=290,h=74,kind='error')
edge([(500,715),(690,715),(690,672)],'ValueError',(601,732),color='#be123c')
connector(690,550,'R');edge([(690,598),(690,568)])
node(280,555,'Add Line','self.traverse.add(line)\nself.solved = set()  |  entry.delete(0, tk.END)',w=440,h=90)
edge([(280,665),(280,600)])
connector(280,440,'V');edge([(280,510),(280,458)])
node(450,315,'Traverse Data & Solved Results','refresh()  |  line.table_values()',w=440,h=80,kind='io')
edge([(280,422),(280,385),(450,385),(450,355)])
node(450,190,'Traverse Plot','draw_plot()  |  self.traverse.vertices()  |  self.draw_edges(points)',w=510,h=80,kind='io')
edge([(450,275),(450,230)])
connector(450,85,'R');edge([(450,150),(450,103)])
finish()

# The data determines the solver; the menu selection is not solver validation.
page('3  Solve Omitted Measurements')
connector(330,1070,'S')
node(330,990,'Fill in the omitted measurements in place.','self.traverse.solve()',w=420,h=82,kind='sub')
edge([(330,1052),(330,1031)])
connector(730,990,'E');edge([(540,990),(712,990)],'ValueError',(625,1008),color='#be123c')
node(330,885,'omitted',w=230,h=70,kind='decision');edge([(330,949),(330,920)])
node(690,885,'No omitted measurements found - nothing to solve.',w=300,h=80,kind='error')
edge([(445,885),(540,885)],'False',(490,902));connector(690,810,'E');edge([(690,845),(690,828)])
node(330,775,'The omitted sides must add up to this vector for the traverse to close.',
     'line.components()  |  closing = (-known_lat, -known_dep)',w=430,h=90,kind='process')
edge([(330,850),(330,820)],'True',(355,832))
node(330,670,'omitted','len(omitted)',w=250,h=80,kind='decision');edge([(330,730),(330,710)])
node(175,555,'Case I: one side has neither bearing nor length.',
     '_solve_one_side(omitted[0], closing)',w=290,h=100,kind='sub')
edge([(205,670),(175,670),(175,605)],'1',(185,688))
node(580,555,'kinds','_solve_two_sides(omitted, closing)',w=370,h=100,kind='decision')
edge([(455,670),(580,670),(580,605)],'2',(520,688))
connector(805,670,'E');edge([(580,670),(787,670)],'else',(728,688))
node(190,405,'Case III: both bearings known, so solve two simultaneous equations.',
     '_solve_two_lengths(i, j, closing)',w=310,h=100,kind='sub')
node(580,405,'Case IV: both lengths known, so intersect two circles (two mirror solutions).',
     '_solve_two_bearings(i, j, closing)',w=330,h=100,kind='sub')
edge([(395,555),(365,555),(365,478),(190,478),(190,455)],'{"length"}',(269,494))
edge([(580,505),(580,455)],'{"bearing"}',(631,479))
node(580,265,'Case II: one side is missing its length, the other its bearing.',
     '_solve_length_and_bearing(i, j, closing)',w=360,h=94,kind='sub')
edge([(765,555),(795,555),(795,265),(760,265)],'{"length", "bearing"}',(777,575))
connector(840,490,'E');edge([(795,555),(840,555),(840,508)],'else',(840,571))
# All successful solver candidates meet at P; solver failures meet at E.
connector(90,300,'P');edge([(175,505),(175,485),(25,485),(25,300),(72,300)])
connector(190,300,'P');edge([(190,355),(190,318)])
# Matching P connectors continue with candidate selection on page 4.
connector(385,405,'P');edge([(415,405),(403,405)])
connector(580,175,'P');edge([(580,218),(580,193)])
finish()

page('4  Results and table actions')
connector(210,1070,'P')
node(210,965,"Prefer one that doesn't cross itself.",
     'chosen = options[0]  |  self.is_simple(trial)\nself.lines[k] = line',w=350,h=110,kind='sub')
edge([(210,1052),(210,1020)])
connector(210,835,'V');edge([(210,910),(210,853)])
connector(655,1070,'E')
node(655,965,'Cannot solve','str(error)\nStatus: could not solve',w=350,h=110,kind='error')
edge([(655,1052),(655,1020)])
connector(655,835,'R');edge([(655,910),(655,853)])
# Remove, Reset, Clear All are independent event callbacks.
connector(170,690,'D');connector(450,690,'Z');connector(730,690,'C')
node(170,590,'selected',w=200,h=80,kind='decision');edge([(170,672),(170,630)])
connector(300,590,'R');edge([(270,590),(282,590)],'False',(293,613))
node(170,450,'Removed selected line(s)','self.traverse.remove(selected)',w=250,h=88,kind='sub')
edge([(170,550),(170,494)],'True',(195,520));connector(170,350,'V');edge([(170,406),(170,368)])
node(450,590,'Empty the table and the entry boxes.','reset()',w=245,h=110,kind='sub');edge([(450,672),(450,645)])
connector(450,450,'V');edge([(450,535),(450,468)])
node(730,590,'self.traverse.lines',w=240,h=80,kind='decision');edge([(730,672),(730,630)])
connector(730,485,'Z');edge([(730,550),(730,503)],'False',(756,525))
node(730,350,'Remove every line\nfrom the table?','messagebox.askyesno()',w=270,h=140,kind='decision')
edge([(850,590),(870,590),(870,440),(730,440),(730,420)],'True',(847,461))
connector(730,225,'Z');edge([(730,280),(730,243)],'True',(755,267))
connector(520,350,'R');edge([(595,350),(538,350)],'False',(565,368))
finish()
C.save()
print(OUT / 'TraverseCraft_Flowchart.pdf')
