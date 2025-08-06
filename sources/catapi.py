import requests
from copy import deepcopy

from sources import ImageSource
from utils.config import Config
from utils.logger import Logger
from utils.constants import BASE_HEADERS, REQUEST_TIMEOUT

class CatAPI(ImageSource):
  def __init__(self, cfg: Config):
    super().__init__(cfg, 'cat')

    self.name = 'TheCatAPI'
    self.url = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png'
    self.logger = Logger(self.name)

  def fetch_img(self) -> bytes | None:
    # get url
    url = self.fetch_img_url()
    if not url:
      self.logger.error(f'Failed to fetch image from {self.url}: No URL was returned.')
      return None

    self.logger.success(f'Fetched image! Got: {url}')

    # fetch image
    res = requests.get(url, headers = BASE_HEADERS, timeout = REQUEST_TIMEOUT)
    if res.status_code != 200:
      self.logger.error(f'Failed to fetch image from {self.url}: Status code {res.status_code}\n{res.text}')
      return None

    return res.content

  def fetch_img_url(self) -> str:
    cfg = self.cfg.cfg[self.cfg_key]
    headers = deepcopy(BASE_HEADERS)
    headers['x-api-key'] = cfg['api_key']

    self.logger.info(f'Fetching image from {self.url}')
    res = requests.get(
      url = self.url,
      headers = headers
    )

    # catapi returns a list of images
    try;
      data = res.json()
    except:
      return

    if isinstance(data, list):
      data = data[0]

    url = data.get('url', '')
    return url
