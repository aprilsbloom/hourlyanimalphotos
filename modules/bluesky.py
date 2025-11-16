import traceback

from atproto import Client
from atproto_core.exceptions import AtProtocolError
from discord import Embed

from utils.config import AnimalConfig
from utils.image import SourceImage
from utils.logger import Logger
from utils.webhook import send_to_webhook

log = Logger("Bluesky")

async def bluesky(source_cfg: AnimalConfig, img: SourceImage, img_url: str) -> str | None:
    # skip if not enabled
    if not source_cfg['bluesky']['enabled']:
        log.info('Bluesky not enabled, skipping')
        return None

    log.info('Posting to Bluesky')

    try:
        bs = Client()
        bs.login(
            login = source_cfg['bluesky']['username'],
            password = source_cfg['bluesky']['app_password']
        )
    except AtProtocolError as e:
        log.error('Failed to authenticate - Bluesky API returned an error.', traceback.format_exc())
        embed = Embed(
            title='Error',
            description='Failed to authenticate - Bluesky API returned an error.',
            color=0xFF0000
        )
        await send_to_webhook(
            url=source_cfg['webhooks']['bluesky'],
            content='@everyone',
            embed=embed,
            exception=e
        )

        return None
    except Exception as e:
        log.error('Failed to authenticate:', traceback.format_exc())
        embed = Embed(
            title='Error',
            description='Failed to authenticate.',
            color=0xFF0000
        )
        await send_to_webhook(
            url=source_cfg['webhooks']['bluesky'],
            content='@everyone',
            embed=embed,
            exception=e
        )

        return None

    log.info('Posting image')
    try:
        post_res = bs.send_image(
            text = "",
            image = img.read(),
            image_alt = ""
        )

        post_id = post_res.uri.split('app.bsky.feed.')[1]
        link = f'https://bsky.app/profile/{source_cfg["bluesky"]["username"]}/{post_id}'
        log.success(f'Posted image to Bluesky! Link: {link}')

        embed = Embed(
            title='Success',
            description='Successfully posted.',
            color=0x00FF00
        )
        embed.add_field(name='URL', value=link)
        embed.set_image(url=img_url)
        await send_to_webhook(
            url=source_cfg['webhooks']['bluesky'],
            embed=embed,
        )

        return link
    except AtProtocolError as e:
        log.error('Failed to post - API returned an error.', traceback.format_exc())
        embed = Embed(
            title='Error',
            description='Failed to post - API returned an error.',
            color=0xFF0000
        )
        await send_to_webhook(
            url=source_cfg['webhooks']['bluesky'],
            content='@everyone',
            embed=embed,
            exception=e
        )

        return None
    except Exception as e:
        log.error('Failed to post:', traceback.format_exc())
        embed = Embed(
            title='Error',
            description='Failed to post.',
            color=0xFF0000
        )
        await send_to_webhook(
            url=source_cfg['webhooks']['bluesky'],
            content='@everyone',
            embed=embed,
            exception=e
        )

        return None