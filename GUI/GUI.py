import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("简单GUI示例")
        self.setGeometry(100, 100, 400, 200)

        # 添加标签
        self.label = QLabel("Hello, GUI!", self)

        # 添加按钮
        self.button = QPushButton("点击我", self)
        self.button.clicked.connect(self.on_button_click)

        # 设置布局
        self.setup_layout()

    def setup_layout(self):
        # 使用垂直布局
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # 设置窗口主布局
        self.setLayout(layout)

    def on_button_click(self):
        self.label.setText("你点击了按钮！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleGUI()
    window.show()
    sys.exit(app.exec_())
