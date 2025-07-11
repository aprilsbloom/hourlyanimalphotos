import asyncio
import os
from datetime import datetime, timedelta
from typing import List

import filetype
import requests
from PIL import Image

from modules import bluesky, tumblr, twitter
from sources import CatAPI, DogAPI, ImageSource
from utils.globals import IMG_EXTENSIONS, MAX_IMG_FETCH_RETRY, cfg, log

async def post():
	sources: List[ImageSource] = [
		CatAPI(cfg),
		DogAPI(cfg),
	]

	for source in sources:
		# ensure at least one site is enabled otherwise we're wasting our time
		if (
			not cfg.cfg[source.cfg_key]['twitter']['enabled'] and
			not cfg.cfg[source.cfg_key]['tumblr']['enabled'] and
			not cfg.cfg[source.cfg_key]['bluesky']['enabled']
		):
			log.error('No sites are enabled. Please enable at least one site in config.json.')
			continue

		# fetch & validate img
		img_fetch_retry = 0
		while img_fetch_retry < MAX_IMG_FETCH_RETRY:
			img = source.fetch_img()
			if not img or len(img) == 0:
				img_fetch_retry += 1
				log.error(f'Failed to fetch image from "{source.name}". Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

			img_type = filetype.guess(img)
			if img_type is None or img_type.extension not in IMG_EXTENSIONS:
				img_fetch_retry += 1
				log.error(f'Source "{source.name}" returned an invalid image. Retrying ({img_fetch_retry}/{MAX_IMG_FETCH_RETRY})')
				continue

		if img_fetch_retry == MAX_IMG_FETCH_RETRY:
			log.error(f'Failed to fetch image from "{source.name}". Reached retry limit ({MAX_IMG_FETCH_RETRY}).')
			continue

	try:
		with open(IMG_PATH, 'wb') as f:
			f.write(res.content)

		log.info('Fetched image successfully. Compressing image to be under 1MB.')

		# resave image as webp to compress it
		img = Image.open(IMG_PATH)
		img.save(IMG_PATH, 'webp', quality=100)

		while True:
			with open(IMG_PATH, 'rb') as f:
				img_bytes = f.read()

			mib = len(img_bytes) / 1000 / 1000
			if mib < 1:
				break

			img = Image.open(IMG_PATH)
			width = int(img.width * 0.9)
			height = int(img.height * 0.9)
			img.resize((width, height), Image.Resampling.LANCZOS)
			img.save(IMG_PATH, 'webp', quality=75)
	except Exception:
		log.error('Failed to write the fetched image.')
		return

	# check if the image is actually supported
	img_type = filetype.guess(IMG_PATH)
	if img_type is None or img_type.extension not in IMG_EXTENSIONS:
		log.error('TheCatAPI returned an invalid image.')
		return False

	# if everything is successful, post the image to all the platforms
	if cfg.cfg['cat']['twitter']['enabled']:
		try:
			twitter()
		except Exception:
			log.error('Failed to post to Twitter.')

	if cfg.cfg['cat']['tumblr']['enabled']:
		try:
			tumblr()
		except Exception:
			log.error('Failed to post to Tumblr.')

	if cfg.cfg['cat']['bluesky']['enabled']:
		try:
			bluesky()
		except Exception:
			log.error('Failed to post to Bluesky.')

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
