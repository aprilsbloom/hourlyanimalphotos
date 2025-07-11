from abc import ABC, abstractmethod
from typing import Literal

from utils.config import Config
from utils.logger import Logger

class ImageSource(ABC):
  cfg: Config
  cfg_key: Literal['cat', 'dog']

  name: str
  url: str
  logger: Logger

  def __init__(self, cfg: Config, cfg_key: Literal['cat', 'dog']):
    self.cfg = cfg
    self.cfg_key = cfg_key

  @abstractmethod
  def fetch_img(self) -> bytes | None:
    pass

  @abstractmethod
  def fetch_img_url(self) -> str:
    pass


from sources.catapi import CatAPI
from sources.dogapi import DogAPI

__all__ = ['ImageSource', 'CatAPI', 'DogAPI']