#python编写一个gui应用，界面如下：
#stun 状态：
#[公共/私有] [地址]
#[按钮，切换公共私有]
#[输入框，配置本地stun端口，占位3478]
#[按钮，启动或终止stun服务器]
#[显示当前私有stun服务器是否运行和端口]
#---
#weblink server:
#[可编辑的单行输入框，输入默认stun服务器] 
#[按钮，npm run build更新默认stun地址]
#[按钮，启动或终止weblink server]
#[显示当前weblink server状态]
#---
#weblink websocket server:
#[npm run build按钮]
#[启动或终止按钮]
#[状态显示]

#当启动私有stun服务器时，非阻塞运行stunserver_win64_1_2_16/release/stunserver --primaryport [配置的端口]
#当启动weblink server时，非阻塞运行./caddy file-server --listen :%port% --root ./weblink/dist --browse
#当启动weblink websocket server时，非阻塞运行weblink-ws-server/node_modules/@oven/bun-windows-x64-baseline/bin/bun run weblink-ws-server/dist/index.js


import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import socket

class STUNApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("STUN and Weblink Servers Control Panel")
        self.geometry('800x500')  # Increased height to accommodate new line status
        
        # STUN Server Section
        stun_frame = ttk.LabelFrame(self, text="本地STUN服务器", padding=(10, 5))
        stun_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(stun_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        
        self.stun_port_entry = ttk.Entry(stun_frame)
        self.stun_port_entry.insert(0, "3478")
        self.stun_port_entry.pack(side=tk.LEFT, padx=5)
        
        self.stun_start_stop_button = ttk.Button(stun_frame, text="启动",
                                                 command=self.toggle_stun_server)
        self.stun_start_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.stun_status_label = ttk.Label(self, text="STUN服务器未运行")
        self.stun_status_label.pack(pady=5)

        # Weblink WebSocket Server Section
        websocket_frame = ttk.LabelFrame(self, text="Weblink WebSocket server", padding=(10, 5))
        websocket_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(websocket_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.webs_default_port_entry = ttk.Entry(websocket_frame)
        self.webs_default_port_entry.pack(side=tk.LEFT, padx=5)
        
        self.websocket_build_button = ttk.Button(websocket_frame, text="npm run build",
                                                 command=self.build_websocket)
        self.websocket_build_button.pack(side=tk.LEFT, padx=5)
        
        self.websocket_start_stop_button = ttk.Button(websocket_frame, text="启动",
                                                      command=self.toggle_websocket_server)
        self.websocket_start_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.websocket_status_label = ttk.Label(self, text="WebSocket服务器未运行")
        self.websocket_status_label.pack(pady=5)
        
        # Weblink Server Section
        weblink_frame = ttk.LabelFrame(self, text="Weblink server", padding=(10, 5))
        weblink_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(weblink_frame, text="stun:").pack(side=tk.LEFT, padx=5)
        self.weblink_default_stun_entry = ttk.Entry(weblink_frame)
        self.weblink_default_stun_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(weblink_frame, text="websocket:").pack(side=tk.LEFT, padx=5)
        self.weblink_default_ws_entry = ttk.Entry(weblink_frame)
        self.weblink_default_ws_entry.pack(side=tk.LEFT, padx=5)

        self.weblink_build_button = ttk.Button(weblink_frame, text="npm run build",
                                               command=self.update_weblink_stun)
        self.weblink_build_button.pack(side=tk.LEFT, padx=5)

        #在下一行配置网页端口
        weblink_frame1 = ttk.LabelFrame(self)
        weblink_frame1.pack(fill=tk.X, padx=10)
        ttk.Label(weblink_frame1, text="user web port:").pack(side=tk.LEFT, padx=5)
        self.weblink_default_runport_entry = ttk.Entry(weblink_frame1)
        self.weblink_default_runport_entry.pack(side=tk.LEFT, padx=5)
        
        self.weblink_start_stop_button = ttk.Button(weblink_frame1, text="启动",
                                                    command=self.toggle_weblink_server)
        self.weblink_start_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.weblink_status_label = ttk.Label(self, text="Weblink服务器未运行")
        self.weblink_status_label.pack(pady=5)

        #获取当前设备所处的所有ip地址并逐行显示到可复制不可编辑的长度为100%的文本框中。ipv4
        ip_list = []
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127."):
                ip_list.append(ip)
        ip_text = "\n".join(ip_list)
        self.ip_text = tk.Text(self, height=5, width=100)
        self.ip_text.insert(tk.END, ip_text)
        self.ip_text.pack(pady=5)


        
        self.stun_process = None
        self.weblink_process = None
        self.websocket_process = None

    def update_weblink_stun(self):

        #如果weblink_default_stun_entry为空，则写入stun.l.google.com:19302
        if self.weblink_default_stun_entry.get() == "":
            self.weblink_default_stun_entry.insert(0, "stun.l.google.com:19302")

        #如果weblink_default_ws_entry为空，则写入ws://localhost:9000
        if self.weblink_default_ws_entry.get() == "":
            self.weblink_default_ws_entry.insert(0, "localhost:9000")

        #更新weblink\src\options.ts的第100行的方括号内的内容(指向getDefaultAppOptions函数的server stun。可能随着weblink源码更新而需要改写)
        #例如stuns: ["stun:stun.l.google.com:19302"],，修改stuns后内容为weblink_default_stun_entry的内容
        with open('weblink\\src\\options.ts', 'r') as file:
            lines = file.readlines()
        with open('weblink\\src\\options.ts', 'w') as file:
            for index, line in enumerate(lines):
                if index == 99:
                    #找到这行中的[stun:
                    start = line.find('["stun:')
                    end = line.find('"],')
                    file.write(line[:start+7] + f'{self.weblink_default_stun_entry.get()}' + line[end:])
                else:
                    file.write(line)

        #更新weblink\src\routes\setting.tsx的第430行内容，这是网页对应设置项的默认占空
        with open('weblink\\src\\routes\\setting.tsx', 'r') as file:
            lines = file.readlines()
        with open('weblink\\src\\routes\\setting.tsx', 'w') as file:
            for index, line in enumerate(lines):
                if index == 429:
                    #找到这行中的placeholder="stun.l.google.com:19302"
                    start = line.find('placeholder="stun:')
                    file.write(line[:start+18] + f'{self.weblink_default_stun_entry.get()}"\n')
                else:
                    file.write(line)

        #更新weblink\.env.local中的VITE_WEBSOCKET_URL为weblink_default_ws_entry的内容
        with open('weblink\\.env.local', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open('weblink\\.env.local', 'w', encoding='utf-8') as file:
            for line in lines:
                if line.startswith('VITE_WEBSOCKET_URL='):
                    file.write(f'VITE_WEBSOCKET_URL=ws://{self.weblink_default_ws_entry.get()}\n')
                else:
                    file.write(line)
                    
        #在weblink目录下运行npm run build
        process = subprocess.Popen('cd weblink && npm run build', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            self.weblink_status_label.config(text="默认STUN地址已更新")
        else:
            self.weblink_status_label.config(text="更新默认STUN地址失败")


    def build_websocket(self):
        #修改weblink-ws-server\.env中的PORT配置，如果为空则写入9000
        if self.webs_default_port_entry.get() == "":
            self.webs_default_port_entry.insert(0, "9000")
        with open('weblink-ws-server\\.env', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open('weblink-ws-server\\.env', 'w', encoding='utf-8') as file:
            for line in lines:
                if line.startswith('PORT='):
                    file.write(f'PORT={self.webs_default_port_entry.get()}\n')
                else:
                    file.write(line)

        #在weblink-ws-server目录下运行npm run build
        process = subprocess.Popen('cd weblink-ws-server && npm run build', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            self.websocket_status_label.config(text="WebSocket服务器已构建")
        else:
            self.websocket_status_label.config(text="构建WebSocket服务器失败")


    def toggle_stun_server(self):
        if self.stun_start_stop_button['text'] == "启动":
            port = self.stun_port_entry.get()
            self.stun_process = self.start_service(f'stunserver_win64_1_2_16\\release\\stunserver --primaryport {port}', 
                                                   'STUN服务器已启动', self.stun_status_label)
            self.stun_start_stop_button.config(text="终止")
        else:
            self.stop_service(self.stun_process, 'STUN服务器未运行', self.stun_status_label)
            self.stun_start_stop_button.config(text="启动")

    def toggle_weblink_server(self):
        if self.weblink_start_stop_button['text'] == "启动":
            port = self.weblink_default_runport_entry.get()
            self.weblink_process = self.start_service(f'caddy file-server --listen 0.0.0.0:{port} --root ./weblink/dist --browse',
                                                     'Weblink服务器已启动', self.weblink_status_label)
            self.weblink_start_stop_button.config(text="终止")
        else:
            self.stop_service(self.weblink_process, 'Weblink服务器未运行', self.weblink_status_label)
            self.weblink_start_stop_button.config(text="启动")

    def toggle_websocket_server(self):
        if self.websocket_start_stop_button['text'] == "启动":
            self.websocket_process = self.start_service('weblink-ws-server\\node_modules\\@oven/bun-windows-x64-baseline\\bin\\bun run weblink-ws-server/dist/index.js',
                                                       'WebSocket服务器已启动', self.websocket_status_label)
            self.websocket_start_stop_button.config(text="终止")
        else:
            self.stop_service(self.websocket_process, 'WebSocket服务器未运行', self.websocket_status_label)
            self.websocket_start_stop_button.config(text="启动")

    def start_service(self, cmd, success_msg, status_label):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def monitor():
            try:
                stdout, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            finally:
                status_label.config(text=success_msg)
                
        threading.Thread(target=monitor).start()
        return process

    def stop_service(self, process, msg, status_label):
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            status_label.config(text=msg)

if __name__ == "__main__":
    app = STUNApp()
    app.mainloop()