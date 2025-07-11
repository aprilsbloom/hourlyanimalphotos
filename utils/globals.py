from typing import Dict, Final

from utils.config import Config

# ---- Misc ---- #
IMG_EXTENSIONS = ["jpg", "png", "jpeg", "webp"]
MAX_IMG_FETCH_RETRY = 3

CAT_TAGS = {
  "cat",
  "cats",

  "cat photo",
  "cat photos",

  "cat photographer",
  "cat photography",

  "hourly cat",
  "hourly cats",
  "hourly cat photo",
  "hourly cat photos",

  "kitten",
  "kittens",
  "kitty",
  "kitties",
  "kitty cat",
  "kitty cats",
  "kitty cat photo",
  "kitty cat photos",
}


REQUEST_TIMEOUT: Final[int] = 30
BASE_HEADERS: Final[Dict[str, str]] = {
	"User-Agent": "HourlyAnimalPhotos (https://github.com/aprilsbloom/hourly-animal-photos)",
	"Accept": "*/*",
	"Accept-Encoding": "gzip, deflate, br",
	"Connection": "keep-alive",
}



cfg = Config("config.json")
