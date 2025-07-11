import traceback

import tweepy
from tweepy import errors
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig
from utils.globals import log
from utils.image import SourceImage


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result))
def twitter(cfg: AnimalConfig, img: SourceImage):
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
		log.error(f'Error while authenticating to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Uploading image to Twitter')

	try:
		img = v1.chunked_upload(filename=img.path, media_category="tweet_image").media_id_string
	except Exception:
		log.error(f'An error occured while uploading the image to Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	log.info('Posting image to Twitter')
	try:
		response = v2.create_tweet(text = "", media_ids = [ img ])
	except errors.TooManyRequests:
		log.error('Rate limit exceeded! Skipping...')
		return True
	except Exception:
		log.error(f'An error occured while posting the image on Twitter: {traceback.format_exc()}')
		log.info('Trying again...\n')
		return

	if response.data and response.errors == []: # type: ignore
		log.success(f'Tweeted image! Link: https://twitter.com/i/status/{response.data["id"]}') # type: ignore
		return True
	else:
		log.error('Error while posting the image!')
		log.error(f'Error: {response.errors}\n') # type: ignore
		return