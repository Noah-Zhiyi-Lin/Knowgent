import tkinter as tk

class MenuBuilder:
    def __init__(self, gui):
        self.gui = gui
        self.root = gui.root
        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.gui.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.gui.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.gui.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Create New File", command=self.gui.create_new_file, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Select Directory", command=self.gui.select_directory, accelerator="Ctrl+D")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # 编辑菜单
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.gui.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.gui.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.gui.paste_text, accelerator="Ctrl+V")
        edit_menu.add_command(label="Select All", command=self.gui.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find", command=self.gui.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.gui.replace_text, accelerator="Ctrl+R")

        # 添加预览菜单
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Preview Markdown", command=self.gui.update_preview, accelerator="Ctrl+P")
        menu_bar.add_cascade(label="View", menu=view_menu)

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menu_bar)

        # 绑定快捷键
        self.bind_shortcuts()

    def bind_shortcuts(self):
        self.root.bind('<Control-o>', lambda event: self.gui.open_file())
        self.root.bind('<Control-s>', lambda event: self.gui.save_file())
        self.root.bind('<Control-Shift-S>', lambda event: self.gui.save_file_as())
        self.root.bind('<Control-n>', lambda event: self.gui.create_new_file())
        self.root.bind('<Control-d>', lambda event: self.gui.select_directory())
        self.root.bind('<Control-q>', lambda event: self.root.quit())
        self.root.bind('<Control-x>', lambda event: self.gui.cut_text())
        self.root.bind('<Control-c>', lambda event: self.gui.copy_text())
        self.root.bind('<Control-v>', lambda event: self.gui.paste_text())
        self.root.bind('<Control-a>', lambda event: self.gui.select_all())
        self.root.bind('<Control-f>', lambda event: self.gui.find_text())
        self.root.bind('<Control-r>', lambda event: self.gui.replace_text())
        self.root.bind('<Control-p>', lambda event: self.gui.update_preview()) 