import tkinter as tk
from tkinter import ttk, font, messagebox, IntVar
import os
import webbrowser
import time
import subprocess
import ctypes
import sys
import re

class SoVitsSVCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("So-Vits-SVC GUI Helper")

        #告诉操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        #获取屏幕的缩放因子
        ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
        #设置程序缩放
        root.tk.call('tk', 'scaling', ScaleFactor/75)
        # 设置窗口保持置顶
        root.attributes('-topmost', True)
        root.update()

        # 将窗口居中
        root.update_idletasks()
        width = 650
        height = 500
        x = (root.winfo_screenwidth() - width) // 2
        y = (root.winfo_screenheight() - height) // 2
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 请定义您的主文件夹路径
        self.main_folder = r'D:\So-Vits-SVC'

        # 获取Windows用户名
        self.username = os.environ.get('USERNAME')

        # 设置字体
        self.custom_font = font.Font(family="微软雅黑", size=12)
        self.style = ttk.Style()
        self.style.configure('.', font=self.custom_font)  # 设置全局字体

        # 创建容器框架
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True)

        # 在容器中居中放置内容
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(1, weight=1)


        self.label = ttk.Label(container, text=f"欢迎您，{self.username}")
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.use_tensorboard_var = IntVar()
        self.use_tensorboard_checkbox = ttk.Checkbutton(container, text="使用TensorBoard(仅主模型)", variable=self.use_tensorboard_var)
        self.use_tensorboard_checkbox.grid(row=1, column=0, columnspan=2, pady=5)
        self.create_button(container, "主模型训练", self.start_main_model_training, row=2, column=0)
        self.create_button(container, "扩散模型训练", self.start_diffusion_model_training, row=2, column=1)
        self.create_button(container, "启动WebUI", self.start_web_ui, row=3, column=0)
        self.create_button(container, "打开输入文件夹", self.open_input_folder, row=3, column=1)
        self.create_button(container, "打开输出文件夹", self.open_output_folder, row=4, column=0)
        self.create_button(container, "关于", self.show_about, row=4, column=1)
        # 添加Label显示最新模型信息
        self.latest_model_label = ttk.Label(container, text=f"最新主模型: {self.get_latest_model_filename()}")
        self.latest_model_label.grid(row=5, column=0, columnspan=2, pady=5)
        # 添加Label显示最新扩散模型信息
        self.latest_diffusion_model_label = ttk.Label(container, text=f"最新扩散模型: {self.get_latest_diffusion_model_filename()}")
        self.latest_diffusion_model_label.grid(row=6, column=0, columnspan=2, pady=5)
        # 添加Label显示说话人信息
        self.speakers_label = ttk.Label(container, text=f"可用说话人: {', '.join(self.get_speaker_names())}")
        self.speakers_label.grid(row=7, column=0, columnspan=2, pady=5)
        # 调用update_models方法，以1分钟为间隔更新模型信息
        self.root.after(60000, self.update_models)



        # 将回车键与确认按钮绑定
        self.root.bind('<Return>', lambda event=None: self.confirm())
    def update_models(self):
        # 更新最新模型信息
        latest_model_info = f"最新主模型: {self.get_latest_model_filename()}"
        self.latest_model_label.config(text=latest_model_info)

        # 更新最新扩散模型信息
        latest_diffusion_model_info = f"最新扩散模型: {self.get_latest_diffusion_model_filename()}"
        self.latest_diffusion_model_label.config(text=latest_diffusion_model_info)

        # 更新说话人信息
        speakers_info = f"可用说话人: {', '.join(self.get_speaker_names())}"
        self.speakers_label.config(text=speakers_info)

        # 调用update_models方法，以1分钟为间隔更新模型信息
        self.root.after(60000, self.update_models)

    def get_latest_model_filename(self):
        logs_path = os.path.join(self.main_folder, 'logs', '44k')
        logs_path = logs_path.replace(" ", "")
        print(logs_path)
        if os.path.exists(logs_path):
            files = [f for f in os.listdir(logs_path) if f.startswith('G') and f.endswith('.pth')]
            if files:
                latest_model = max(files, key=lambda x: os.path.getctime(os.path.join(logs_path, x)))
                return latest_model
        return "无可用模型文件"
    def get_latest_diffusion_model_filename(self):
        diffusion_logs_path = os.path.join(self.main_folder, 'logs', '44k', 'diffusion')
        diffusion_logs_path = diffusion_logs_path.replace(" ", "")
        print(diffusion_logs_path)
        if os.path.exists(diffusion_logs_path):
            files = [f for f in os.listdir(diffusion_logs_path) if f.startswith('model') and f.endswith('.pt')]
            if files:
                latest_diffusion_model = max(files, key=lambda x: os.path.getctime(os.path.join(diffusion_logs_path, x)))
                return latest_diffusion_model
        return "无可用模型文件"
    def get_speaker_names(self):
        dataset_raw_path = os.path.join(self.main_folder, 'dataset_raw')
        if os.path.exists(dataset_raw_path):
            speakers = [d for d in os.listdir(dataset_raw_path) if os.path.isdir(os.path.join(dataset_raw_path, d))]
            return speakers
        return ["无可用说话人"]
    def create_button(self, container, text, command, row, column):
        style = ttk.Style()
        style.configure("TButton", padding=5, width=15, anchor="center", font=("微软雅黑", 12))  # 设置字体

        ttk.Button(container, text=text, command=command, style="TButton").grid(row=row, column=column, pady=5)

    def start_main_model_training(self):
        use_tensorboard = self.use_tensorboard_var.get()
        if use_tensorboard:
            messagebox.showinfo("提示", f"开始主模型训练，使用TensorBoard选项：是")
            main_bat_path = os.path.abspath(os.path.join(self.main_folder))
            main_bat_file_path = os.path.abspath(os.path.join(self.main_folder, "[Tool]StartTrainMainModel.bat"))
            tensorboard_file_path = os.path.abspath(os.path.join(self.main_folder, "[Tool]TensorBoard.bat"))
            main_bat_file_path = main_bat_file_path.replace(" ", "")
            tensorboard_file_path = tensorboard_file_path.replace(" ", "")
            command_Main = f'start cmd /c "cd /d {main_bat_path} && "{main_bat_file_path}"'
            command_Tensorboard = f'start cmd /c "cd /d {main_bat_path} && "{tensorboard_file_path}"'
            os.system(command_Tensorboard)
            os.system(command_Main)
            os.system("taskmgr")
            time.sleep(5)
            webbrowser.open('http://localhost:6006')
        else:
            messagebox.showinfo("提示", f"开始主模型训练，使用TensorBoard选项：否")
            main_bat_path = os.path.abspath(os.path.join(self.main_folder))
            main_bat_file_path = os.path.abspath(os.path.join(self.main_folder, "[Tool]StartTrainMainModel.bat"))
            main_bat_file_path = main_bat_file_path.replace(" ", "")
            command = f'start cmd /c "cd /d {main_bat_path} && "{main_bat_file_path}"'
            os.system(command)

    
    def start_diffusion_model_training(self):
        diffusion_bat_path = os.path.abspath(os.path.join(self.main_folder))
        diffusion_bat_file_path = os.path.abspath(os.path.join(self.main_folder, "[Tool]StartTrainDiffusionModel.bat"))
        diffusion_bat_file_path = diffusion_bat_file_path.replace(" ", "")
        command = f'start cmd /c "cd /d {diffusion_bat_path} && "{diffusion_bat_file_path}"'
        os.system(command)

    def start_web_ui(self):
        webui_bat_path = os.path.abspath(os.path.join(self.main_folder))
        webui_bat_file_path = os.path.abspath(os.path.join(self.main_folder, "[Tool]StartWebUI.bat"))
        webui_bat_file_path = webui_bat_file_path.replace(" ", "")
        command = f'start cmd /c "cd /d {webui_bat_path} && "{webui_bat_file_path}"'
        os.system(command)

    def open_input_folder(self):
        subprocess.run(["explorer", os.path.join(self.main_folder, "raw")])

    def open_output_folder(self):
        subprocess.run(["explorer", os.path.join(self.main_folder, "results")])

    def show_about(self):
        about_text = "So-Vits-SVC-4.1 GUI\n程序版本：1.0\n作者：Right_Pro和ChatGPT\n本程序仅为So-Vits-SVC的训练及推理提供GUI启动按钮，与项目本体无关。"
        messagebox.showinfo("关于", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoVitsSVCApp(root)
    root.mainloop()
