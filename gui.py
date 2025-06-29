import tkinter as tk
from tkinter import font

class GUI:
    bg_color = "#f0f4f8"
    label_color = "#1f2937"
    button_color = "#6B9BDB"
    button_label_color = "#ffffff"

    entry_width = 30
    combo_width = 27
    textbox_width = 22

    def __init__(self, root):
        self.root = root
        self.header1_font = font.Font(self.root, family="Courier New", size=14, weight="bold")
        self.header2_font = font.Font(self.root, family="Courier New", size=11)
        self.text_font = font.Font(self.root, family="Courier New", size=10)
        self.button_font = font.Font(self.root, family="Courier New", size=10, weight="bold")