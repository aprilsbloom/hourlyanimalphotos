from typing import Final

from utils.config import Config
from utils.logger import Logger

# ---- Misc ---- #
CAT_TAGS = ["cat", "cat_photo", "cat_photographer", "cat_photography", "cat_photos", "catlife", "catlove", "catlover", "catlovers", "catoftheday", "catphoto", "catphotographer", "catphotography", "catphotos", "cats", "cats_of_instagram", "catsofinstagram", "catsoftheworld", "hourly_cat", "hourly_cat_photo", "hourly_cat_photography", "hourly_cat_photos", "hourly_cats", "hourlycat", "hourlycatphoto", "hourlycatphotography", "hourlycatphotos", "hourlycats"]
IMG_EXTENSIONS = ["jpg", "png", "jpeg", "webp"]
BASE_HEADERS: Final = {
	"User-Agent": "HourlyCatPhotos (https://github.com/aprilsbloom/hourly-cat-photos)",
	"Accept": "*/*",
	"Accept-Encoding": "gzip, deflate, br",
	"Connection": "keep-alive",
}

MAX_IMG_FETCH_RETRY = 3

log = Logger()
cfg = Config("config.json")
