from reportlab . graphics . shapes import Drawing
from reportlab . graphics . charts . lineplots import LinePlot
from reportlab . lib . pagesizes import A4
from reportlab . lib import colors
from reportlab . platypus import SimpleDocTemplate
from reportlab . lib . styles import getSampleStyleSheet
styles = getSampleStyleSheet ()
doc = SimpleDocTemplate ("graph.pdf", pagesize =A4 )
elements = []
drawing = Drawing ( 400 , 200 )
linePlotData = [(( 0.2 , 0.5 ) , ( 0.5 , 0.7 ) ,
                ( 1.2 , 0.9 ) , ( 1.8 , 1.1 ) ,
                ( 2.1 , 1.4 ) , ( 2.7 , 3.5 ) )]
lp = LinePlot ()
lp . x = 50
lp . y = 50
lp . height = 125
lp . width = 300
lp . data = linePlotData
lp . joinedLines = 1
lp . strokeColor = colors . black
lp . xValueAxis . valueMin = 0
lp . xValueAxis . valueMax = 5
lp . yValueAxis . valueMin = 0
lp . yValueAxis . valueMax = 5
lp . xValueAxis . valueSteps = [0 ,1 ,2 ,3 ,4 , 5]
lp . yValueAxis . valueSteps = [0 ,1 ,2 ,3 ,4 , 5]
drawing.add( lp )
elements.append ( drawing )
doc.build ( elements )


