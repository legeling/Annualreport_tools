import tkinter as tk
from tkinter import filedialog, messagebox
import jieba
from collections import Counter
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class WordFrequencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("词频分析小工具")
        self.create_widgets()

    def create_widgets(self):
        # 文件路径选择
        tk.Label(self.root, text="选择文件路径").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = tk.Entry(self.root, width=50)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="浏览", command=self.select_path).grid(row=0, column=2, padx=10, pady=10)

        # 关键词输入
        tk.Label(self.root, text="输入需要分析的关键词").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.keyword_entry = tk.Entry(self.root, width=50)
        self.keyword_entry.grid(row=1, column=1, padx=10, pady=10)

        # 开始分析按钮
        tk.Button(self.root, text="开始分析", command=self.analyze).grid(row=2, column=1, padx=10, pady=10)

        # 结果显示区域
        self.result_text = tk.Text(self.root, width=60, height=15)
        self.result_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def select_path(self):
        path = filedialog.askopenfilename()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

    def analyze(self):
        file_path = self.path_entry.get()
        keyword = self.keyword_entry.get()

        if not file_path or not keyword:
            messagebox.showwarning("警告", "请填写完整信息")
            return

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 词频统计
        words = jieba.cut(content)
        word_count = Counter(words)

        # 显示词频结果
        self.result_text.delete(1.0, tk.END)
        for word, count in word_count.items():
            if keyword in word:
                self.result_text.insert(tk.END, f"{word}: {count}\n")

        # 生成词云
        self.generate_wordcloud(word_count)

    def generate_wordcloud(self, word_count):
        wc = WordCloud(font_path='simsun.ttf', background_color="white")
        wc.generate_from_frequencies(word_count)
        wc.to_file("wordcloud.png")

        # 显示词云图片
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = WordFrequencyApp(root)
    root.mainloop()
