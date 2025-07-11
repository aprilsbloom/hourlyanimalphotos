import requests

from sources import ImageSource
from utils.config import Config
from utils.logger import Logger

class DogAPI(ImageSource):
  def __init__(self, cfg: Config):
    super().__init__(cfg, 'dog')

    self.name = 'TheDogAPI'
    self.url = 'https://api.thedogapi.com/v1/images/search?mime_types=jpg,png'
    self.logger = Logger(self.name)

  def fetch_img(self) -> bytes | None:
    # get url
    url = self.fetch_img_url()
    if not url:
      self.logger.error(f'Failed to fetch image from {self.url}: No URL was returned.')
      return None

    self.logger.success(f'Fetched image! Got: {url}')

    # fetch image
    res = requests.get(url)
    if res.status_code != 200:
      self.logger.error(f'Failed to fetch image from {self.url}: Status code {res.status_code}')
      print(res.text)
      return None

    return res.content

  def fetch_img_url(self) -> str:
    cfg = self.cfg.cfg[self.cfg_key]
    api_key = cfg['api_key']

    self.logger.info(f'Fetching image from {self.url}')
    res = requests.get(
      url = self.url,
      headers = { 'x-api-key': api_key }
    )

    # dogapi returns a list of images
    data = res.json()
    if isinstance(data, list):
      data = data[0]

    url = data.get('url', '')
    return url