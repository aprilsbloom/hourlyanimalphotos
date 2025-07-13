import asyncio
import traceback
from datetime import datetime, timedelta
from typing import List, cast

import filetype
import shutil

from modules import bluesky, tumblr, twitter
from sources import CatAPI, DogAPI, ImageSource
from utils.config import cfg
from utils.discord import DiscordEmbed, DiscordFile, send_message
from utils.image import SourceImage
from utils.constants import IMG_EXTENSIONS, MAX_IMG_FETCH_RETRY, MAX_IMG_SIZE_MB
from utils.logger import Logger

log = Logger("Main")

async def post():
	log = Logger("Post")
	sources: List[ImageSource] = [
		CatAPI(cfg),
		DogAPI(cfg),
	]

	for source in sources:
		source_cfg = cfg.cfg[source.cfg_key]

		# ensure at least one site is enabled otherwise we're wasting our time
		if not source_cfg['enabled']:
			log.info(f'Skipping disabled source "{source.cfg_key}" ("{source.name}").')
			continue

		if (
			not source_cfg['twitter']['enabled'] and
			not source_cfg['tumblr']['enabled'] and
			not source_cfg['bluesky']['enabled']
		):
			log.error(f'No sites are enabled for the source "{source.cfg_key}" ("{source.name}"). Please enable at least one site in config.json.')
			continue

		# fetch & validate img
		img_fetch_retry = 0
		while img_fetch_retry < MAX_IMG_FETCH_RETRY:
			img_data = source.fetch_img()

			# if no img data, retry
			if not img_data or len(img_data) == 0:
				img_fetch_retry += 1
				log.error(f'Failed to fetch image from "{source.cfg_key}" ("{source.name}"). Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

			# if img data is invalid, retry
			img_type = filetype.guess(img_data)
			if img_type is None or img_type.extension not in IMG_EXTENSIONS:
				img_fetch_retry += 1
				log.error(f'Source "{source.cfg_key}" ("{source.name}") returned an invalid image. Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

			break

		if img_fetch_retry == MAX_IMG_FETCH_RETRY:
			log.error(f'Failed to fetch image from "{source.cfg_key}" ("{source.name}"). Reached retry limit ({MAX_IMG_FETCH_RETRY}).')
			continue

		# resize image to be below 1mb if applicable
		img = SourceImage(cast(bytes, img_data))
		if img.get_size_mb() > MAX_IMG_SIZE_MB:
			while img.get_size_mb() > MAX_IMG_SIZE_MB:
				dimensions = img.get_dimensions()
				width = int(dimensions[0] * 0.9)
				height = int(dimensions[1] * 0.9)
				img.resize(width, height, 90)

		# if everything is successful, post the image to all the platforms
		if source_cfg['twitter']['enabled']:
			try:
				twitter(source_cfg, img)
			except Exception:
				log.error('Failed to post to Twitter.')
				send_message(
					url=source_cfg['webhooks']['twitter'],
					file=DiscordFile(bytes(traceback.format_exc(), 'utf-8'), 'error.txt'),
					embed=DiscordEmbed(
						title='Error',
						description='Failed to post to Twitter.',
						color=0xFF0000
					)
				)

		if source_cfg['tumblr']['enabled']:
			try:
				tumblr(source_cfg, img)
			except Exception:
				log.error('Failed to post to Tumblr.')
				send_message(
					url=source_cfg['webhooks']['tumblr'],
					file=DiscordFile(bytes(traceback.format_exc(), 'utf-8'), 'error.txt'),
					embed=DiscordEmbed(
						title='Error',
						description='Failed to post to Tumblr.',
						color=0xFF0000
					)
				)

		if source_cfg['bluesky']['enabled']:
			try:
				bluesky(source_cfg, img)
			except Exception:
				log.error('Failed to post to Bluesky.')
				send_message(
					url=source_cfg['webhooks']['bluesky'],
					file=DiscordFile(bytes(traceback.format_exc(), 'utf-8'), 'error.txt'),
					embed=DiscordEmbed(
						title='Error',
						description='Failed to post to Bluesky.',
						color=0xFF0000
					)
				)

		img.cleanup()

	print()


async def main():
	shutil.rmtree('jobs', ignore_errors=True)
	cfg.validate(should_exit=True)

	while True:
    # run loop 15s early to account for img fetching
		current_time = datetime.now()
		goal_timestamp = current_time + timedelta(hours = 1, minutes = -current_time.minute, seconds = -current_time.second - 15, microseconds=-current_time.microsecond)

		log.info(f'Posting at: {goal_timestamp.strftime("%H:%M:%S")}')
		await asyncio.sleep((goal_timestamp - current_time).total_seconds())

		await post()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		log.info('Exiting...')
		exit()
