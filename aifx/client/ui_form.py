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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1125, 1487)
        Widget.setWindowOpacity(1.000000000000000)
        Widget.setAutoFillBackground(True)
        self.verticalLayout = QVBoxLayout(Widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.vl_instrument = QVBoxLayout()
        self.vl_instrument.setObjectName(u"vl_instrument")
        self.lbl_current_pair = QLabel(Widget)
        self.lbl_current_pair.setObjectName(u"lbl_current_pair")
        font = QFont()
        font.setPointSize(22)
        self.lbl_current_pair.setFont(font)
        self.lbl_current_pair.setAlignment(Qt.AlignCenter)

        self.vl_instrument.addWidget(self.lbl_current_pair)

        self.tbl_recent_candles = QTableView(Widget)
        self.tbl_recent_candles.setObjectName(u"tbl_recent_candles")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl_recent_candles.sizePolicy().hasHeightForWidth())
        self.tbl_recent_candles.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamilies([u"DejaVu Sans Mono"])
        self.tbl_recent_candles.setFont(font1)
        self.tbl_recent_candles.setAlternatingRowColors(True)

        self.vl_instrument.addWidget(self.tbl_recent_candles)

        self.wgt_plot = QWidget(Widget)
        self.wgt_plot.setObjectName(u"wgt_plot")

        self.vl_instrument.addWidget(self.wgt_plot)

        self.vl_instrument.setStretch(2, 1)

        self.verticalLayout.addLayout(self.vl_instrument)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.hs_instrument = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.hs_instrument, 0, 3, 1, 1)

        self.lbl_oanda_status = QLabel(Widget)
        self.lbl_oanda_status.setObjectName(u"lbl_oanda_status")
        font2 = QFont()
        font2.setFamilies([u"DejaVu Sans Mono"])
        font2.setPointSize(16)
        self.lbl_oanda_status.setFont(font2)
        self.lbl_oanda_status.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.gridLayout.addWidget(self.lbl_oanda_status, 1, 5, 1, 1)

        self.btn_load = QPushButton(Widget)
        self.btn_load.setObjectName(u"btn_load")

        self.gridLayout.addWidget(self.btn_load, 0, 2, 1, 1)

        self.cb_instrument = QComboBox(Widget)
        self.cb_instrument.setObjectName(u"cb_instrument")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_instrument.sizePolicy().hasHeightForWidth())
        self.cb_instrument.setSizePolicy(sizePolicy1)
        self.cb_instrument.setMinimumSize(QSize(350, 0))

        self.gridLayout.addWidget(self.cb_instrument, 0, 1, 1, 1)

        self.lbl_broker = QLabel(Widget)
        self.lbl_broker.setObjectName(u"lbl_broker")
        self.lbl_broker.setFont(font2)
        self.lbl_broker.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout.addWidget(self.lbl_broker, 0, 4, 1, 1)

        self.lbl_oanda = QLabel(Widget)
        self.lbl_oanda.setObjectName(u"lbl_oanda")
        self.lbl_oanda.setFont(font2)
        self.lbl_oanda.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout.addWidget(self.lbl_oanda, 1, 4, 1, 1)

        self.lbl_instrument = QLabel(Widget)
        self.lbl_instrument.setObjectName(u"lbl_instrument")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lbl_instrument.sizePolicy().hasHeightForWidth())
        self.lbl_instrument.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.lbl_instrument, 0, 0, 1, 1)

        self.lbl_broker_status = QLabel(Widget)
        self.lbl_broker_status.setObjectName(u"lbl_broker_status")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lbl_broker_status.sizePolicy().hasHeightForWidth())
        self.lbl_broker_status.setSizePolicy(sizePolicy3)
        self.lbl_broker_status.setFont(font2)
        self.lbl_broker_status.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.gridLayout.addWidget(self.lbl_broker_status, 0, 5, 1, 1)

        self.btn_exit = QPushButton(Widget)
        self.btn_exit.setObjectName(u"btn_exit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_exit.sizePolicy().hasHeightForWidth())
        self.btn_exit.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.btn_exit, 1, 0, 1, 1)

        self.gridLayout.setColumnStretch(3, 1)

        self.verticalLayout.addLayout(self.gridLayout)


        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.lbl_current_pair.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-size:22pt; color:#00aa00;\">Currency Pair</span></p></body></html>", None))
        self.lbl_oanda_status.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.btn_load.setText(QCoreApplication.translate("Widget", u"Load", None))
        self.lbl_broker.setText(QCoreApplication.translate("Widget", u"Broker", None))
        self.lbl_oanda.setText(QCoreApplication.translate("Widget", u"Oanda", None))
        self.lbl_instrument.setText(QCoreApplication.translate("Widget", u"Instrument:", None))
        self.lbl_broker_status.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.btn_exit.setText(QCoreApplication.translate("Widget", u"Exit", None))
    # retranslateUi

