# Hourly Animal Photos
The source code for @HourlyCatPhotos & @HourlyDogPhotos, a bot to post animal photos hourly.
It fetches images from both [TheCatAPI](https://thecatapi.com/) & [TheDogAPI](https://thedogapi.com/), crossposting to Twitter, Tumblr & Bluesky.

## Setup
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
2. Create a virtual environment
```sh
uv venv
```

3. Activate the virtual environment
```sh
# Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Install the dependencies
```sh
uv pip install -r requirements.txt
```

5. Run the program
```sh
py main.py
```

6. Enter your credentials in `config.json`. The program will tell you what is incorrect and where to fix it.