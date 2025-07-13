from __future__ import annotations

import json
import time
from typing import List, Optional

import requests

class DiscordWebhook:
  content: str = ""
  embeds: Optional[List[DiscordEmbed]] = None
  files: Optional[List[DiscordFile]] = None

  def __init__(self, url: str, rate_limit_retry: bool = True):
    self.url = url
    self.rate_limit_retry = rate_limit_retry

  def add_embed(self, embed: DiscordEmbed):
    if not self.embeds:
      self.embeds = []

    self.embeds.append(embed)

  def add_file(self, file: DiscordFile):
    if not self.files:
      self.files = []

    self.files.append(file)

  def execute(self):
    request = {}

    if self.content:
      request['content'] = self.content

    if self.embeds:
      request['embeds'] = [embed.to_dict() for embed in self.embeds]

    if self.files:
      request['attachments'] = []

      file_count = 0
      for file in self.files:
        request['attachments'].append({
          'id': file_count,
          'filename': file.filename,
        })

    # if request['attachments'], we need to send multipart form data request
    # the json is in the param 'payload_json'
    # the files are in the param name 'file[id]'
    # each file has a filename attribute

    if request['attachments']:
      payload_json = json.dumps(request)
      form_data = {'payload_json': payload_json}
      file_data = {}

      if self.files:
        for id, file in enumerate(self.files):
          file_data[f'files[{id}]'] = (file.filename, file.file)

      max_retries = 5
      retries = 0

      while retries < max_retries:
        response = requests.post(
          self.url,
          data=form_data,
          files=file_data
        )

        if response.status_code == 429 and self.rate_limit_retry:
          retry_after = response.json().get('retry_after', 5)
          time.sleep(retry_after)
          retries += 1
          continue

        return response
    else:
      response = requests.post(
        self.url,
        json=request
      )
      return response

class DiscordEmbed:
  def __init__(self, title: str, description: str, color: int):
    self.title = title
    self.description = description
    self.color = color

  def to_dict(self):
    return {
      'title': self.title,
      'description': self.description,
      'color': self.color
    }

class DiscordFile:
  def __init__(self, file: bytes, filename: str):
    self.file = file
    self.filename = filename

def send_message(
  url: str,
  content: str = "",
  *,
  embed: Optional[DiscordEmbed] = None,
  embeds: Optional[List[DiscordEmbed]] = None,
  file: Optional[DiscordFile] = None,
  files: Optional[List[DiscordFile]] = None
):
  if not url:
    return None

  webhook = DiscordWebhook(url=url, rate_limit_retry=True)

  if content:
    webhook.content = content

  # embeds
  if embed:
    webhook.add_embed(embed)

  if embeds:
    for embed in embeds:
      webhook.add_embed(embed)

  # files
  if file:
    webhook.add_file(file=file)

  if files:
    for file in files:
      webhook.add_file(file=file)

  response = webhook.execute()
  return response