from server.application.services.ollama_service import OllamaService as Ollama
from server.application.exceptions.ollama import OllamaError
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage, font as tkfont
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math
import threading

class llmagent:

    def __init__(self,root):
        self.Ollama = Ollama()
        self.botstate = False
        self.bots=['qwen2.5:0.5b', 'llama3.2:1b', 'nomic-embed-text', 'mxbai-embed-large', ]
        self.image_refs=[]
        self.image_path=None
        self.thumbnail_label=None
        self.style=ttk.Style()
        self.editor_content=None
        self.root=root

    def create_chat(self, frameroot):
        self.chat=ttk.Frame(frameroot, style="Custom.TFrame")
        # ================= 聊天显示区域（带滚动条） ================= #
        chat_frame = tk.Frame(self.chat, bg="white")
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        menu_title=tk.StringVar()
        menu_title.set("My model")

        def check_and_pull(bot):
            self.botstate=False
            self.send_button.config(state='disabled')
            try:
                self.botstate=self.Ollama.pull(bot)
            except OllamaError as e:
                messagebox.showinfo("Error", "Please open ollama before choosing a model.")
                menu_title.set("My model")
                return 
            if self.botstate:
                menu_title.set(bot)
                self.model_name = bot
                self.send_button.config(state='normal')
            else:
                menu_title.set(f"{bot}:unavailable")

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

        self.style.configure('TScrollbar',
                    background='#FFFFFF',
                    arrowcolor='#2C3E50',
                    bordercolor='#FFFFFF',
                    troughcolor='#FFFFFF',
                    relief=tk.FLAT,
                    width=12  # 设置滚动条宽度
                )
        
        
        # 配置滚动条贴图
        self.style.map('TScrollbar',
            background=[
                ('pressed', '#E0E0E0'),
                ('active', '#E0E0E0',),
                ('!active', "#FFFFFF")
            ],
            arrowcolor=[
                ('pressed', '#2C3E50'),
                ('active', '#2C3E50'),
                ('!active', '#2C3E50')
            ]
        )

        # 滚动条
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical",style='TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = ttk.Scrollbar(chat_frame, orient="horizontal", style='TScrollbar')
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)


        # Canvas实现滚动
        self.chat_canvas = tk.Canvas(chat_frame, bg="white",xscrollcommand=h_scrollbar.set, yscrollcommand=scrollbar.set, highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.chat_canvas.yview)
        h_scrollbar.config(command=self.chat_canvas.xview)
        


        def on_mouse_wheel(event):
        # 实现鼠标滚轮滚动效果
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            #print("wheeling")
        def on_shift_mouse_wheel(event):
        # 按住Shift时，鼠标滚轮进行水平滚动
            self.chat_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")        

        # 在Canvas上创建一个Frame来容纳消息内容
        self.chat_frame_inner = tk.Frame(self.chat_canvas, bg="white")
        self.window=self.chat_canvas.create_window((0, 0), window=self.chat_frame_inner, anchor="nw")        
    

        def on_frame_configure(event):
        # # 更新Canvas的滚动区域大小
            self.chat_canvas.config(scrollregion=self.chat_canvas.bbox("all"))
            
        self.chat_frame_inner.bind("<Configure>", on_frame_configure)
        
        def resize_message_canvas(event):
            canvas_width = max(self.chat_canvas.winfo_width(), self.chat_frame_inner.winfo_reqwidth())
            self.chat_canvas.itemconfig(self.window, width=canvas_width)
            pass

        self.chat_canvas.bind("<Configure>", resize_message_canvas)

        self.chat_frame_inner.bind("<Shift-MouseWheel>", on_shift_mouse_wheel)  # 按住Shift + 滚轮进行水平滚动
        self.chat_frame_inner.bind("<MouseWheel>", on_mouse_wheel)   # Windows

        # ================= 输入框区域 ================= #
        self.input_frame = tk.Frame(self.chat, bg="#DEDEDE", height=80, highlightbackground='white',highlightthickness=2)
        self.input_frame.pack(side=tk.BOTTOM, fill='both')


        # 使用grid布局管理输入框和按钮
        self.placeholder='Ask me anything'
        self.input_entry = tk.Text(self.input_frame, font=("等线", 12), relief="flat", bg="#DEDEDE",fg="#8F8F8F",wrap="word", height=5)
        self.input_entry.grid(row=1, column=0, padx=10, pady=10, columnspan=4,sticky="ew")
        def on_focus_in(event):
            if self.input_entry.get("1.0", "end-1c") == self.placeholder:
                self.input_entry.delete('1.0', tk.END)  # 清空输入框
                self.input_entry.config(fg="black")  # 设置输入文字颜色为黑色

        def on_focus_out(event):
            if not self.input_entry.get("1.0", "end-1c"):  # 输入框为空时显示提示文字
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
            
        def insert_newline(event=None):
            """在输入框中插入换行符"""
            self.input_entry.insert(tk.INSERT, "\n")
            return "break" 

        self.input_entry.bind("<Return>", on_enter_press)  
        self.input_entry.bind("<Shift-Return>", insert_newline)  

        send_icon = PhotoImage(file="./client/src/send.png")
        self.send_button = tk.Button(self.input_frame, image=send_icon, bg="#DEDEDE",command=self.send_message, relief='flat')
        self.send_button.grid(row=1, column=4, padx=10, pady=10, sticky="e")
        self.send_button.image = send_icon
        self.send_button.config(state='disabled')

        image_icon = PhotoImage(file="./client/src/clip.png")
        image_button = tk.Button(self.input_frame, image=image_icon, bg="#DEDEDE",command=self.upload_image, relief='flat')
        image_button.grid(row=2, column=0, padx=10, pady=10, sticky="ws")
        image_button.image = image_icon
        

        new_icon = PhotoImage(file="./client/src/add.png")
        new_button = tk.Button(self.input_frame, image=new_icon, bg="#DEDEDE",command=self.new_chat, relief='flat')
        new_button.grid(row=2, column=4, padx=10, pady=10, sticky="e")
        new_button.image = new_icon
        
        tag_icon = PhotoImage(file="./client/src/tag.png")
        self.tag_button = tk.Button(self.input_frame, image=tag_icon, bg="#DEDEDE", relief='flat')
        self.tag_button.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        self.tag_button.image = tag_icon

        outline_icon = PhotoImage(file="./client/src/stroke.png")
        self.outline_button = tk.Button(self.input_frame, image=outline_icon, bg="#DEDEDE", relief='flat')
        self.outline_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.outline_button.image = outline_icon

        self.input_frame.grid_columnconfigure(3, weight=1) 

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
    def add_message(self, sender, msg_text=None, image_path=None):
        """添加消息到聊天窗口"""
        if sender == "user":
            msg_color = "#DCF8C6"  # 浅绿色背景
            anchor = "e"  # 右对齐
        else:
            msg_color = "#E5E5E5"  # 浅灰色背景
            anchor = "w"  # 左对齐

        message_frame = tk.Frame(self.chat_frame_inner, bg="white")
        message_frame.pack(anchor=anchor, pady=5, padx=10)

        # 使用Canvas绘制圆角矩形
        message_canvas = tk.Canvas(message_frame, bg="white", highlightthickness=0)
        message_canvas.pack(padx=5)
        

        if image_path:
            image = Image.open(image_path)
            image.thumbnail((350, 350))  # 缩放到 150x150 像素以内
            photo = ImageTk.PhotoImage(image)
            self.image_refs.append(photo)
            text_id=message_canvas.create_image(10,10,anchor="nw", image=photo)
            
        else:
            #print(len(msg_text))
            message_widget = tk.Text(message_canvas, wrap=tk.WORD, height=1, bg=msg_color, fg="black", font=("等线", 12), bd=0)
            message_widget.insert(tk.END, msg_text)
            message_widget.config(state="disabled")  # 设置为只读
            message_widget.pack(anchor="nw", padx=10, pady=5, fill=tk.X)

            # 动态调整高度以适应内容
            # font = message_widget.cget("font")
            text_font = tkfont.Font(family="等线", size=12)
            text_width =text_font.measure(msg_text)//text_font.measure("a")
            max_chars = 400 // text_font.measure("A")  
            
            message_widget.config(width=min(text_width+2,max_chars))
            
            lines = ((text_width+2) // max_chars) + 1  # 超过最大宽度会换行
            text_lines = lines+msg_text.count("\n")+msg_text.count("\r") # 加上显式换行符的行数
            print(text_lines)
            print(msg_text.count("\n"))
            print(msg_text)
            
            message_widget.config(height=text_lines)
            
            message_widget.update_idletasks()              

            def on_wheel(event):
                if event.widget.master.master.master:
                    event.widget.master.master.master.event_generate("<MouseWheel>", delta=event.delta)

            
            def on_swheel(event):
                if event.widget.master.master.master:
                    event.widget.master.master.master.event_generate("<Shift-MouseWheel>", delta=event.delta)

            message_widget.bind("<MouseWheel>", on_wheel)  # 禁用鼠标滚轮
            message_widget.bind("<Shift-MouseWheel>",on_swheel)      # 禁用键盘向上滚动



            text_id=message_canvas.create_window(10, 10, anchor="nw", window=message_widget)
            
                #max_width = 400  # 最大气泡宽度
                #text_id = message_canvas.create_text(10, 10, anchor="nw", text=text, font=("等线", 12), fill="black", width=max_width)

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

        def copy_message():
            self.root.clipboard_clear()
            try:
                self.root.clipboard_append(msg_text)
            except tk.TclError:
                pass
        if not sender == "user":  
            copy_icon = PhotoImage(file="./client/src/copy.png")
            copy_button = tk.Button(message_frame, image=copy_icon, bg="white",command=copy_message, relief='flat')
            copy_button.image = copy_icon
            copy_button.pack(padx=5,anchor="nw")

        self.chat_canvas.yview_moveto(1.0)
        return message_frame

    # 发送消息的函数
    def send_message(self):
        if self.botstate:
            user_text = self.input_entry.get("1.0", "end-1c").strip()
            #print(len(user_text))
            if not self.image_path and not user_text:
                return
            if self.image_path:
                self.add_message("user",image_path=self.image_path)
                self.thumbnail_label.destroy()
                self.thumbnail_label = None
                self.cancel_button.destroy()
                self.cancel_button = None
            
            if user_text:
                self.input_entry.delete("1.0", tk.END)
                self.add_message("user", user_text)
            mesg=self.add_message("message","...")
            thread = threading.Thread(target=self.get_bot_reply, args=(user_text,mesg, True))
            thread.start()
            
            # 滚动到底部
            

    def get_bot_reply(self, user_text, mesg, if_include):
        reply = self.Ollama.chat(self.model_name, user_text, if_include, image_path=self.image_path)
        # 在主线程中更新 UI
        self.image_path = None
        mesg.destroy()
        self.add_message("bot", reply)
    
    def create_outline(self, editor_text):
        user_text = editor_text.strip()
        #print(user_text)
        if user_text and self.botstate:
            input = "Please generate an outline for the following note. Organize your reply in markdown grammar. Make sure the language of your response be the same as the following note.\n\n" + user_text
            mesg=self.add_message("message","Generating outline, please wait...")
            thread = threading.Thread(target=self.get_bot_reply, args=(input,mesg, False))
            thread.start()

    def create_tag(self, editor_text):
        user_text = editor_text.strip()
        if user_text and self.botstate:
            input = "Please generate 2 to 5 tags that can properly classify the following note into a specific field. Each tag, which is a short noun word or noun phrase without further explanation, should be put in a seperate line. Don't reply anything other than these tags. Don't reply in markdown format. Make sure the language of your response be the same as the following note. Don't add number before tags.\n\n" + user_text
            mesg=self.add_message("message","Generating tags, please wait...")
            thread = threading.Thread(target=self.get_bot_reply, args=(input,mesg, False))
            thread.start()

    def upload_image(self): 
        try:       
            init_dir = "MyNotebooks"
            file_path = filedialog.askopenfilename(
                initialdir=init_dir,
                title="Select an image",
                filetypes=[
                    ("img", ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"]),
                ]
            )
            if file_path:
                self.image_path = file_path
                image = Image.open(file_path)
                image.thumbnail((100, 100))  # 设置缩略图大小
                thumbnail = ImageTk.PhotoImage(image)

                if self.thumbnail_label:
                    self.thumbnail_label.destroy()

                self.thumbnail_label = tk.Label(self.input_frame, image=thumbnail)
                self.thumbnail_label.image = thumbnail  # 保持引用
                self.thumbnail_label.grid(row=0, column=0, padx=5, pady=5)

                cancel_icon = PhotoImage(file="./client/src/delete.png")
                self.cancel_button = tk.Button(
                    self.input_frame, 
                    text="Cancel", 
                    command=self.cancel_upload,
                    image=cancel_icon,
                    relief="flat",
                    bg="#DEDEDE"
                )
                self.cancel_button.grid(row=0, column=3, padx=5, pady=5)
                self.cancel_button.image=cancel_icon

        except Exception as e:
            print(f"Error: {e}")

    def cancel_upload(self):
        # 删除缩略图和取消按钮，清空图片路径
        self.thumbnail_label.destroy()
        self.thumbnail_label = None
        self.cancel_button.destroy()
        self.cancel_button = None
        self.image_path = None
        #print("Image upload canceled.")

    def new_chat(self):
        for widget in self.chat_frame_inner.winfo_children():
            widget.destroy()
        if self.input_entry.get("1.0", "end-1c") and not self.input_entry.get("1.0", "end-1c") == self.placeholder:
            self.input_entry.delete('1.0',tk.END)
        
        self.Ollama.clear_chat_history()
        if self.image_path:
            self.image_path = None
            self.cancel_upload()
        
