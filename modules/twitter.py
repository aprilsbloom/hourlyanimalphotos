import time
import traceback

import tweepy
from tweepy import errors
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import TwitterConfig
from utils.image import SourceImage
from utils.logger import Logger
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP

log = Logger("Twitter")

# current API ratelimit says max of 17 every 24hrs

@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
def twitter(cfg: TwitterConfig, img: SourceImage):
	log.info('Posting to Twitter')

	try:
		consumer_key = cfg['consumer_key']
		consumer_secret = cfg['consumer_secret']
		access_token = cfg['access_token']
		access_token_secret = cfg['access_token_secret']

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
		log.success(f'Posted image to Twitter! Link: https://x.com/i/status/{response.data["id"]}') # type: ignore
		return True
	else:
		log.error('An error occurred while posting the image (response):', response.errors) # type: ignore
		return