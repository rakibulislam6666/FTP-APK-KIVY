from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from threading import Thread
import http.server
import socketserver
import cgi
import os
import urllib.parse
import json
import socket
import time

PORT = 8040
UPLOAD_DIR = "/sdcard/RAKIBUL_ISLAM"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None  # None দিলে বোঝা যাবে হটস্পট নেই

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/home"  or self.path == "/index":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("HOME.HTML", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/send_file" :
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("send_file.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/receive_file" :
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("receive_file.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path.startswith("/files/"):
            filename = urllib.parse.unquote(self.path[len("/files/"):])
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                self.send_response(200)
                self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found.")


        elif self.path == "/list":
            try:
                files = os.listdir(UPLOAD_DIR)
            except FileNotFoundError:
                files = []
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())

        else:
            self.send_error(404, "File not found.")

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        files = form["file"]
        if not isinstance(files, list):
            files = [files]

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        for file_item in files:
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_item.file.read())

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Files uploaded successfully.')


class RAKIBULS_HPFTPApp(App):

    def start_server(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
            print(f"Server running on https://localhost:{PORT}")
            httpd.serve_forever()

    def update_status(self, *args):
        ip = get_local_ip()
        if ip:
            try:
                files = os.listdir(UPLOAD_DIR)
            except FileNotFoundError:
                files = []
            self.label.text = f"Hotspot IP: {ip}\nServer: http://{ip}:{PORT}\n\nPublic Files List:\n" + "\n".join(files) if files else f"Hotspot IP: {ip}\nServer: http://{ip}:{PORT}\n(No files)"
          
        else:
            self.label.text = "Please ON Hotspot!"

    def on_start(self):
        Thread(target=self.start_server, daemon=True).start()
        Clock.schedule_interval(self.update_status, 2)

    def build(self):
        self.label = Label(text="Checking Hotspot...")
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        return layout


if __name__ == '__main__':
    RAKIBULS_HPFTPApp().run()

