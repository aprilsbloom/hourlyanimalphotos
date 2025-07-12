import traceback
import time

from atproto import Client
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig
from utils.image import SourceImage
from utils.logger import Logger

log = Logger("Bluesky")

@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(5))
def bluesky(cfg: AnimalConfig, img: SourceImage):
	log.info('Posting to Bluesky')

	try:
		bs = Client()
		bs.login(
			login = cfg['bluesky']['username'],
			password = cfg['bluesky']['app_password']
		)
	except Exception:
		log.error('An error occurred while authenticating:')
		log.error(traceback.format_exc())
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
		log.success(f'Posted image to Bluesky! Link: https://bsky.app/profile/{cfg["bluesky"]["username"]}/{url}')
		return True
	except Exception:
		log.error('An error occurred while posting the image:')
		log.error(traceback.format_exc())
		log.info('Retrying')
		return False