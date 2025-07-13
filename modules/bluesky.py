import traceback
import time

from atproto import Client
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import BlueskyConfig
from utils.image import SourceImage
from utils.logger import Logger
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP

log = Logger("Bluesky")

@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
def bluesky(cfg: BlueskyConfig, img: SourceImage):
	log.info('Posting to Bluesky')

	try:
		bs = Client()
		bs.login(
			login = cfg['username'],
			password = cfg['app_password']
		)
	except Exception:
		log.error('An error occurred while authenticating:', traceback.format_exc())
		log.info('Retrying')
		return False

	log.info('Posting image')
	try:
		res = bs.send_image(
			text = "",
			image = img.read(),
			image_alt = ""
		)

		url = res.uri.split('app.bsky.feed.')[1]
		log.success(f'Posted image to Bluesky! Link: https://bsky.app/profile/{cfg["username"]}/{url}')
		return True
	except Exception:
		log.error('An error occurred while posting the image:', traceback.format_exc())
		log.info('Retrying')
		return False