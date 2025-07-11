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

  def info(self, *args, **kwargs):
    print(f"{self.fetch_time()} [{self.name}] {colors['grey']}[~]{colors['reset']}", *args, **kwargs)

  def error(self, *args, **kwargs):
    print(f"{self.fetch_time()} [{self.name}] {colors['red']}[-]{colors['reset']}", *args, **kwargs)

  def warning(self, *args, **kwargs):
    print(f"{self.fetch_time()} [{self.name}] {colors['yellow']}[!]{colors['reset']}", *args, **kwargs)

  def success(self, *args, **kwargs):
    print(f"{self.fetch_time()} [{self.name}] {colors['green']}[+]{colors['reset']}", *args, **kwargs)
