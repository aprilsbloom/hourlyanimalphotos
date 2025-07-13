from __future__ import annotations
import os
import copy
from typing import TypedDict, List, Literal
import json
import time
import threading

from requests_oauthlib import OAuth1Session
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from utils.logger import Logger
from utils.constants import CAT_TAGS, DOG_TAGS

AnimalType = Literal['cat', 'dog']

class ConfigType(TypedDict):
  cat: AnimalConfig
  dog: AnimalConfig


class AnimalConfig(TypedDict):
  enabled: bool
  key: AnimalType
  name: str
  api_key: str
  twitter: TwitterConfig
  tumblr: TumblrConfig
  bluesky: BlueskyConfig
  webhooks: DiscordWebhooks


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


class DiscordWebhooks(TypedDict):
  twitter: str
  tumblr: str
  bluesky: str


class Config:
  path: str
  cfg: ConfigType
  log: Logger
  _observer: BaseObserver
  _saving: bool = False

  def __init__(self, path: str):
    self.path = path
    self.log = Logger("Config")

    self.load()
    self.watch()

  def save(self):
    self._saving = True
    with open(self.path, "w", encoding="utf-8") as f:
      json.dump(self.cfg, f, indent=2, ensure_ascii=False)

    def reset_is_saving():
      time.sleep(1)
      self._saving = False

    threading.Thread(target=reset_is_saving, daemon=True).start()

  def is_saving(self):
    return self._saving

  def load(self):
    if os.path.exists(self.path):
      with open(self.path, "r", encoding="utf-8") as f:
        loaded_cfg = json.load(f)
    else:
      loaded_cfg = {}

    cat_config = loaded_cfg.get("cat", {})
    cat_twitter = cat_config.get("twitter", {})
    cat_tumblr = cat_config.get("tumblr", {})
    cat_bluesky = cat_config.get("bluesky", {})
    cat_discord_webhooks = cat_config.get("discord_webhooks", {})

    dog_config = loaded_cfg.get("dog", {})
    dog_twitter = dog_config.get("twitter", {})
    dog_tumblr = dog_config.get("tumblr", {})
    dog_bluesky = dog_config.get("bluesky", {})
    dog_discord_webhooks = dog_config.get("discord_webhooks", {})

    old_cfg = copy.deepcopy(self.cfg) if hasattr(self, 'cfg') else None

    self.cfg = ConfigType(
      cat=AnimalConfig(
        enabled=cat_config.get("enabled", True),
        key="cat",
        name="TheCatAPI",
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
        ),
        webhooks=DiscordWebhooks(
          twitter=cat_discord_webhooks.get("twitter", ""),
          tumblr=cat_discord_webhooks.get("tumblr", ""),
          bluesky=cat_discord_webhooks.get("bluesky", "")
        )
      ),
      dog=AnimalConfig(
        enabled=dog_config.get("enabled", True),
        key="dog",
        name="TheDogAPI",
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
        ),
        webhooks=DiscordWebhooks(
          twitter=dog_discord_webhooks.get("twitter", ""),
          tumblr=dog_discord_webhooks.get("tumblr", ""),
          bluesky=dog_discord_webhooks.get("bluesky", "")
        )
      )
    )

    if old_cfg != self.cfg:
      self.save()

  def watch(self):
    class ConfigFileHandler(FileSystemEventHandler):
      config: Config
      last_modified: float

      def __init__(self, config_instance):
        self.config = config_instance
        self.last_modified = os.path.getmtime(self.config.path)

      def on_modified(self, event):
        # skip if not modified event
        if not isinstance(event, FileModifiedEvent):
          return

        # skip if modification from saving
        if self.config.is_saving():
          return

        # skip if fired in short period
        if time.time() - self.last_modified < 1:
          return

        self.last_modified = time.time()

        # reload cfg if modified
        if event.src_path == os.path.abspath(self.config.path):
          self.config.log.info("Config file modified, reloading...")
          self.config.load()
          self.config.validate()

    observer = Observer()
    handler = ConfigFileHandler(self)
    observer.schedule(handler, os.path.dirname(os.path.abspath(self.path)), recursive=False)
    observer.start()

    self._observer = observer

  def validate(self, should_exit: bool = False) -> None:
    exit_needed = False

    # validate cfg entries
    # if a social media platform is enabled, ensure all keys are set
    has_found_enabled_source = False
    for source in self.cfg:
      source_cfg = self.cfg[source]

      # skip if not enabled
      if not source_cfg['enabled']:
        continue

      has_found_enabled_source = True

      # needs an api key to function lol
      if not source_cfg['api_key']:
        self.log.error(f'API key is not set for source "{source}" ("{source_cfg["name"]}").')
        exit_needed = True

      # twitter
      if source_cfg['twitter']['enabled']:
        twitter_keys = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
        missing_keys = []
        for key in twitter_keys:
          if not source_cfg['twitter'][key]:
            missing_keys.append(key)

        if len(missing_keys) > 0:
          self.log.error(f'The following keys for Twitter in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}.')

          if source_cfg['twitter']['enabled']:
            self.log.info(f'Twitter in source "{source}" ("{source_cfg["name"]}") has now been disabled for you.')
            source_cfg['twitter']['enabled'] = False
            self.save()

          exit_needed = True

      # tumblr
      if source_cfg['tumblr']['enabled']:
        tumblr_keys = ['blogname', 'consumer_key', 'consumer_secret']
        missing_keys = []
        for key in tumblr_keys:
          if not source_cfg['tumblr'][key]:
            missing_keys.append(key)

        if len(missing_keys) > 0:
          self.log.error(f'The following keys for Tumblr in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}.')

          if source_cfg['tumblr']['enabled']:
            self.log.info(f'Tumblr in source "{source}" ("{source_cfg["name"]}") has now been disabled for you.')
            source_cfg['tumblr']['enabled'] = False
            self.save()

          exit_needed = True

        if not exit_needed and (not source_cfg['tumblr']['oauth_token'] or not source_cfg['tumblr']['oauth_token_secret']):
          self.init_tumblr_oauth(source_cfg)

      # bluesky
      if source_cfg['bluesky']['enabled']:
        bluesky_keys = ['username', 'app_password']
        missing_keys = []
        for key in bluesky_keys:
          if not source_cfg['bluesky'][key]:
            missing_keys.append(key)

        if len(missing_keys) > 0:
          self.log.error(f'The following keys for Bluesky in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}.')

          if source_cfg['bluesky']['enabled']:
            self.log.info(f'Bluesky in source "{source}" ("{source_cfg["name"]}") has now been disabled for you.')
            source_cfg['bluesky']['enabled'] = False
            self.save()

          exit_needed = True

      # discord webhook
      for platform, webhook_url in source_cfg['discord_webhooks'].items():
        if webhook_url and not webhook_url.startswith("https://discord.com/api/webhooks/"):
          self.log.error(f'Discord webhook URL for {platform} in source "{source}" ("{source_cfg["name"]}") doesn\'t appear to be valid.')

    if not has_found_enabled_source:
      self.log.error('No enabled sources found. Please enable at least one source.')
      exit_needed = True

    if exit_needed and should_exit:
      os._exit(1)

  def init_tumblr_oauth(self, source_cfg: AnimalConfig) -> None:
    tumblr_log = Logger("Tumblr")
    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'

    # obtain request token
    oauth_session = OAuth1Session(source_cfg['tumblr']['consumer_key'], client_secret=source_cfg['tumblr']['consumer_secret'])
    fetch_response = oauth_session.fetch_request_token(request_token_url)

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # redirect to authentication page
    full_authorize_url = oauth_session.authorization_url(authorize_url)
    tumblr_log.info(f'Oauth tokens are missing for source "{source_cfg["name"]}".')
    tumblr_log.info(f'Please visit this URL and authorize (make sure you are signed into blog "{source_cfg["tumblr"]["blogname"]}"): {full_authorize_url}')
    redirect_response = tumblr_log.input('Paste the full redirect URL here: ').strip()

    # retrieve verifier
    oauth_response = oauth_session.parse_authorization_response(redirect_response)
    verifier = oauth_response.get('oauth_verifier')

    # request final access token
    oauth_session = OAuth1Session(
      source_cfg['tumblr']['consumer_key'],
      client_secret=source_cfg['tumblr']['consumer_secret'],
      resource_owner_key=resource_owner_key,
      resource_owner_secret=resource_owner_secret,
      verifier=verifier
    )

    oauth_tokens = oauth_session.fetch_access_token(access_token_url)
    source_cfg['tumblr']['oauth_token'] = oauth_tokens.get('oauth_token', '')
    source_cfg['tumblr']['oauth_token_secret'] = oauth_tokens.get('oauth_token_secret', '')
    self.save()

    tumblr_log.success('Tumblr oauth token and secret have been set.')

  def __str__(self) -> str:
    return json.dumps(self.cfg, indent=2, ensure_ascii=False)

cfg = Config("config.json")
