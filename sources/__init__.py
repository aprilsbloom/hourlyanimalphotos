from abc import ABC, abstractmethod

from utils.config import AnimalType, Config
from utils.logger import Logger

class ImageSource(ABC):
  cfg: Config
  cfg_key: AnimalType

  name: str
  url: str
  logger: Logger

  def __init__(self, cfg: Config, cfg_key: AnimalType):
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