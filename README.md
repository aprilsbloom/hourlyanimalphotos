# Hourly Cat Photos
The source code for [@HourlyCatPhotos](https://twitter.com/HourlyCatPhotos), a Twitter bot I run that posts a new cat photo every hour.
It fetches images from [TheCatAPI](https://thecatapi.com/). I also crosspost to [Mastodon](https://botsin.space/@hourlycatphotos), [Tumblr](https://hourlycatphotos.tumblr.com/) & [Bluesky](https://bsky.app/profile/hourlycatphotos.bsky.social).

## Setup
Run `pip install -r requirements.txt` to install the required dependencies.

Then, run `main.py`. It will create a file named `config.json`, which you need to fill out with your own API keys.

Once you have filled out `config.json`, run `main.py` again - it will then post photos every hour.

# Hourly Animal Photos
The source code for @HourlyCatPhotos & @HourlyDogPhotos, a bot to post animal photos hourly.
It fetches images from both [TheCatAPI](https://thecatapi.com/) & [TheDogAPI](https://thedogapi.com/), crossposting to Twitter, Tumblr & Bluesky.

## Setup
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
2. Activate the virtual environment
```sh
# Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. Install the dependencies
```sh
uv pip install -r requirements.txt
```

4. Run the program
```sh
py main.py
```

5. It will prompt you to enter your credentials