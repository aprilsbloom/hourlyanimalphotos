import io
import os
from pathlib import Path
from PIL import Image
import uuid

jobs_dir = Path('./jobs')
jobs_dir.mkdir(parents=True, exist_ok=True)

class SourceImage:
  id: str
  path: Path
  _img: Image.Image

  def __init__(self, data: bytes):
    self.id = str(uuid.uuid4())
    self.path = jobs_dir / f'{self.id}.webp'
    self._img = Image.open(io.BytesIO(data))
    self.save(convert_to_webp=True)

  def cleanup(self):
    os.remove(self.path)

  def save(self, convert_to_webp: bool = False):
    jobs_dir.mkdir(parents=True, exist_ok=True)

    self._img.save(self.path, 'webp', quality=100)
    if convert_to_webp:
      self.reload_image()

  def read(self) -> bytes:
    with open(self.path, 'rb') as f:
      return f.read()

  def reload_image(self):
    with open(self.path, 'rb') as f:
      self._img = Image.open(f)
      self._img.load()

  def get_size_mb(self) -> float:
    return os.path.getsize(self.path) / 1000 / 1000

  def get_dimensions(self) -> tuple[int, int]:
    return self._img.width, self._img.height

  def resize(self, width: int, height: int, quality: int = 100):
    self._img = self._img.resize((width, height), Image.Resampling.LANCZOS)
    self._img.save(self.path, 'webp', quality=quality)