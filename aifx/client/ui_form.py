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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QTableView, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(1626, 1547)
        Widget.setWindowOpacity(1.000000000000000)
        Widget.setAutoFillBackground(True)
        self.layoutWidget = QWidget(Widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 1591, 1471))
        self.vl_top = QVBoxLayout(self.layoutWidget)
        self.vl_top.setObjectName(u"vl_top")
        self.vl_top.setContentsMargins(0, 0, 0, 0)
        self.hl_title = QHBoxLayout()
        self.hl_title.setObjectName(u"hl_title")
        self.lbl_aifx = QLabel(self.layoutWidget)
        self.lbl_aifx.setObjectName(u"lbl_aifx")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_aifx.sizePolicy().hasHeightForWidth())
        self.lbl_aifx.setSizePolicy(sizePolicy)
        self.lbl_aifx.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.hl_title.addWidget(self.lbl_aifx)

        self.hs_title = QSpacerItem(40, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.hl_title.addItem(self.hs_title)

        self.lbl_version = QLabel(self.layoutWidget)
        self.lbl_version.setObjectName(u"lbl_version")
        sizePolicy.setHeightForWidth(self.lbl_version.sizePolicy().hasHeightForWidth())
        self.lbl_version.setSizePolicy(sizePolicy)
        self.lbl_version.setMouseTracking(True)
        self.lbl_version.setTextFormat(Qt.AutoText)
        self.lbl_version.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.hl_title.addWidget(self.lbl_version)


        self.vl_top.addLayout(self.hl_title)

        self.vl_plot = QVBoxLayout()
        self.vl_plot.setObjectName(u"vl_plot")
        self.lbl_current_pair = QLabel(self.layoutWidget)
        self.lbl_current_pair.setObjectName(u"lbl_current_pair")
        font = QFont()
        font.setPointSize(16)
        self.lbl_current_pair.setFont(font)
        self.lbl_current_pair.setAlignment(Qt.AlignCenter)

        self.vl_plot.addWidget(self.lbl_current_pair)

        self.tbl_recent_candles = QTableView(self.layoutWidget)
        self.tbl_recent_candles.setObjectName(u"tbl_recent_candles")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tbl_recent_candles.sizePolicy().hasHeightForWidth())
        self.tbl_recent_candles.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setFamilies([u"DejaVu Sans Mono"])
        self.tbl_recent_candles.setFont(font1)
        self.tbl_recent_candles.setAlternatingRowColors(True)

        self.vl_plot.addWidget(self.tbl_recent_candles)

        self.wgt_plot = QWidget(self.layoutWidget)
        self.wgt_plot.setObjectName(u"wgt_plot")

        self.vl_plot.addWidget(self.wgt_plot)

        self.vl_plot.setStretch(2, 1)

        self.vl_top.addLayout(self.vl_plot)

        self.hl_instrument = QHBoxLayout()
        self.hl_instrument.setObjectName(u"hl_instrument")
        self.lbl_instrument = QLabel(self.layoutWidget)
        self.lbl_instrument.setObjectName(u"lbl_instrument")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lbl_instrument.sizePolicy().hasHeightForWidth())
        self.lbl_instrument.setSizePolicy(sizePolicy2)

        self.hl_instrument.addWidget(self.lbl_instrument)

        self.cb_instrument = QComboBox(self.layoutWidget)
        self.cb_instrument.setObjectName(u"cb_instrument")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.cb_instrument.sizePolicy().hasHeightForWidth())
        self.cb_instrument.setSizePolicy(sizePolicy3)
        self.cb_instrument.setMinimumSize(QSize(350, 0))

        self.hl_instrument.addWidget(self.cb_instrument)

        self.btn_load = QPushButton(self.layoutWidget)
        self.btn_load.setObjectName(u"btn_load")

        self.hl_instrument.addWidget(self.btn_load)

        self.hs_instrument = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.hl_instrument.addItem(self.hs_instrument)

        self.hl_instrument.setStretch(3, 1)

        self.vl_top.addLayout(self.hl_instrument)

        self.hl_upstream = QHBoxLayout()
        self.hl_upstream.setObjectName(u"hl_upstream")
        self.vl_upstream = QVBoxLayout()
        self.vl_upstream.setObjectName(u"vl_upstream")
        self.lbl_broker = QLabel(self.layoutWidget)
        self.lbl_broker.setObjectName(u"lbl_broker")
        self.lbl_broker.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.vl_upstream.addWidget(self.lbl_broker)

        self.lbl_oanda = QLabel(self.layoutWidget)
        self.lbl_oanda.setObjectName(u"lbl_oanda")
        self.lbl_oanda.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.vl_upstream.addWidget(self.lbl_oanda)


        self.hl_upstream.addLayout(self.vl_upstream)

        self.vl_upstream_status = QVBoxLayout()
        self.vl_upstream_status.setObjectName(u"vl_upstream_status")
        self.lbl_broker_status = QLabel(self.layoutWidget)
        self.lbl_broker_status.setObjectName(u"lbl_broker_status")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lbl_broker_status.sizePolicy().hasHeightForWidth())
        self.lbl_broker_status.setSizePolicy(sizePolicy4)
        font2 = QFont()
        font2.setFamilies([u"DejaVu Sans Mono"])
        font2.setPointSize(16)
        self.lbl_broker_status.setFont(font2)
        self.lbl_broker_status.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.vl_upstream_status.addWidget(self.lbl_broker_status)

        self.lbl_oanda_status = QLabel(self.layoutWidget)
        self.lbl_oanda_status.setObjectName(u"lbl_oanda_status")
        self.lbl_oanda_status.setFont(font2)
        self.lbl_oanda_status.setAlignment(Qt.AlignBottom|Qt.AlignRight|Qt.AlignTrailing)

        self.vl_upstream_status.addWidget(self.lbl_oanda_status)


        self.hl_upstream.addLayout(self.vl_upstream_status)

        self.vl_upstream_spacer = QVBoxLayout()
        self.vl_upstream_spacer.setObjectName(u"vl_upstream_spacer")
        self.hs_broker = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.vl_upstream_spacer.addItem(self.hs_broker)

        self.hs_oanda = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.vl_upstream_spacer.addItem(self.hs_oanda)


        self.hl_upstream.addLayout(self.vl_upstream_spacer)

        self.hl_upstream.setStretch(2, 1)

        self.vl_top.addLayout(self.hl_upstream)

        self.hl_exit = QHBoxLayout()
        self.hl_exit.setObjectName(u"hl_exit")
        self.hs_exit = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_exit.addItem(self.hs_exit)

        self.btn_exit = QPushButton(self.layoutWidget)
        self.btn_exit.setObjectName(u"btn_exit")
        sizePolicy.setHeightForWidth(self.btn_exit.sizePolicy().hasHeightForWidth())
        self.btn_exit.setSizePolicy(sizePolicy)

        self.hl_exit.addWidget(self.btn_exit)


        self.vl_top.addLayout(self.hl_exit)

        self.vl_top.setStretch(1, 1)

        self.retranslateUi(Widget)

        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.lbl_aifx.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-size:24pt; font-weight:700; color:#669f1e;\">AI FX</span></p></body></html>", None))
        self.lbl_version.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700; color:#669f1e;\">&lt;version&gt;</span></p></body></html>", None))
        self.lbl_current_pair.setText(QCoreApplication.translate("Widget", u"N/A", None))
        self.lbl_instrument.setText(QCoreApplication.translate("Widget", u"Instrument:", None))
        self.btn_load.setText(QCoreApplication.translate("Widget", u"Load", None))
        self.lbl_broker.setText(QCoreApplication.translate("Widget", u"Broker:", None))
        self.lbl_oanda.setText(QCoreApplication.translate("Widget", u"OANDA:", None))
        self.lbl_broker_status.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.lbl_oanda_status.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.btn_exit.setText(QCoreApplication.translate("Widget", u"Exit", None))
    # retranslateUi

