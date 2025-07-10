import asyncio
import os
from datetime import datetime, timedelta

import filetype
import requests
from PIL import Image

from modules import bluesky, mastodon, tumblr, twitter
from utils.globals import IMG_EXTENSIONS, IMG_PATH, cfg, log

retry_count = 0
async def fetch_img():
	global retry_count

	# ensure at least one site is enabled otherwise we're wasting our time
	if (
		not cfg.get('twitter.enabled') and
		not cfg.get('mastodon.enabled') and
		not cfg.get('tumblr.enabled') and
		not cfg.get('bluesky.enabled')
	):
		log.error('No sites are enabled. Please enable at least one site in config.json.')
		return

	log.info('Fetching image from https://thecatapi.com')
	res = requests.get(
		url = 'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png',
		headers = { 'x-api-key': cfg.get('catapi-key') }
	)

	try:
		data = res.json()
	except requests.exceptions.JSONDecodeError:
		log.error('Failed to fetch image.')
		if retry_count == 3:
			log.info('Retrying...')
			retry_count += 1

			await fetch_img()
		else:
			log.error('Reached retry limit, giving up.')

		return

	# catapi sometimes returns things in a list for some reason
	if isinstance(data, list):
		data = data[0]

	# check if the request was successful by checking for the 'url' key
	url = data.get('url')
	if not url:
		log.error('Failed to fetch image.')
		return False

	# if everything is successful, fetch the image and write it to a file
	res = requests.get(url)
	if os.path.exists(IMG_PATH):
		try:
			os.remove(IMG_PATH)
		except Exception:
			log.error(f'Failed to remove {IMG_PATH}.')

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
	if cfg.get('twitter.enabled'):
		try:
			twitter()
		except Exception:
			log.error('Failed to post to Twitter.')

	if cfg.get('tumblr.enabled'):
		try:
			tumblr()
		except Exception:
			log.error('Failed to post to Tumblr.')

	if cfg.get('mastodon.enabled'):
		try:
			mastodon()
		except Exception:
			log.error('Failed to post to Mastodon.')

	if cfg.get('bluesky.enabled'):
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
		await fetch_img()

if __name__ == '__main__':
	asyncio.run(main())
