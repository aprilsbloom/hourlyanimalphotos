import time
import traceback
from datetime import datetime

import tweepy
from discord import Embed
from tenacity import retry, retry_if_result, stop_after_attempt
from tweepy import errors

from utils.config import AnimalConfig
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP
from utils.image import SourceImage
from utils.logger import Logger
from utils.webhook import send_to_webhook

log = Logger("Twitter")

# current API ratelimit says max of 17 every 24hrs
@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
async def twitter(source_cfg: AnimalConfig, img: SourceImage):
	# skip if not enabled
	if not source_cfg['twitter']['enabled']:
		log.info('Twitter not enabled, skipping')
		return True

	webhook_url = source_cfg['webhooks']['twitter']

	# only post on even hours (0, 2, 4, ...)
	current_hour = datetime.now().hour
	if current_hour % 2 != 0:
		log.info('Skipping Twitter post for this hour - posting in even hours only due to rate limits.')
		return True

	log.info('Posting to Twitter')

	try:
		consumer_key = source_cfg['twitter']['consumer_key']
		consumer_secret = source_cfg['twitter']['consumer_secret']
		access_token = source_cfg['twitter']['access_token']
		access_token_secret = source_cfg['twitter']['access_token_secret']

		auth = tweepy.OAuth1UserHandler(
			consumer_key = consumer_key,
			consumer_secret = consumer_secret,
			access_token = access_token,
			access_token_secret = access_token_secret
		)

		v1 = tweepy.API(auth)
		v2 = tweepy.Client(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token=access_token,
			access_token_secret=access_token_secret
		)
	except Exception as e:
		log.error('An error occurred while authenticating:', traceback.format_exc())

		embed = Embed(
			title='Error',
			description='Failed to authenticate.',
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

	# upload image
	log.info('Uploading image')
	upload_res = None
	media_id = None
	try:
		upload_res = v1.chunked_upload(
			filename=str(img.path),
			media_category="tweet_image"
		)
		media_id = upload_res.media_id_string
	except Exception as e:
		log.error('An error occured while uploading the image:', traceback.format_exc())

		embed = Embed(
			title='Error',
			description='Failed to upload image to Twitter.',
			color=0xFF0000
		)
		await send_to_webhook(
			url=webhook_url,
			content='@everyone',
			embed=embed,
			exception=e,
			response=upload_res
		)

		log.info('Retrying')
		return

	log.success('Uploaded image!')

	# post image
	log.info('Posting image')
	post_res = None
	try:
		post_res = v2.create_tweet(text = "", media_ids = [ media_id ])
	except errors.TooManyRequests as e:
		log.error('Rate limit exceeded! Skipping post')

		embed = Embed(
			title='Error',
			description='Failed to post - Rate limit exceeded.',
			color=0xFF0000
		)
		await send_to_webhook(
			url=webhook_url,
			content='@everyone',
			embed=embed,
			exception=e,
			response=post_res
		)

		return True
	except Exception as e:
		log.error('An error occured while posting the image:', traceback.format_exc())

		embed = Embed(
			title='Error',
			description='Failed to post.',
			color=0xFF0000
		)
		await send_to_webhook(
			url=webhook_url,
			content='@everyone',
			embed=embed,
			exception=e,
			response=post_res
		)

		log.info('Retrying')
		return

	# check response
	if post_res and post_res.data and not post_res.errors: # type: ignore
		tweet_url = f'https://x.com/i/status/{post_res.data["id"]}' # type: ignore
		log.success(f'Posted image to Twitter! Link: {tweet_url}')
		embed = Embed(
			title='Success',
			description='Successfully posted.',
			color=0x00FF00
		)
		embed.add_field(name='URL', value=tweet_url)
		await send_to_webhook(
			url=webhook_url,
			embed=embed
		)
		return True
	else:
		response_errors = post_res.errors if post_res else None # type: ignore
		log.error('An error occurred while posting the image:', response_errors)

		embed = Embed(
			title='Error',
			description='Failed to post.',
			color=0xFF0000
		)
		await send_to_webhook(
			url=webhook_url,
			content='@everyone',
			embed=embed,
			response=post_res
		)

		return