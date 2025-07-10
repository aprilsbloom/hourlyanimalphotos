import requests

from sources import ImageSource
from utils.globals import IMG_PATH, log
from utils.config import Config

class DogAPI(ImageSource):
  def __init__(self, cfg: Config):
    super().__init__(cfg, 'dog')

    self.name = 'TheDogAPI'
    self.url = 'https://api.thedogapi.com/v1/images/search?mime_types=jpg,png'

  def fetch_img(self) -> bytes:
    cfg = self.cfg.cfg[self.cfg_key]
    api_key = cfg['api_key']

    res = requests.get(
      url = self.url,
      headers = { 'x-api-key': api_key }
    )

    return bytes()