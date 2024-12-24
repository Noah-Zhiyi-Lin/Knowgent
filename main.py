import tkinter as tk
from client.gui import KnowgentGUI
from server.database.database import Database

def main():
    base_path = "./MyRepository"
    # 读取配置文件
    try:
        with open("config.txt", "r") as config_file:
            for line in config_file:
                if line.startswith("base_path"):
                    base_path = line.split("=")[1].strip()  # 获取bath_path的值
                    break  # 找到后退出循环
    except FileNotFoundError:
        pass
    # 初始化数据库
    db = Database(base_path)
    db.initialize()

    # 初始化主窗口
    root = tk.Tk()
    root.title("Knowgent v0.4.2")
    root.geometry("1200x720")
    app = KnowgentGUI(root, db,base_path)
    root.mainloop()

if __name__ == "__main__":
    main() 
