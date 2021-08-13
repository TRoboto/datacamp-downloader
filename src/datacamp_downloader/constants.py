import tempfile

HOME_PAGE = "https://www.datacamp.com/"
LOGIN_URL = "https://www.datacamp.com/users/sign_in"
LOGIN_DETAILS_URL = "https://www.datacamp.com/api/users/signed_in"

SESSION_FILE = tempfile.gettempdir() + "/.datacamp.v3"

PROFILE_URL = "https://www.datacamp.com/profile/{slug}"
COURSE_DETAILS_API = "https://campus-api.datacamp.com/api/courses/{id}/"
EXERCISE_DETAILS_API = "https://campus-api.datacamp.com/api/exercise/{id}"
VIDEO_DETAILS_API = "https://projector.datacamp.com/api/videos/{hash}"
PROGRESS_API = "https://campus-api.datacamp.com/api/courses/{course_id}/chapters/{chapter_id}/progress"

LANGMAP = {
    "en": "English",
    "zh": "Chinese simplified",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "es": "Spanish",
}
