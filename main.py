import tkinter as tk
from frontend.gui import KnowgentGUI

def main():
    root = tk.Tk()
    root.title("Knowgent v0.2.2")
    root.geometry("1200x800")
    app = KnowgentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 