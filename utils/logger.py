from datetime import datetime

colors = {
  "red": "\033[91m",
  "yellow": "\033[93m",
  "green": "\033[92m",
  "grey": "\033[90m",
  "reset": "\033[37m"
}

class Logger:
  name: str

  def __init__(self, name: str):
    self.name = name

  @staticmethod
  def fetch_time():
    time = datetime.now().strftime("%H:%M:%S")
    return f"[{time}]"

  def info(self, text):
    print(f"{self.fetch_time()} [{self.name}] {colors['grey']}[~]{colors['reset']} {text}")

  def error(self, text):
    print(f"{self.fetch_time()} [{self.name}] {colors['red']}[-]{colors['reset']} {text}")

  def warning(self, text):
    print(f"{self.fetch_time()} [{self.name}] {colors['yellow']}[!]{colors['reset']} {text}")

  def success(self, text):
    print(f"{self.fetch_time()} [{self.name}] {colors['green']}[+]{colors['reset']} {text}")
