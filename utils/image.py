import io
import os
from pathlib import Path
from PIL import Image
import uuid

jobs_dir = Path('./jobs')
jobs_dir.mkdir(parents=True, exist_ok=True)

class SourceImage:
  data: bytes
  id: str
  path: Path

  def __init__(self, data: bytes):
    self.data = data
    self.id = str(uuid.uuid4())
    self.path = jobs_dir / f'{self.id}.webp'
    self.save(convert_to_webp=True)

  def cleanup(self):
    os.remove(self.path)

  def save(self, convert_to_webp: bool = False):
    if convert_to_webp:
      # convert self.data to webp
      img = Image.open(io.BytesIO(self.data))
      img.save(self.path, 'webp', quality=100)

      # re-read the file to get converted webp data
      self.re_read()

    with open(self.path, 'wb') as f:
      f.write(self.data)

  def read(self) -> bytes:
    with open(self.path, 'rb') as f:
      return f.read()

  def re_read(self):
    with open(self.path, 'rb') as f:
      self.data = f.read()

  def get_size_mb(self) -> float:
    return os.path.getsize(self.path) / 1000 / 1000

  def get_dimensions(self) -> tuple[int, int]:
    with open(self.path, 'rb') as f:
      img = Image.open(f)
      return img.width, img.height

  def resize(self, width: int, height: int, quality: int = 100):
    img = Image.open(self.path)
    img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(self.path, 'webp', quality=quality)