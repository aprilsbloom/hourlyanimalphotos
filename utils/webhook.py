import io
import json
import traceback
from typing import List

import aiohttp
import discord
import requests


async def send_to_webhook(
  url: str,
  content: str = '',
  embed: discord.Embed | None = None,
  embeds: List[discord.Embed] = [],
  file: discord.File | None = None,
  files: List[discord.File] = [],
  response: requests.Response | dict | None = None,
  exception: Exception | str | None = None
):
  if not url:
    return

  async with aiohttp.ClientSession() as sess:
    webhook = discord.Webhook.from_url(
      url=url,
      session=sess
    )

    if len(embeds) == 0 and embed is not None:
      embeds = [embed]

    if len(files) == 0 and file is not None:
      files = [file]

    # add the response to the file array
    if response:
      filename = 'response.txt'
      content = response.text

      if isinstance(response, dict) or hasattr(response, '__dict__'):
        data = response if isinstance(response, dict) else response.__dict__

        filename = 'response.json'
        content = json.dumps(data, indent=2)

        files.append(discord.File(
          fp=io.BytesIO(content.encode('utf-8')),
          filename=filename
        ))
      elif isinstance(response, requests.Response):
        # we only want to include the response if it's text-based
        content_type = response.headers.get('content-type')

        if 'text' in content_type or 'json' in content_type:
          # adjust filename if json obj
          if 'json' in content_type:
            filename = 'response.json'
            content_obj = response.json()
            content = json.dumps(content_obj, indent=2)

          files.append(discord.File(
            fp=io.BytesIO(content.encode('utf-8')),
            filename=filename
          ))


    # add the exception to the file array
    if exception:
      if isinstance(exception, Exception):
        tb_str = traceback.format_exception(exception)
        exc_str = '\n'.join(tb_str)
      else:
        exc_str = str(exception)

      files.append(discord.File(
        fp=io.BytesIO(
          exc_str.encode('utf-8')
        ),
        filename='error.txt'
      ))

    try:
      await webhook.send(
        content,
        embeds=embeds,
        files=files
      )
    except Exception as e:
      print(f'Failed to send webhook message to URL "{url}"', e)
      traceback.print_exc()
