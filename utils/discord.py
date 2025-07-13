from typing import List, Optional

from discord_webhook import DiscordWebhook, DiscordEmbed

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

  if file:
    webhook.add_file(file=file.file, filename=file.filename)

  if files:
    for file in files:
      webhook.add_file(file=file.file, filename=file.filename)

  if embed:
    webhook.add_embed(embed)

  if embeds:
    for embed in embeds:
      webhook.add_embed(embed)

  response = webhook.execute()
  return response

