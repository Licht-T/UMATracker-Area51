#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsObject

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtCore import Qt
import copy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor

class ResizableGraphicsObject(QGraphicsObject):

    def __init__(self, parent=None):
        super(ResizableGraphicsObject, self).__init__(parent)
        self.setZValue(1000)

        self.mouseIsPressed = None

        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)

        self._buttonList = {}
        self.setFocus(Qt.ActiveWindowFocusReason)

        self.color = QColor(128, 128, 255, 128)

        self.initialized = False

    def setColor(self, color):
        self.color = QColor(color)
        self.color.setAlpha(32)

    def setPoints(self, points):
        self.points = points
        rect = QRectF(QPointF(*points[0]), QPointF(*points[1]))
        self.setRect(rect)

    def setRect(self, rect):
        self._rect = rect
        self._boundingRect = rect

    def prepareGeometryChange(self):
        top = self._rect.topLeft()
        bottom = self._rect.bottomRight()
        super(ResizableGraphicsObject, self).prepareGeometryChange()

    def hoverMoveEvent(self, event):
        hoverMovePos = event.scenePos()
        mouseHoverArea = None
        for item in self._buttonList:
            if self._buttonList[item].contains(hoverMovePos):
                mouseHoverArea = item
                break
        if mouseHoverArea:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            return
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(ResizableGraphicsObject, self).hoverMoveEvent(event)

    def hoverEnterEvent(self, event):
        self.setCursor(QtCore.Qt.SizeAllCursor)
        super(ResizableGraphicsObject, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)
        super(ResizableGraphicsObject, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.mouseIsPressed = True
        self.mousePressPos = event.scenePos()
        self.rectPress = copy.deepcopy(self._rect)
        self.mousePressArea = None
        for item in self._buttonList:
            if self._buttonList[item].contains(self.mousePressPos):
                self.mousePressArea = item
                break
        super(ResizableGraphicsObject, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouseIsPressed = False
        self.updateResizeHandles()
        super(ResizableGraphicsObject, self).mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        self.draw(painter, option, widget, self._rect)
        for item in self._buttonList:
            painter.drawRect(self._buttonList[item])

        if not self.initialized:
            self.updateResizeHandles()
            self.initialized = True

    def draw(self, painter, option, widget, rect):
        return

    def boundingRect(self):
        return self._boundingRect

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def mouseMoveEvent(self, event):
        mouseMovePos = event.scenePos()
        if self.mouseIsPressed:
            if self.mousePressArea == 'topRect':
                self._rect.setTop(
                        self.rectPress.y() - (self.mousePressPos.y() - mouseMovePos.y())
                        )
            elif self.mousePressArea == 'bottomRect':
                self._rect.setBottom(
                        self.rectPress.bottom() - (self.mousePressPos.y() - mouseMovePos.y())
                        )
            elif self.mousePressArea == 'leftRect':
                self._rect.setLeft(
                        self.rectPress.left() - (self.mousePressPos.x() - mouseMovePos.x())
                        )
            elif self.mousePressArea == 'rightRect':
                self._rect.setRight(
                        self.rectPress.right() - (self.mousePressPos.x() - mouseMovePos.x())
                        )
            elif self.mousePressArea == 'topleftRect':
                self._rect.setTopLeft(
                        self.rectPress.topLeft() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'toprightRect':
                self._rect.setTopRight(
                        self.rectPress.topRight() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'bottomleftRect':
                self._rect.setBottomLeft(
                        self.rectPress.bottomLeft() - (self.mousePressPos - mouseMovePos)
                        )
            elif self.mousePressArea == 'bottomrightRect':
                self._rect.setBottomRight(
                        self.rectPress.bottomRight() - (self.mousePressPos - mouseMovePos)
                        )
            else:
                self._rect.moveCenter(
                        self.rectPress.center() - (self.mousePressPos - mouseMovePos)
                        )
        self.updateResizeHandles()

    def updateResizeHandles(self):
        self.prepareGeometryChange()
        self.resizeHandleSize = 4.0
        self._rect = self._rect.normalized()

        # FIXME:結構アドホック，複数のビューでシーンを表示してるときには問題が出る．
        views = self.scene().views()
        self.offset = self.resizeHandleSize * (views[0].mapToScene(1, 0).x() - views[0].mapToScene(0, 1).x())

        adjusted_rect = self._rect.adjusted(
                -self.offset*2,
                -self.offset*2,
                self.offset*2,
                self.offset*2
            )

        self._boundingRect.setRect(adjusted_rect.x(), adjusted_rect.y(), adjusted_rect.width(), adjusted_rect.height())
        self._buttonList["topRect"] = QRectF(
                self._rect.center().x(),
                self._boundingRect.topLeft().y()+self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["bottomRect"] = QRectF(
                self._rect.center().x(),
                self._rect.bottom()-self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["leftRect"] = QRectF(
                self._rect.x()-self.offset,
                self._rect.center().y()-self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["rightRect"] = QRectF(
                self._rect.right()-self.offset,
                self._rect.center().y()-self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["topleftRect"] = QRectF(
                self._boundingRect.topLeft().x()+self.offset,
                self._boundingRect.topLeft().y()+self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["toprightRect"] = QRectF(
                self._boundingRect.topRight().x()-3*self.offset,
                self._boundingRect.topRight().y()+self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["bottomleftRect"] = QRectF(
                self._boundingRect.bottomLeft().x()+self.offset,
                self._boundingRect.bottomLeft().y()-3*self.offset,
                2*self.offset,
                2*self.offset
            )
        self._buttonList["bottomrightRect"] = QRectF(
                self._boundingRect.bottomRight().x()-self.offset*3,
                self._boundingRect.bottomRight().y()-self.offset*3,
                2*self.offset,
                2*self.offset
            )


def main():
    pass

if __name__ == "__main__":
    main()
