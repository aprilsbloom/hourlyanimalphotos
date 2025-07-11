import requests

from sources import ImageSource
from utils.globals import log
from utils.config import Config

class CatAPI(ImageSource):
  def __init__(self, cfg: Config):
    super().__init__(cfg, 'cat')

    self.name = 'TheCatAPI'
    self.url = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png'

  def fetch_img(self) -> bytes | None:
    # get url
    url = self.fetch_img_url()
    if not url:
      return None

    # fetch image
    res = requests.get(url)
    if res.status_code != 200:
      return None

    return res.content

  def fetch_img_url(self) -> str:
    cfg = self.cfg.cfg[self.cfg_key]
    api_key = cfg['api_key']

    res = requests.get(
      url = self.url,
      headers = { 'x-api-key': api_key }
    )

    # catapi returns a list of images
    data = res.json()
    if isinstance(data, list):
      data = data[0]

    url = data.get('url', '')
    return url
