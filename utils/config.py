from __future__ import annotations
import os
import copy
from typing import Dict, Any, TypedDict, Optional, List
import json

from utils.constants import CAT_TAGS, DOG_TAGS


class ConfigType(TypedDict):
  cat: AnimalConfig
  dog: AnimalConfig


class AnimalConfig(TypedDict):
  enabled: bool
  name: str
  api_key: str
  twitter: TwitterConfig
  tumblr: TumblrConfig
  bluesky: BlueskyConfig


class TwitterConfig(TypedDict):
  enabled: bool
  consumer_key: str
  consumer_secret: str
  access_token: str
  access_token_secret: str


class TumblrConfig(TypedDict):
  enabled: bool
  tags: List[str]
  blogname: str
  consumer_key: str
  consumer_secret: str
  oauth_token: str
  oauth_token_secret: str


class BlueskyConfig(TypedDict):
  enabled: bool
  username: str
  app_password: str


class Config:
  path: str
  cfg: ConfigType

  def __init__(self, path: str):
    self.path = path
    self.cfg = ConfigType(
      cat=AnimalConfig(
        enabled=False,
        name="TheCatAPI",
        api_key="",
        twitter=TwitterConfig(enabled=False, consumer_key="", consumer_secret="", access_token="", access_token_secret=""),
        tumblr=TumblrConfig(
          enabled=False,
          tags=list(CAT_TAGS),
          blogname="",
          consumer_key="",
          consumer_secret="",
          oauth_token="",
          oauth_token_secret=""
        ),
        bluesky=BlueskyConfig(enabled=False, username="", app_password=""),
      ),
      dog=AnimalConfig(
        enabled=False,
        name="TheDogAPI",
        api_key="",
        twitter=TwitterConfig(enabled=False, consumer_key="", consumer_secret="", access_token="", access_token_secret=""),
        tumblr=TumblrConfig(enabled=False, tags=list(DOG_TAGS), blogname="", consumer_key="", consumer_secret="", oauth_token="", oauth_token_secret=""),
        bluesky=BlueskyConfig(enabled=False, username="", app_password=""),
      )
    )

    self.load()

  def save(self):
    with open(self.path, "w", encoding="utf-8") as f:
      json.dump(self.cfg, f, indent=2, ensure_ascii=False)

  def load(self):
    if not os.path.exists(self.path):
      self.save()
      return

    with open(self.path, "r", encoding="utf-8") as f:
      loaded_cfg = json.load(f)

    cat_config = loaded_cfg.get("cat", {})
    cat_twitter = cat_config.get("twitter", {})
    cat_tumblr = cat_config.get("tumblr", {})
    cat_bluesky = cat_config.get("bluesky", {})

    dog_config = loaded_cfg.get("dog", {})
    dog_twitter = dog_config.get("twitter", {})
    dog_tumblr = dog_config.get("tumblr", {})
    dog_bluesky = dog_config.get("bluesky", {})

    old_cfg = copy.deepcopy(self.cfg)
    self.cfg = ConfigType(
      cat=AnimalConfig(
        enabled=cat_config.get("enabled", True),
        name=cat_config.get("name", "TheCatAPI"),
        api_key=cat_config.get("api_key", ""),
        twitter=TwitterConfig(
          enabled=cat_twitter.get("enabled", False),
          consumer_key=cat_twitter.get("consumer_key", ""),
          consumer_secret=cat_twitter.get("consumer_secret", ""),
          access_token=cat_twitter.get("access_token", ""),
          access_token_secret=cat_twitter.get("access_token_secret", "")
        ),
        tumblr=TumblrConfig(
          enabled=cat_tumblr.get("enabled", False),
          tags=cat_tumblr.get("tags", list(CAT_TAGS)),
          blogname=cat_tumblr.get("blogname", ""),
          consumer_key=cat_tumblr.get("consumer_key", ""),
          consumer_secret=cat_tumblr.get("consumer_secret", ""),
          oauth_token=cat_tumblr.get("oauth_token", ""),
          oauth_token_secret=cat_tumblr.get("oauth_token_secret", "")
        ),
        bluesky=BlueskyConfig(
          enabled=cat_bluesky.get("enabled", False),
          username=cat_bluesky.get("username", ""),
          app_password=cat_bluesky.get("app_password", "")
        )
      ),
      dog=AnimalConfig(
        enabled=dog_config.get("enabled", True),
        name=dog_config.get("name", "TheDogAPI"),
        api_key=dog_config.get("api_key", ""),
        twitter=TwitterConfig(
          enabled=dog_twitter.get("enabled", False),
          consumer_key=dog_twitter.get("consumer_key", ""),
          consumer_secret=dog_twitter.get("consumer_secret", ""),
          access_token=dog_twitter.get("access_token", ""),
          access_token_secret=dog_twitter.get("access_token_secret", "")
        ),
        tumblr=TumblrConfig(
          enabled=dog_tumblr.get("enabled", False),
          tags=dog_tumblr.get("tags", list(DOG_TAGS)),
          blogname=dog_tumblr.get("blogname", ""),
          consumer_key=dog_tumblr.get("consumer_key", ""),
          consumer_secret=dog_tumblr.get("consumer_secret", ""),
          oauth_token=dog_tumblr.get("oauth_token", ""),
          oauth_token_secret=dog_tumblr.get("oauth_token_secret", "")
        ),
        bluesky=BlueskyConfig(
          enabled=dog_bluesky.get("enabled", False),
          username=dog_bluesky.get("username", ""),
          app_password=dog_bluesky.get("app_password", "")
        )
      )
    )

    if old_cfg != self.cfg:
      self.save()

  def __str__(self) -> str:
    return json.dumps(self.cfg, indent=2, ensure_ascii=False)

cfg = Config("config.json")
