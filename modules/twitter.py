import time
import traceback

import tweepy
from tweepy import errors
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig
from utils.image import SourceImage
from utils.logger import Logger

log = Logger("Twitter")


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(5))
def twitter(cfg: AnimalConfig, img: SourceImage):
	log.info('Posting to Twitter')

	try:
		consumer_key = cfg['twitter']['consumer_key']
		consumer_secret = cfg['twitter']['consumer_secret']
		access_token = cfg['twitter']['access_token']
		access_token_secret = cfg['twitter']['access_token_secret']

		auth = tweepy.OAuth1UserHandler(
			consumer_key = consumer_key,
			consumer_secret = consumer_secret,
			access_token = access_token,
			access_token_secret = access_token_secret
		)

		v1 = tweepy.API(auth, wait_on_rate_limit=True)
		v2 = tweepy.Client(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token=access_token,
			access_token_secret=access_token_secret
		)
	except Exception:
		log.error('An error occurred while authenticating:', traceback.format_exc())
		log.info('Retrying')
		return

	# upload image
	log.info('Uploading image')
	try:
		img = v1.chunked_upload(filename=str(img.path), media_category="tweet_image").media_id_string
	except Exception:
		log.error('An error occured while uploading the image:', traceback.format_exc())
		log.info('Retrying')
		return

	log.success('Uploaded image!')

	# post image
	log.info('Posting image')
	try:
		response = v2.create_tweet(text = "", media_ids = [ img ])
	except errors.TooManyRequests:
		log.error('Rate limit exceeded! Skipping post')
		return True
	except Exception:
		log.error('An error occured while posting the image (exception):', traceback.format_exc())
		log.info('Retrying')
		return

	# check response
	if response.data and response.errors == []: # type: ignore
		log.success(f'Posted image! Link: https://x.com/i/status/{response.data["id"]}') # type: ignore
		return True
	else:
		log.error('An error occurred while posting the image (response):', response.errors) # type: ignore
		return