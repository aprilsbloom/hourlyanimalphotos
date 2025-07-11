import traceback

import pytumblr
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig
from utils.globals import CAT_TAGS
from utils.image import SourceImage
from utils.logger import Logger

log = Logger("Tumblr")


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result))
def tumblr(cfg: AnimalConfig, img: SourceImage):
	log.info('Posting to Tumblr')

	try:
		blogname = cfg['tumblr']['blogname']
		tumblr = pytumblr.TumblrRestClient(
			consumer_key = cfg['tumblr']['consumer_key'],
			consumer_secret = cfg['tumblr']['consumer_secret'],
			oauth_token = cfg['tumblr']['oauth_token'],
			oauth_secret = cfg['tumblr']['oauth_token_secret']
		)
	except Exception:
		log.error('An error occurred while authenticating:')
		log.error(traceback.format_exc())
		log.info('Retrying')
		return

	log.info('Posting image')

	try:
		response = tumblr.create_photo(
			blogname = blogname,
			state = "published",
			tags = CAT_TAGS,
			data = img.read()
		)

		log.success(f'Posted image to Tumblr! Link: https://{blogname}.tumblr.com/post/{response["id"]}')
		return True
	except Exception:
		log.error('An error occurred while posting the image:')
		log.error(traceback.format_exc())
		log.info('Retrying')
		return