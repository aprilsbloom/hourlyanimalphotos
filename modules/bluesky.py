import traceback
import time

from atproto import Client
from discord_webhook import DiscordEmbed
from tenacity import retry, retry_if_result, stop_after_attempt

from utils.config import AnimalConfig
from utils.discord import DiscordFile, send_message
from utils.image import SourceImage
from utils.logger import Logger
from utils.constants import MAX_POST_RETRY, POST_RETRY_SLEEP

log = Logger("Bluesky")

@retry(stop=stop_after_attempt(MAX_POST_RETRY), retry = retry_if_result(lambda result: not result), sleep=lambda _: time.sleep(POST_RETRY_SLEEP))
def bluesky(source_cfg: AnimalConfig, img: SourceImage):
	log.info('Posting to Bluesky')

	try:
		bs = Client()
		bs.login(
			login = source_cfg['bluesky']['username'],
			password = source_cfg['bluesky']['app_password']
		)
	except Exception:
		log.error('An error occurred while authenticating:', traceback.format_exc())
		send_message(
			url=source_cfg['webhooks']['bluesky'],
			file=DiscordFile(bytes(traceback.format_exc(), 'utf-8'), 'traceback.txt'),
			embed=DiscordEmbed(
				title='Error',
				description='Failed to authenticate to Bluesky.',
				color=0xFF0000
			)
		)

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
		log.success(f'Posted image to Bluesky! Link: https://bsky.app/profile/{source_cfg["bluesky"]["username"]}/{url}')
		return True
	except Exception:
		log.error('An error occurred while posting the image:', traceback.format_exc())
		send_message(
			url=source_cfg['webhooks']['bluesky'],
			file=DiscordFile(bytes(traceback.format_exc(), 'utf-8'), 'traceback.txt'),
			embed=DiscordEmbed(
				title='Error',
				description='Failed to post to Bluesky.',
				color=0xFF0000
			)
		)

		log.info('Retrying')
		return False