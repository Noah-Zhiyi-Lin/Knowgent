from server.application.services.ollama_service import OllamaService as Ollama
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
import threading

class llmagent:

    def __init__(self):
        self.Ollama = Ollama()
        self.botstate = False
        self.bots=['qwen2.5:0.5b', 'llama3.2:1b', 'nomic-embed-text', 'mxbai-embed-large', ]
        self.hint_label=None
    def create_chat(self,root):
        self.chat=ttk.Frame(root, style="Custom.TFrame")
        # ================= 聊天显示区域（带滚动条） ================= #
        chat_frame = tk.Frame(self.chat, bg="white")
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        menu_title=tk.StringVar()
        menu_title.set("My model")

        def check_and_pull(bot):
            self.botstate=False
            self.send_button.config(state='disabled')
            self.botstate=self.Ollama.pull(bot)
            if self.botstate:
                menu_title.set(bot)
                self.model_name = bot
                self.send_button.config(state='normal')
            else:
                menu_title.set(f"{bot}:unavailable")
                self.send_button.config(state='disabled')

        # 添加 OptionMenu 下拉菜单
        def on_person_selected(bot):
            menu_title.set("pulling model...")
            thread = threading.Thread(target=check_and_pull, args=(bot,))
            thread.start()
            

        dropdown_button = tk.Menubutton(chat_frame, textvariable=menu_title, justify='left', font=("Arial", 12), bg="#DEDEDE", fg="black", relief="flat")
        dropdown_button.pack(side=tk.TOP, fill=tk.BOTH, pady=10, padx=10)
        dropdown_menu = tk.Menu(dropdown_button, tearoff=0, font=("Arial", 14))

        
        # 动态生成菜单项，设置与窗口等宽
        for bot in self.bots:
            dropdown_menu.add_command(label=bot, font=("Arial", 14), command=lambda p=bot: on_person_selected(p))

        # 将菜单关联到 Menubutton
        dropdown_button.config(menu=dropdown_menu)
        # 滚动条
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = ttk.Scrollbar(chat_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        # Canvas实现滚动
        self.chat_canvas = tk.Canvas(chat_frame, bg="white",xscrollcommand=h_scrollbar.set, yscrollcommand=scrollbar.set, highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_canvas.yview)
        
        def on_mouse_wheel(event):
        # 实现鼠标滚轮滚动效果
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def on_shift_mouse_wheel(event):
        # 按住Shift时，鼠标滚轮进行水平滚动
            self.chat_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        self.chat_canvas.bind_all("<Shift-MouseWheel>", on_shift_mouse_wheel)  # 按住Shift + 滚轮进行水平滚动
        self.chat_canvas.bind_all("<MouseWheel>", on_mouse_wheel)   # Windows
        

        # 在Canvas上创建一个Frame来容纳消息内容
        self.chat_frame_inner = tk.Frame(self.chat_canvas, bg="white")
        chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame_inner, anchor="nw")

        def on_frame_configure(event):
        # 更新Canvas的滚动区域大小
            self.chat_canvas.config(scrollregion=self.chat_canvas.bbox("all"))
            self.chat_canvas.itemconfig(chat_window, width=event.width)
        
        self.chat_frame_inner.bind("<Configure>", on_frame_configure)

        # 更新Canvas大小
        def update_scroll_region(event):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

        self.chat_frame_inner.bind("<Configure>", update_scroll_region)
        
        # ================= 输入框区域 ================= #
        self.input_frame = tk.Frame(self.chat, bg="#DEDEDE", height=80, highlightbackground='white',highlightthickness=2)
        self.input_frame.pack(side=tk.BOTTOM, fill='both')


        # 使用grid布局管理输入框和按钮
        self.placeholder='Ask me anything'
        self.input_entry = tk.Entry(self.input_frame, font=("等线", 12), relief="flat", bg="#DEDEDE",fg="#8F8F8F")
        self.input_entry.grid(row=0, column=0, padx=10, pady=10, columnspan=3,sticky="ew")
        def on_focus_in(event):
            if self.input_entry.get() == self.placeholder:
                self.input_entry.delete('0', tk.END)  # 清空输入框
                self.input_entry.config(fg="black")  # 设置输入文字颜色为黑色

        def on_focus_out(event):
            if not self.input_entry.get():  # 输入框为空时显示提示文字
                self.input_entry.insert(tk.END, self.placeholder)
                self.input_entry.config(fg="#8F8F8F")  # 设置提示文字颜色为灰色

        # 绑定事件
        self.input_entry.bind("<FocusIn>", on_focus_in)
        self.input_entry.bind("<FocusOut>", on_focus_out)
        
        self.input_entry.insert(tk.END, self.placeholder)  # 初始显示提示文字
        def on_enter_press(event):
            if self.botstate:
                self.send_message()
                return "break"  # 阻止默认的换行行为

        self.input_entry.bind("<Return>", on_enter_press)  

        send_icon = PhotoImage(file="./client/src/send.png")
        self.send_button = tk.Button(self.input_frame, image=send_icon, bg="#DEDEDE",command=self.send_message, relief='flat')
        self.send_button.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        self.send_button.image = send_icon
        self.send_button.config(state='disabled')

        image_icon = PhotoImage(file="./client/src/clip.png")
        image_button = tk.Button(self.input_frame, image=image_icon, bg="#DEDEDE",command=self.upload_image, relief='flat')
        image_button.grid(row=1, column=0, padx=10, pady=10, sticky="ws")
        image_button.image = image_icon
        self.image_path=None

        new_icon = PhotoImage(file="./client/src/add.png")
        new_button = tk.Button(self.input_frame, image=new_icon, bg="#DEDEDE",command=self.new_chat, relief='flat')
        new_button.grid(row=1, column=3, padx=10, pady=10, sticky="e")
        new_button.image = new_icon
        

        self.input_frame.grid_columnconfigure(2, weight=1) 

        return self.chat

    # 绘制圆角矩形的函数
    @staticmethod
    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs):
        """绘制圆角矩形"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius,
            x2, y2, x2 - radius, y2,
            x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    # 添加消息的函数
    def add_message(self, sender, text):
        """添加消息到聊天窗口"""
        if sender == "user":
            msg_color = "#DCF8C6"  # 浅绿色背景
            anchor = "e"  # 右对齐
        else:
            msg_color = "#E5E5E5"  # 浅灰色背景
            anchor = "w"  # 左对齐

        # 消息容器
        message_frame = tk.Frame(self.chat_frame_inner, bg="white")
        message_frame.pack(anchor=anchor, pady=5, padx=10)

        # 使用Canvas绘制圆角矩形
        message_canvas = tk.Canvas(message_frame, bg="white", highlightthickness=0)
        message_canvas.pack()

        max_width = 400  # 最大气泡宽度
        text_id = message_canvas.create_text(10, 10, anchor="nw", text=text, font=("等线", 12), fill="black", width=max_width)

        # 动态计算文本宽高
        bbox = message_canvas.bbox(text_id)
        text_width = bbox[2] - bbox[0] + 20  # 气泡宽度加内边距
        text_height = bbox[3] - bbox[1] + 20  # 气泡高度加内边距

        # 绘制圆角矩形背景
        rect_id=self.create_rounded_rectangle(message_canvas, 5, 5, text_width, text_height, radius=10, fill=msg_color, outline=msg_color)

        # 重新调整文本的位置，使其居中于圆角矩形内
        message_canvas.coords(text_id, 15, 15)

        message_canvas.tag_raise(text_id, rect_id)

        # 调整Canvas的大小
        message_canvas.config(width=text_width + 10, height=text_height + 10)

        return message_frame

    # 发送消息的函数
    def send_message(self):
        if self.botstate:
            user_text = self.input_entry.get().strip()
            if user_text:
                print("send")
                self.input_entry.delete("0", tk.END)
                self.add_message("user", user_text)
                mesg=self.add_message("message","...")
                thread = threading.Thread(target=self.get_bot_reply, args=(user_text,mesg))
                thread.start()
                self.image_path = None
            # 滚动到底部
            self.chat_canvas.yview_moveto(1.0)
            if self.hint_label:
                self.hint_label.destroy()

    def get_bot_reply(self, user_text,mesg):
        reply = self.Ollama.chat(self.model_name, user_text, include_history=True, image_path=self.image_path)
        # 在主线程中更新 UI
        mesg.destroy()
        self.add_message("bot", reply)

    def upload_image(self): 
        try:       
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("img", ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"]),
                ]
            )
            self.image_path = file_path
            # 添加欢迎文字标签
            self.hint_label = tk.Label(self.input_frame, text="Image uploaded successfully", font=("Arial", 12), fg="#8F8F8F", bg="#DEDEDE")
            self.hint_label.grid(row=1, column=1, padx=0, pady=10, sticky="w") 
            
             # 放在底部，调整上下间距
        except Exception as e:
            print(f"Error: {e}")

    def new_chat(self):
        for widget in self.chat_frame_inner.winfo_children():
            widget.destroy()
        if self.input_entry.get() and not self.input_entry.get() == self.placeholder:
            self.input_entry.delete('0',tk.END)
        self.image_path = None
        self.Ollama.clear_chat_history()
        if self.hint_label:
            self.hint_label.destroy()
        

