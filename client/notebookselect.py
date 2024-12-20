import tkinter as tk
from tkinter import ttk, messagebox

class NotebookSelectionDialog:
    def __init__(self, parent, notebook_service):
        self.notebook_service = notebook_service
        self.selected_notebook = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Notebook")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # 创建一个Frame来包含Treeview和滚动条
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建Treeview
        self.notebook_tree = ttk.Treeview(container, columns=(0,), show="headings")  # 使用整数索引 0
        self.notebook_tree.heading(0, text="Notebook Name")  # 使用整数索引 0
        self.notebook_tree.column(0, width=350, anchor="w")  # 使用整数索引 0
        self.notebook_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 将Treeview放在左侧

        # 添加滚动条
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.notebook_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # 将滚动条放在右侧
        self.notebook_tree.configure(yscrollcommand=scrollbar.set)

        # 加载笔记本列表
        self.load_notebooks()

        # 创建确认和取消按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)  # 将按钮框架放在底部

        # 使用 grid 布局均匀分布按钮
        confirm_button = ttk.Button(button_frame, text="Confirm", command=self.confirm_selection)
        confirm_button.grid(row=0, column=0, padx=5, pady=5)  # 确认按钮放在第一列

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_button.grid(row=0, column=1, padx=5, pady=5)  # 取消按钮放在第二列

        # 设置列权重，使按钮均匀分布
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)


    def load_notebooks(self):
        """加载所有笔记本到Treeview中"""
        try:
            notebooks = self.notebook_service.get_all_notebooks()
            if not notebooks:
                messagebox.showinfo("No Notebooks", "No notebooks available. Please create a notebook first.")
                self.dialog.destroy()
                return

            # 清空Treeview
            self.notebook_tree.delete(*self.notebook_tree.get_children())

            # 插入笔记本数据
            for notebook in notebooks:
                self.notebook_tree.insert("", "end", values=(notebook['notebook_name'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notebooks: {str(e)}")
            self.dialog.destroy()

    def confirm_selection(self):
        """确认选择并返回选中的笔记本名称"""
        selected_item = self.notebook_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a notebook.")
            return

        self.selected_notebook = self.notebook_tree.item(selected_item, "values")[0]
        self.dialog.destroy()

    def get_selected_notebook(self):
        """等待用户选择并返回选中的笔记本名称"""
        self.dialog.wait_window()
        return self.selected_notebook

    def select_notebook(parent, notebook_service):
        """弹出笔记本选择对话框，返回用户选择的笔记本名称"""
        dialog = NotebookSelectionDialog(parent, notebook_service)
        return dialog.get_selected_notebook()