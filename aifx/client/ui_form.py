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
        Widget.resize(1452, 737)
        Widget.setWindowOpacity(1.000000000000000)
        Widget.setAutoFillBackground(True)
        self.layoutWidget = QWidget(Widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 16, 1421, 661))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
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

        self.hl_title.setStretch(1, 1)

        self.verticalLayout.addLayout(self.hl_title)

        self.vl_current_pair = QVBoxLayout()
        self.vl_current_pair.setObjectName(u"vl_current_pair")
        self.lbl_current_pair = QLabel(self.layoutWidget)
        self.lbl_current_pair.setObjectName(u"lbl_current_pair")
        font = QFont()
        font.setPointSize(16)
        self.lbl_current_pair.setFont(font)
        self.lbl_current_pair.setAlignment(Qt.AlignCenter)

        self.vl_current_pair.addWidget(self.lbl_current_pair)

        self.wgt_plot = QWidget(self.layoutWidget)
        self.wgt_plot.setObjectName(u"wgt_plot")

        self.vl_current_pair.addWidget(self.wgt_plot)

        self.vl_current_pair.setStretch(1, 1)

        self.verticalLayout.addLayout(self.vl_current_pair)

        self.hl_recent_candles = QHBoxLayout()
        self.hl_recent_candles.setObjectName(u"hl_recent_candles")
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

        self.hl_recent_candles.addWidget(self.tbl_recent_candles)


        self.verticalLayout.addLayout(self.hl_recent_candles)

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

        self.hs_instrument = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.hl_instrument.addItem(self.hs_instrument)

        self.btn_load = QPushButton(self.layoutWidget)
        self.btn_load.setObjectName(u"btn_load")

        self.hl_instrument.addWidget(self.btn_load)

        self.hl_instrument.setStretch(2, 1)

        self.verticalLayout.addLayout(self.hl_instrument)

        self.hl_footer = QHBoxLayout()
        self.hl_footer.setObjectName(u"hl_footer")
        self.lbl_connection = QLabel(self.layoutWidget)
        self.lbl_connection.setObjectName(u"lbl_connection")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lbl_connection.sizePolicy().hasHeightForWidth())
        self.lbl_connection.setSizePolicy(sizePolicy4)

        self.hl_footer.addWidget(self.lbl_connection)

        self.hs_footer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hl_footer.addItem(self.hs_footer)

        self.btn_exit = QPushButton(self.layoutWidget)
        self.btn_exit.setObjectName(u"btn_exit")
        sizePolicy.setHeightForWidth(self.btn_exit.sizePolicy().hasHeightForWidth())
        self.btn_exit.setSizePolicy(sizePolicy)

        self.hl_footer.addWidget(self.btn_exit)

        self.hl_footer.setStretch(1, 1)

        self.verticalLayout.addLayout(self.hl_footer)


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
        self.lbl_connection.setText(QCoreApplication.translate("Widget", u"<html><head/><body><p><span style=\" font-weight:700; color:#ff7800;\">Uninitialized</span></p></body></html>", None))
        self.btn_exit.setText(QCoreApplication.translate("Widget", u"Exit", None))
    # retranslateUi

