import time
import traceback

import pytumblr
from discord import Embed
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig, cfg
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP
from utils.image import SourceImage
from utils.logger import Logger
from utils.webhook import send_to_webhook

log = Logger("Tumblr")

@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
async def tumblr(source_cfg: AnimalConfig, img: SourceImage):
	# skip if not enabled
	if not source_cfg['tumblr']['enabled']:
		log.info('Tumblr not enabled, skipping')
		return True

	log.info('Posting to Tumblr')

	webhook_url = source_cfg['webhooks'].get('tumblr') if source_cfg.get('webhooks') else None

	try:
		blogname = source_cfg['tumblr']['blogname']

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
				color=0xFF0000
			)
			await send_to_webhook(
				url=webhook_url,
				content='@everyone',
				embed=embed,
				exception=e
			)
		log.info('Retrying')
		return

	try:
		response = tumblr.create_photo(
			blogname = blogname,
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
						color=0xFF0000
					)
					await send_to_webhook(
						url=webhook_url,
						content='@everyone',
						embed=embed,
						response=response
					)
				return True

			log.error(f'An error occurred while posting the image (status: {status}, {status_msg}): {error}')
			if webhook_url:
				embed = Embed(
					title='Error',
					description='Failed to post - Tumblr returned an error.',
					color=0xFF0000
				)
				await send_to_webhook(
					url=webhook_url,
					content='@everyone',
					embed=embed,
					response=response
				)

			return
	except Exception as e:
		log.error('An error occurred while posting the image:', traceback.format_exc())

		if webhook_url:
			embed = Embed(
				title='Error',
				description='Failed to post.',
				color=0xFF0000
			)
			await send_to_webhook(
				url=webhook_url,
				content='@everyone',
				embed=embed,
				exception=e
			)

		log.info('Retrying')
		return

	post_url = f'https://{blogname}.tumblr.com/post/{response["id"]}'
	log.success(f'Posted image to Tumblr! Link: {post_url}')
	if webhook_url:
		embed = Embed(
			title='Success',
			description='Successfully posted.',
			color=0x00FF00
		)
		embed.add_field(name='URL', value=post_url, inline=False)
		await send_to_webhook(
			url=webhook_url,
			embed=embed
		)

	return True