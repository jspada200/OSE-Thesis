"""Script just to test stuff in QT outside main app."""
#!/usr/bin/env python

import math
from PyQt4 import QtCore, QtGui


class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        super(Node, self).__init__()

        self.graph = graphWidget
        self.edgeList = []

        self.nodeWidth = 400
        self.nodeMinHeight = 400

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setCacheMode(QtGui.QGraphicsItem.DeviceCoordinateCache)
        self.setZValue(1)
    
    def boundingRect(self):
        adjust = 1000.0
        return QtCore.QRectF(-self.nodeWidth,
                             -self.nodeMinHeight,
                             self.nodeWidth,
                             self.nodeMinHeight )
 
    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)
        # painter.drawEllipse(-7, -7, 20, 20)
        rectangle = QtCore.QRectF(-self.nodeWidth,
                                  -self.nodeMinHeight,
                                  self.nodeWidth,
                                  self.nodeMinHeight)
        painter.drawRoundedRect(rectangle, 3.0, 3.0)


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            self.graph.itemMoved()

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super(Node, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super(Node, self).mouseReleaseEvent(event)


class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        super(GraphWidget, self).__init__()

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        node1 = Node(self)
        scene.addItem(node1)

        node1.setPos(-50, -50)

        self.scale(0.8, 0.8)
        self.setMinimumSize(2500, 2500)
        self.setWindowTitle("Elastic Nodes")
    
    def drawBackground(self, painter, rect):
        # Shadow.
        sceneRect = self.sceneRect()
        rightShadow = QtCore.QRectF(sceneRect.right(), sceneRect.top() + 5, 5,
                sceneRect.height())
        bottomShadow = QtCore.QRectF(sceneRect.left() + 5, sceneRect.bottom(),
                sceneRect.width(), 5)
        if rightShadow.intersects(rect) or rightShadow.contains(rect):
          painter.fillRect(rightShadow, QtCore.Qt.darkGray)
        if bottomShadow.intersects(rect) or bottomShadow.contains(rect):
          painter.fillRect(bottomShadow, QtCore.Qt.darkGray)

        # Fill.
        gradient = QtGui.QLinearGradient(sceneRect.topLeft(),
                sceneRect.bottomRight())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(1, QtCore.Qt.lightGray)
        painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(gradient))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(sceneRect)

        # Text.
        textRect = QtCore.QRectF(sceneRect.left() + 4, sceneRect.top() + 4,
                sceneRect.width() - 4, sceneRect.height() - 4)
        message = "Click and drag the nodes around, and zoom with the " \
                "mouse wheel or the '+' and '-' keys"

        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.lightGray)
        painter.drawText(textRect.translated(2, 2), message)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(textRect, message)


    # -------------- Zooming --------------------------------
    def wheelEvent(self, event):
        self.translate(0, 25)
        # self.scaleView(math.pow(2.0, -event.delta() / 240.0), event)

    def scaleView(self, scaleFactor, event):

        # Save the scene pos
        oldPos = self.mapToScene(event.pos())
        self.scale(scaleFactor, scaleFactor)
        
        # Get the new position
        newPos = self.mapToScene(event.pos())
        center = QtCore.QPointF(750.0, 750.0)
        # Move scene to old position
        delta = center - oldPos
        print "OldPos:", oldPos

        print "center:", center

        print "delta:", delta

        
class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
        
    def initUI(self):               
        
        self.statusBar().showMessage('Ready')
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Statusbar')    
        gv = GraphWidget()

        self.setCentralWidget(gv)
        self.show()
        self.setGeometry(300, 300, 350, 250)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    widget = Example()
    widget.show()

    sys.exit(app.exec_())