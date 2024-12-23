import tkinter as tk
from client.gui import KnowgentGUI
from server.database.database import Database

def main():
    # 初始化数据库
    db = Database("MyRepository")
    db.initialize()

    # 初始化主窗口
    root = tk.Tk()
    root.title("Knowgent v0.4.2")
    root.geometry("1200x800")
    app = KnowgentGUI(root, db)
    root.mainloop()

if __name__ == "__main__":
    main() 
