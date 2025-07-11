import asyncio
import os
from datetime import datetime, timedelta
from typing import List, cast

import filetype
import requests
from PIL import Image

from modules import bluesky, tumblr, twitter
from sources import CatAPI, DogAPI, ImageSource
from utils.image import SourceImage
from utils.globals import IMG_EXTENSIONS, MAX_IMG_FETCH_RETRY, cfg, log

async def post():
	sources: List[ImageSource] = [
		CatAPI(cfg),
		DogAPI(cfg),
	]

	for source in sources:
		source_cfg = cfg.cfg[source.cfg_key]
		# ensure at least one site is enabled otherwise we're wasting our time
		if (
			not source_cfg['twitter']['enabled'] and
			not source_cfg['tumblr']['enabled'] and
			not source_cfg['bluesky']['enabled']
		):
			log.error('No sites are enabled. Please enable at least one site in config.json.')
			continue

		# fetch & validate img
		img_fetch_retry = 0
		while img_fetch_retry < MAX_IMG_FETCH_RETRY:
			img_data = source.fetch_img()
			if not img_data or len(img_data) == 0:
				img_fetch_retry += 1
				log.error(f'Failed to fetch image from "{source.name}". Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

			img_type = filetype.guess(img_data)
			if img_type is None or img_type.extension not in IMG_EXTENSIONS:
				img_fetch_retry += 1
				log.error(f'Source "{source.name}" returned an invalid image. Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

		if img_fetch_retry == MAX_IMG_FETCH_RETRY:
			log.error(f'Failed to fetch image from "{source.name}". Reached retry limit ({MAX_IMG_FETCH_RETRY}).')
			continue

		# resize image to be below 1mb if applicable
		img = SourceImage(cast(bytes, img_data))
		if img.get_size_mb() > 1:
			while img.get_size_mb() > 1:
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

		if source_cfg['tumblr']['enabled']:
			try:
				tumblr(source_cfg, img)
			except Exception:
				log.error('Failed to post to Tumblr.')

		if source_cfg['bluesky']['enabled']:
			try:
				bluesky(source_cfg, img)
			except Exception:
				log.error('Failed to post to Bluesky.')

		img.cleanup()

	print()

async def main():
	while True:
		current_time = datetime.now()
		goal_timestamp = current_time + timedelta(hours = 1, minutes = -current_time.minute, seconds = -current_time.second, microseconds=-current_time.microsecond)
		log.info(f'Posting at: {goal_timestamp.strftime("%H:%M:%S")}')
		await asyncio.sleep((goal_timestamp - current_time).total_seconds())
		await post()

if __name__ == '__main__':
	asyncio.run(main())
