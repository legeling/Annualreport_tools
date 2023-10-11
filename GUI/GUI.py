#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Annualreport_tools 
@File    ：GUI.py
@IDE     ：PyCharm 
@Author  ：lingxiaotian
@Date    ：2023/10/11 13:31 
'''
import first
import second
import third
import sys
from PyQt5.QtWidgets import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题
        self.setWindowTitle("年报爬虫小工具 - by:凌小添")
        # 设置窗口尺寸
        self.setGeometry(800, 800, 1000, 800)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)



        # 创建输入框
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("请输入")

        # 创建输出框
        self.output_box = QTextEdit(self)
        self.output_box.setPlaceholderText("Output will be displayed here")

        # 创建提示框
        self.label = QLabel("Select an option:", self)

        # 创建单选框
        self.radio_button1 = QRadioButton("Option 1", self)
        self.radio_button2 = QRadioButton("Option 2", self)

        # 创建按钮
        self.button = QPushButton("Submit", self)
        self.button.clicked.connect(self.process_input)

        # 设置布局
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.button)

        options_layout = QVBoxLayout()
        options_layout.addWidget(self.label)
        options_layout.addWidget(self.radio_button1)
        options_layout.addWidget(self.radio_button2)

        main_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.output_box)
        main_layout.addLayout(options_layout)

        self.central_widget.setLayout(main_layout)

    def showDialog(self):
        # 创建一个信息对话框
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("这是一个信息对话框")
        msg.setWindowTitle("信息")
        msg.setStandardButtons(QMessageBox.Ok)

        # 显示对话框
        msg.exec_()

    def process_input(self):
        user_input = self.input_box.text()
        if self.radio_button1.isChecked():
            result = f"Option 1 selected. You entered: {user_input}"
        elif self.radio_button2.isChecked():
            result = f"Option 2 selected. You entered: {user_input}"
        else:
            result = f"No option selected. You entered: {user_input}"

        self.output_box.setPlainText(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())