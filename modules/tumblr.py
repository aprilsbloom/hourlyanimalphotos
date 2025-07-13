import traceback
import time

import pytumblr
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import cfg, TumblrConfig
from utils.image import SourceImage
from utils.logger import Logger
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP

log = Logger("Tumblr")

@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
def tumblr(tumblr_cfg: TumblrConfig, img: SourceImage):
	log.info('Posting to Tumblr')

	try:
		blogname = tumblr_cfg['blogname']

		tumblr = pytumblr.TumblrRestClient(
			consumer_key = tumblr_cfg['consumer_key'],
			consumer_secret = tumblr_cfg['consumer_secret'],
			oauth_token = tumblr_cfg['oauth_token'],
			oauth_secret = tumblr_cfg['oauth_token_secret']
		)
	except Exception:
		log.error('An error occurred while authenticating:', traceback.format_exc())
		log.info('Retrying')
		return

	try:
		response = tumblr.create_photo(
			blogname = blogname,
			state = "published",
			tags = tumblr_cfg['tags'],
			data = img.path
		)

		# check if error
		if response.get('meta', {}).get('status'):
			status = response.get("meta", {}).get("status", "Unknown")
			status_msg = response.get("meta", {}).get("msg", "Unknown")
			error = response.get('response', 'Unknown')
			if error == 'You cannot post to this blog':
				log.error('You have either set the incorrect blogname value, or you have authorized the app to the wrong account. Tumblr has now been disabled, so please re-check config.json and try again.')
				tumblr_cfg['enabled'] = False
				cfg.save()
				return True

			log.error(f'An error occurred while posting the image (status: {status}, {status_msg}): {error}')
			return

		print(response)
		log.success(f'Posted image to Tumblr! Link: https://{blogname}.tumblr.com/post/{response["id"]}')
		return True
	except Exception:
		log.error('An error occurred while posting the image:', traceback.format_exc())
		log.info('Retrying')
		return