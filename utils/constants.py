from typing import Dict, Final

# ---- Misc ---- #
IMG_EXTENSIONS = ["jpg", "png", "jpeg", "webp"]
MAX_IMG_FETCH_RETRY = 3

MAX_POST_RETRY = 3
POST_RETRY_SLEEP = 5

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

DOG_TAGS = {
  "dog",
  "dogs",
  "dog photo",
  "dog photos",

  "puppy",
  "puppies",
  "puppy photo",
  "puppy photos",

  "hourly dog",
  "hourly dogs",
  "hourly dog photo",
  "hourly dog photos",
}

REQUEST_TIMEOUT: Final[int] = 30
BASE_HEADERS: Final[Dict[str, str]] = {
	"User-Agent": "HourlyAnimalPhotos (https://github.com/aprilsbloom/hourly-animal-photos)",
	"Accept": "*/*",
	"Accept-Encoding": "gzip, deflate, br",
	"Connection": "keep-alive",
}