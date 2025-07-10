import requests

from sources import ImageSource
from utils.globals import IMG_PATH, log
from utils.config import Config

class CatAPI(ImageSource):
  def __init__(self, cfg: Config):
    super().__init__(cfg, 'cat')

    self.name = 'TheCatAPI'
    self.url = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png'

  def fetch_img(self) -> bytes:
    cfg = self.cfg.cfg[self.cfg_key]
    api_key = cfg['api_key']

    res = requests.get(
      url = self.url,
      headers = { 'x-api-key': api_key }
    )

    return bytes()