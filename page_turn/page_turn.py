from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import sys

class RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == "/":
      self.serve_index()
    else:
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"Not Found")

  def serve_index(self):
    try:
      with open("index.html", "rb") as file:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(file.read())
    except FileNotFoundError:
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"index.html not found")

  def do_POST(self):
    print("POST request received", self.path)

    if self.path == "/next":
      self.run_command("evemu-play /dev/input/event1 < ./next_page")
    elif self.path == "/previous":
      self.run_command("evemu-play /dev/input/event1 < ./previous_page")
    elif self.path == "/stop":
      self.send_response(200)
      self.end_headers()
      self.wfile.write(b"Stopping server...")
      sys.exit(0)
    else:
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"Not Found")

  def run_command(self, command):
    try:
      result = subprocess.run(command, shell=True, capture_output=True, text=True)
      self.send_response(200)
      self.end_headers()
      self.wfile.write(result.stdout.encode() if result.stdout else b"Command executed")
    except Exception as e:
      self.send_response(500)
      self.end_headers()
      self.wfile.write(f"Exception: {str(e)}".encode())

def setup():
  # Open port 8080 in iptables
  command = "/usr/sbin/iptables -A INPUT -i wlan0 -p tcp --dport 8080 -j ACCEPT"
  subprocess.run(command, shell=True, capture_output=True, text=True)
  print("Opened port 8080")

def cleanup():
  # Close port 8080 in iptables
  command = "/usr/sbin/iptables -D INPUT -i wlan0 -p tcp --dport 8080 -j ACCEPT"
  subprocess.run(command, shell=True, capture_output=True, text=True)
  print("Closed port 8080")

if __name__ == "__main__":
  setup()

  server_address = ("", 8080)
  httpd = HTTPServer(server_address, RequestHandler)
  print("Server running on port 8080...")

  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print("Shutting down server...")
    cleanup()
    httpd.server_close()
