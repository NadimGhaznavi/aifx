# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(800, 600)
        self.widget = QWidget(Widget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 10, 781, 581))
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lbl_aifx = QLabel(self.widget)
        self.lbl_aifx.setObjectName(u"lbl_aifx")
        self.lbl_aifx.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.horizontalLayout_2.addWidget(self.lbl_aifx)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.lbl_version = QLabel(self.widget)
        self.lbl_version.setObjectName(u"lbl_version")
        self.lbl_version.setTextFormat(Qt.AutoText)
        self.lbl_version.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.horizontalLayout_2.addWidget(self.lbl_version)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 223, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lbl_instrument = QLabel(self.widget)
        self.lbl_instrument.setObjectName(u"lbl_instrument")

        self.horizontalLayout.addWidget(self.lbl_instrument)

        self.cb_instrument = QComboBox(self.widget)
        self.cb_instrument.setObjectName(u"cb_instrument")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cb_instrument.sizePolicy().hasHeightForWidth())
        self.cb_instrument.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.cb_instrument)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 223, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lbl_connection = QLabel(self.widget)
        self.lbl_connection.setObjectName(u"lbl_connection")

        self.horizontalLayout_3.addWidget(self.lbl_connection)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.btn_exit = QPushButton(self.widget)
        self.btn_exit.setObjectName(u"btn_exit")

        self.horizontalLayout_3.addWidget(self.btn_exit)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.lbl_aifx.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-size:24pt; font-weight:700; color:#669f1e;\">AI FX</span></p></body></html>", None))
        self.lbl_version.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700; color:#669f1e;\">&lt;version&gt;</span></p></body></html>", None))
        self.lbl_instrument.setText(QCoreApplication.translate("Widget", u"Instrument:", None))
        self.lbl_connection.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.btn_exit.setText(QCoreApplication.translate("Widget", u"Exit", None))
    # retranslateUi

