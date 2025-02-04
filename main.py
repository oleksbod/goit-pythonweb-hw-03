import mimetypes
import pathlib
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Storage data.json read and write
def load_data():
    if pathlib.Path("storage/data.json").exists():
        with open("storage/data.json", "r") as f:
            return json.load(f)
    return {}


def save_data(data):
    pathlib.Path("storage").mkdir(parents=True, exist_ok=True)
    with open("storage/data.json", "w") as f:
        json.dump(data, f, indent=4)


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        data = load_data()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data[timestamp] = {
            "username": data_dict.get("username"),
            "message": data_dict.get("message"),
        }
        save_data(data)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_read_page()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_read_page(self):
        data = load_data()

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('data.html')

        content = template.render(data=data)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
