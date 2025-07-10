from abc import ABC, abstractmethod
from sources.catapi import CatAPI
from sources.dogapi import DogAPI

from utils.config import Config

class ImageSource(ABC):
  cfg: Config
  cfg_key: str

  name: str
  url: str

  def __init__(self, cfg: Config, cfg_key: str):
    self.cfg = cfg
    self.cfg_key = cfg_key

  @abstractmethod
  def fetch_img(self) -> bytes:
    pass

__all__ = ['ImageSource', 'CatAPI', 'DogAPI']