import traceback

from atproto import Client
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.globals import log
from utils.config import AnimalConfig
from utils.image import SourceImage


@retry(stop=stop_after_attempt(3), retry = retry_if_result(lambda result: not result))
def bluesky(cfg: AnimalConfig, img: SourceImage):
	try:
		bs = Client()
		bs.login(
			login = cfg['bluesky']['username'],
			password = cfg['bluesky']['app_password']
		)
	except Exception:
		log.error('Failed to create Bluesky client.')
		return False

	log.info('Sending image to Bluesky')
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
		log.error(f'Failed to send image to Bluesky: {traceback.format_exc()}')
		return False