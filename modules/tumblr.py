import traceback

import pytumblr
from discord import Embed

from utils.config import AnimalConfig, cfg
from utils.image import SourceImage
from utils.logger import Logger
from utils.webhook import send_to_webhook

log = Logger("Tumblr")

async def tumblr(source_cfg: AnimalConfig, img: SourceImage, img_url: str) -> str | None:
    webhook_url = source_cfg['webhooks']['tumblr']
    blog_name = source_cfg['tumblr']['blogname']

    # skip if not enabled
    if not source_cfg['tumblr']['enabled']:
        log.info('Tumblr not enabled, skipping')
        return None

    log.info('Posting to Tumblr')

    try:
        tumblr = pytumblr.TumblrRestClient(
            consumer_key = source_cfg['tumblr']['consumer_key'],
            consumer_secret = source_cfg['tumblr']['consumer_secret'],
            oauth_token = source_cfg['tumblr']['oauth_token'],
            oauth_secret = source_cfg['tumblr']['oauth_token_secret']
        )
    except Exception as e:
        log.error('An error occurred while authenticating:', traceback.format_exc())
        if webhook_url:
            embed = Embed(
                title='Error',
                description='Failed to authenticate to Tumblr.',
            )
            await send_to_webhook(
                url=webhook_url,
                content='@everyone',
                embed=embed,
                exception=e
            )
        return None

    try:
        response = tumblr.create_photo(
            blogname = blog_name,
            state = "published",
            tags = source_cfg['tumblr']['tags'],
            data = img.path
        )

        # check if error
        if response.get('meta', {}).get('status'):
            status = response.get("meta", {}).get("status", "Unknown")
            status_msg = response.get("meta", {}).get("msg", "Unknown")
            error = response.get('response', 'Unknown')
            if error == 'You cannot post to this blog':
                log.error('You have either set the incorrect blogname value, or you have authorized the app to the wrong account. Tumblr has now been disabled, so please re-check config.json and try again.')
                source_cfg['tumblr']['enabled'] = False
                cfg.save()

                if webhook_url:
                    embed = Embed(
                        title='Error',
                        description='Failed to post - the configured blog name is incorrect.',
                    )
                    await send_to_webhook(
                        url=webhook_url,
                        content='@everyone',
                        embed=embed,
                        response=response
                    )
                return None

            log.error(f'An error occurred while posting the image (status: {status}, {status_msg}): {error}')
            if webhook_url:
                embed = Embed(
                    title='Error',
                    description='Failed to post - Tumblr returned an error.',
                )
                await send_to_webhook(
                    url=webhook_url,
                    content='@everyone',
                    embed=embed,
                    response=response
                )

            return None
    except Exception as e:
        log.error('An error occurred while posting the image:', traceback.format_exc())

        if webhook_url:
            embed = Embed(
                title='Error',
                description='Failed to post.',
            )
            await send_to_webhook(
                url=webhook_url,
                content='@everyone',
                embed=embed,
                exception=e
            )

        return None

    post_url = f'https://{blog_name}.tumblr.com/post/{response["id"]}'
    log.success(f'Posted image to Tumblr! Link: {post_url}')
    if webhook_url:
        embed = Embed(
            title='Success',
            description='Successfully posted.',
        )
        embed.add_field(name='URL', value=post_url, inline=False)
        embed.set_image(url=img_url)
        await send_to_webhook(
            url=webhook_url,
            embed=embed
        )

    return post_url