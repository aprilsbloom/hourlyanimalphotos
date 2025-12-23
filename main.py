import asyncio
import shutil
from datetime import datetime, timedelta
from typing import List, cast

from discord import Embed
import filetype

from modules import bluesky, tumblr, twitter
from sources import CatAPI, DogAPI, ImageSource
from utils.config import cfg
from utils.constants import IMG_EXTENSIONS, MAX_IMG_FETCH_RETRY, MAX_IMG_SIZE_MB
from utils.image import SourceImage
from utils.logger import Logger
from utils.webhook import send_to_webhook

log = Logger("Main")

async def post():
    post_log = Logger("Post")

    img_data = None
    img_url = None
    sources: List[ImageSource] = [
        CatAPI(cfg),
        DogAPI(cfg),
    ]

    for source in sources:
        source_cfg = cfg.cfg[source.cfg_key]

        # ensure at least one site is enabled otherwise we're wasting our time
        if not source_cfg['enabled']:
            post_log.info(f'Skipping disabled source "{source.cfg_key}" ("{source.name}").')
            continue

        if (
            not source_cfg['twitter']['enabled'] and
            not source_cfg['tumblr']['enabled'] and
            not source_cfg['bluesky']['enabled']
        ):
            post_log.error(f'No sites are enabled for the source "{source.cfg_key}" ("{source.name}"). Please enable at least one site in config.json.')
            continue

        # fetch & validate img
        img_fetch_retry = 0
        while img_fetch_retry < MAX_IMG_FETCH_RETRY:
            img_data, img_url = source.fetch_img()

            # if no img data, retry
            if not img_data or len(img_data) == 0:
                img_fetch_retry += 1
                post_log.error(f'Failed to fetch image from "{source.cfg_key}" ("{source.name}"). Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
                continue

            # if img data is invalid, retry
            img_type = filetype.guess(img_data)
            if img_type is None or img_type.extension not in IMG_EXTENSIONS:
                img_fetch_retry += 1
                post_log.error(f'Source "{source.cfg_key}" ("{source.name}") returned an invalid image. Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
                continue

            break


        if img_fetch_retry == MAX_IMG_FETCH_RETRY:
            post_log.error(f'Failed to fetch image from "{source.cfg_key}" ("{source.name}"). Reached retry limit ({MAX_IMG_FETCH_RETRY}).')
            embed = Embed(
                title='Error',
                description=f'Failed to fetch image from "{source.cfg_key}" ("{source.name}"). Reached retry limit ({MAX_IMG_FETCH_RETRY}).',
            )
            await send_to_webhook(
                url=source_cfg["webhooks"]["misc"],
                content='@everyone',
                embed=embed
            )
            continue

        # resize the image to be below 1 mb if applicable
        if img_data is None:
            post_log.error('Failed to fetch image data: img_data is None after fetching')
            embed = Embed(
                title='Error',
                description=f'Failed to fetch image data: `img_data` is `None` after fetching.',
            )
            await send_to_webhook(
                url=source_cfg["webhooks"]["misc"],
                content='@everyone',
                embed=embed
            )
            continue


        img = SourceImage(cast(bytes, img_data))
        if img.get_size_mb() > MAX_IMG_SIZE_MB:
            while img.get_size_mb() > MAX_IMG_SIZE_MB:
                dimensions = img.get_dimensions()
                width = int(dimensions[0] * 0.9)
                height = int(dimensions[1] * 0.9)
                img.resize(width, height, 90)

        # if everything is successful, post the image to all the platforms
        twitter_url = await twitter(source_cfg, img, img_url)
        tumblr_url = await tumblr(source_cfg, img, img_url)
        bluesky_url = await bluesky(source_cfg, img, img_url)

        webhook_url = source_cfg['webhooks']['post_notification']
        if webhook_url and (twitter_url or tumblr_url or bluesky_url):
          embed = Embed(title='Photo')

          # add post urls
          post_urls = ''
          if twitter_url is not None:
            post_urls += f'- [Twitter]({twitter_url})\n'

          if tumblr_url is not None:
            post_urls += f'- [Tumblr]({tumblr_url})\n'

          if bluesky_url is not None:
            post_urls += f'- [Bluesky]({bluesky_url})\n'

          if post_urls:
            embed.add_field(name='URLs', value=post_urls, inline=False)

          embed.set_image(url=img_url)
          await send_to_webhook(
            url=webhook_url,
            embed=embed
          )

        img.cleanup()

    print()


async def main():
    shutil.rmtree('jobs', ignore_errors=True)
    cfg.validate(should_exit=True)

    while True:
    # run loop 15s early to account for img fetching
        current_time = datetime.now()
        goal_timestamp = current_time + timedelta(hours = 1, minutes = -current_time.minute, seconds = -current_time.second, microseconds=-current_time.microsecond)

        log.info(f'Posting at: {goal_timestamp.strftime("%H:%M:%S")}')
        await asyncio.sleep((goal_timestamp - current_time).total_seconds())

        await post()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Exiting...')
        exit()
