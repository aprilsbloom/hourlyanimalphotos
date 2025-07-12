import asyncio
import os
from datetime import datetime, timedelta
from typing import List, cast

import filetype
import requests
from PIL import Image
from requests_oauthlib import OAuth1Session

from modules import bluesky, tumblr, twitter
from sources import CatAPI, DogAPI, ImageSource
from utils.config import Config, TumblrConfig
from utils.image import SourceImage
from utils.globals import IMG_EXTENSIONS, MAX_IMG_FETCH_RETRY, cfg
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


def init_tumblr_oauth(cfg: Config, tumblr_cfg: TumblrConfig) -> None:
	tumblr_log = Logger("Tumblr")
	request_token_url = 'http://www.tumblr.com/oauth/request_token'
	authorize_url = 'http://www.tumblr.com/oauth/authorize'
	access_token_url = 'http://www.tumblr.com/oauth/access_token'

	# STEP 1: Obtain request token
	oauth_session = OAuth1Session(tumblr_cfg['consumer_key'], client_secret=tumblr_cfg['consumer_secret'])
	fetch_response = oauth_session.fetch_request_token(request_token_url)

	resource_owner_key = fetch_response.get('oauth_token')
	resource_owner_secret = fetch_response.get('oauth_token_secret')

	# redirect to authentication page
	full_authorize_url = oauth_session.authorization_url(authorize_url)
	tumblr_log.info(f'Please visit this URL and authorize: {full_authorize_url}')
	redirect_response = tumblr_log.input('Paste the full redirect URL here: ').strip()

	# retrieve verifier
	oauth_response = oauth_session.parse_authorization_response(redirect_response)
	verifier = oauth_response.get('oauth_verifier')

	# request final access token
	oauth_session = OAuth1Session(
		tumblr_cfg['consumer_key'],
		client_secret=tumblr_cfg['consumer_secret'],
		resource_owner_key=resource_owner_key,
		resource_owner_secret=resource_owner_secret,
		verifier=verifier
	)

	oauth_tokens = oauth_session.fetch_access_token(access_token_url)
	tumblr_cfg['oauth_token'] = oauth_tokens.get('oauth_token', '')
	tumblr_cfg['oauth_token_secret'] = oauth_tokens.get('oauth_token_secret', '')
	cfg.save()

	tumblr_log.success('Tumblr oauth token and secret have been set.')


def validate_cfg() -> None:
	# validate cfg entries
	# if a social media platform is enabled, ensure all keys are set
	has_found_enabled_source = False
	for source in cfg.cfg:
		source_cfg = cfg.cfg[source]

		# skip if not enabled
		if not source_cfg['enabled']:
			continue

		has_found_enabled_source = True

		# needs an api key to function lol
		if not source_cfg['api_key']:
			log.error(f'API key is not set for source "{source}" ("{source_cfg["name"]}"). Please set it in config.json.')
			os._exit(1)

    # twitter
		if source_cfg['twitter']['enabled']:
			twitter_keys = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']
			missing_keys = []
			for key in twitter_keys:
				if not source_cfg['twitter'][key]:
					missing_keys.append(key)

			if len(missing_keys) > 0:
				log.error(f'The following keys for Twitter in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}. Please set them in config.json.')
				os._exit(1)

		# tumblr
		if source_cfg['tumblr']['enabled']:
			tumblr_keys = ['blogname', 'consumer_key', 'consumer_secret']
			missing_keys = []
			for key in tumblr_keys:
				if not source_cfg['tumblr'][key]:
					missing_keys.append(key)

			if len(missing_keys) > 0:
				log.error(f'The following keys for Tumblr in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}. Please set them in config.json.')
				os._exit(1)

			if not source_cfg['tumblr']['oauth_token'] or not source_cfg['tumblr']['oauth_token_secret']:
				init_tumblr_oauth(cfg, source_cfg['tumblr'])

		# bluesky
		if source_cfg['bluesky']['enabled']:
			bluesky_keys = ['username', 'app_password']
			for key in bluesky_keys:
				if not source_cfg['bluesky'][key]:
					missing_keys.append(key)

			if len(missing_keys) > 0:
				log.error(f'The following keys for Bluesky in source "{source}" ("{source_cfg["name"]}") are not set: {", ".join(missing_keys)}. Please set them in config.json.')
				os._exit(1)

	if not has_found_enabled_source:
		log.error('No enabled sources found. Please enable at least one source in config.json.')
		os._exit(1)

async def main():
	validate_cfg()

	await post()

	# while True:
	# 	current_time = datetime.now()
	# 	goal_timestamp = current_time + timedelta(hours = 1, minutes = -current_time.minute, seconds = -current_time.second, microseconds=-current_time.microsecond)
	# 	log.info(f'Posting at: {goal_timestamp.strftime("%H:%M:%S")}')
	# 	await asyncio.sleep((goal_timestamp - current_time).total_seconds())
	# 	await post()

if __name__ == '__main__':
	asyncio.run(main())
