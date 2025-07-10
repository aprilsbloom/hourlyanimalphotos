from __future__ import annotations
import os
from typing import Dict, Any, TypedDict, Optional
import json


class ConfigType(TypedDict):
  cat: AnimalConfig
  dog: AnimalConfig


class AnimalConfig(TypedDict):
  name: str
  api_key: str
  twitter: TwitterConfig
  tumblr: TumblrConfig
  bluesky: BlueskyConfig


class TwitterConfig(TypedDict):
  enabled: bool
  username: str
  consumer_key: str
  consumer_secret: str
  access_token: str
  access_token_secret: str


class TumblrConfig(TypedDict):
  enabled: bool
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
    self.load()

  def save(self):
    with open(self.path, "w") as f:
      json.dump(self.cfg, f, indent=2)

  def load(self):
    if not os.path.exists(self.path):
      self.save()
      return

    with open(self.path, "r") as f:
      loaded_cfg = json.load(f)

    cat_config = loaded_cfg.get("cat", {})
    cat_twitter = cat_config.get("twitter", {})
    cat_tumblr = cat_config.get("tumblr", {})
    cat_bluesky = cat_config.get("bluesky", {})

    dog_config = loaded_cfg.get("dog", {})
    dog_twitter = dog_config.get("twitter", {})
    dog_tumblr = dog_config.get("tumblr", {})
    dog_bluesky = dog_config.get("bluesky", {})

    self.cfg = ConfigType(
      cat=AnimalConfig(
        name=cat_config.get("name", "TheCatAPI"),
        api_key=cat_config.get("api_key", ""),
        twitter=TwitterConfig(
          enabled=cat_twitter.get("enabled", False),
          username=cat_twitter.get("username", ""),
          consumer_key=cat_twitter.get("consumer_key", ""),
          consumer_secret=cat_twitter.get("consumer_secret", ""),
          access_token=cat_twitter.get("access_token", ""),
          access_token_secret=cat_twitter.get("access_token_secret", "")
        ),
        tumblr=TumblrConfig(
          enabled=cat_tumblr.get("enabled", False),
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
        name=dog_config.get("name", "TheDogAPI"),
        api_key=dog_config.get("api_key", ""),
        twitter=TwitterConfig(
          enabled=dog_twitter.get("enabled", False),
          username=dog_twitter.get("username", ""),
          consumer_key=dog_twitter.get("consumer_key", ""),
          consumer_secret=dog_twitter.get("consumer_secret", ""),
          access_token=dog_twitter.get("access_token", ""),
          access_token_secret=dog_twitter.get("access_token_secret", "")
        ),
        tumblr=TumblrConfig(
          enabled=dog_tumblr.get("enabled", False),
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

  def __str__(self) -> str:
    return json.dumps(self.cfg, indent=2)


# Example usage
config_data = ConfigType(
  cat=AnimalConfig(
    name="TheCatAPI",
    api_key="",
    twitter=TwitterConfig(
      enabled=False,
      username="",
      consumer_key="",
      consumer_secret="",
      access_token="",
      access_token_secret="",
    ),
    tumblr=TumblrConfig(
      enabled=False,
      blogname="",
      consumer_key="",
      consumer_secret="",
      oauth_token="",
      oauth_token_secret="",
    ),
    bluesky=BlueskyConfig(
      enabled=False,
      username="",
      app_password=""
    )
  ),
  dog=AnimalConfig(
    name="TheDogAPI",
    api_key="",
    twitter=TwitterConfig(
      enabled=False,
      username="",
      consumer_key="",
      consumer_secret="",
      access_token="",
      access_token_secret="",
    ),
    tumblr=TumblrConfig(
      enabled=False,
      blogname="",
      consumer_key="",
      consumer_secret="",
      oauth_token="",
      oauth_token_secret="",
    ),
    bluesky=BlueskyConfig(
      enabled=False,
      username="",
      app_password=""
    )
  )
)
config = Config("config.json")

# Access typed fields example
twitter_enabled = config.cfg["cat"]["twitter"]["enabled"]
twitter_username = config.cfg["dog"]["twitter"]["username"]

print(twitter_enabled)
print(twitter_username)
# Print stringified config
print(str(config))
