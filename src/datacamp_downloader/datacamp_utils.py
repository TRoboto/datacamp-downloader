from pathlib import Path
import sys
from bs4 import BeautifulSoup
import re

from .constants import (
    COURSE_DETAILS_API,
    EXERCISE_DETAILS_API,
    LANGMAP,
    LOGIN_DETAILS_URL,
    LOGIN_URL,
    PROFILE_URL,
    PROGRESS_API,
    VIDEO_DETAILS_API,
)
from .helper import Logger, animate_wait, download_file, print_progress, save_text
from .templates.track import Track
from .templates.course import Chapter, Course
from .templates.exercise import Exercise
from .templates.video import Video


def login_required(f):
    def wrapper(*args):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(f"{login_required.__name__} can only decorate Datacamp class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        # if not self.has_active_subscription:
        #     Logger.error("No active subscription found.")
        #     return
        return f(*args)

    return wrapper


def try_except_request(f):
    def wrapper(*args):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(
                f"{try_except_request.__name__} can only decorate Datacamp class."
            )
            return

        try:
            return f(*args)
        except Exception:
            Logger.warning(f"Couldn't run {f.__name__} with inputs {args[1:]}")
        return

    return wrapper


class Datacamp:
    def __init__(self, session) -> None:

        self.session = session
        self.username = None
        self.password = None
        self.token = None
        self.has_active_subscription = False
        self.loggedin = False
        self.login_data = None

        self.courses = []
        self.tracks = []

    @animate_wait
    @try_except_request
    def login(self, username, password):
        if username == self.username and self.password == password and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.session.restart()
        self.username = username
        self.password = password

        req = self.session.get(LOGIN_URL)
        if not req or req.status_code != 200 or not req.text:
            Logger.error("Cannot access datacamp website!")
            return
        soup = BeautifulSoup(req.text, "html.parser")
        authenticity_token = soup.find("input", {"name": "authenticity_token"}).get(
            "value"
        )
        if not authenticity_token:
            Logger.error("Cannot find authenticity_token attribute!")
            return

        login_req = self.session.post(
            LOGIN_URL,
            params=[
                ("authenticity_token", authenticity_token),
                ("user[email]", username),
                ("user[password]", password),
            ],
        )
        if (
            not login_req
            or login_req.status_code != 200
            or "/users/sign_up" in login_req.text
        ):
            Logger.error("Incorrent username/password")
            return

        self._set_profile()

    @animate_wait
    def set_token(self, token):
        if self.token == token and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.session.restart()
        self.token = token
        cookie = {
            "name": "_dct",
            "value": token,
            "domain": ".datacamp.com",
            "secure": True,
        }
        self.session.add_cookie(cookie)
        self._set_profile()

    def _set_profile(self):
        page = self.session.get(LOGIN_DETAILS_URL)
        try:
            data = page.json()
        except:
            Logger.error("Incorrect input token!")
            return
        Logger.info("Hi, " + (data["first_name"] or data["last_name"] or data["email"]))

        if data["has_active_subscription"]:
            Logger.info("Active subscription found")
        else:
            Logger.warning("No active subscription found")

        self.loggedin = True
        self.login_data = data
        self.has_active_subscription = data["has_active_subscription"]

        self.session.save()

    @login_required
    def list_completed_tracks(self, refresh):
        if refresh or not self.tracks:
            self.get_completed_tracks()
        rows = [["#", "Title"]]
        for track in self.tracks:
            rows.append([track.id, track.name])
        Logger.print_table(rows)

    @login_required
    def list_completed_courses(self, refresh):
        if refresh or not self.courses:
            self.get_completed_courses()
        rows = [["#", "ID", "Title", "Datasets", "Exercises", "Videos"]]
        for i, course in enumerate(self.courses, 1):
            all_exercises_count = sum([c.nb_exercises for c in course.chapters])
            videos_count = sum([c.number_of_videos for c in course.chapters])
            rows.append(
                [
                    i,
                    course.id,
                    course.title,
                    len(course.datasets),
                    all_exercises_count - videos_count,
                    videos_count,
                ]
            )
        Logger.print_table(rows)

    @login_required
    def download_courses(
        self,
        courses_ids,
        directory,
        slides,
        datasets,
        videos,
        exercises,
        subtitles,
        audios,
        scripts,
    ):
        if "all" in courses_ids:
            if not self.courses:
                self.get_completed_courses()
            courses_to_download = self.courses
        else:
            courses_to_download = [self.get_course(id) for id in courses_ids]
        path = Path(directory)
        for i, course in enumerate(courses_to_download, 1):
            if not course:
                continue
            Logger.info(
                f"[{i}/{len(courses_to_download)}] Starts to download [{course.id}] {course.title}"
            )
            self._download_course(
                course,
                path,
                slides,
                datasets,
                videos,
                exercises,
                subtitles,
                audios,
                scripts,
            )

    def _download_course(
        self,
        course: Course,
        path: Path,
        slides,
        datasets,
        videos,
        exercises,
        subtitles,
        audios,
        scripts,
    ):
        download_path = path / course.slug
        if datasets:
            for dataset in course.datasets:
                if dataset.asset_url:
                    download_file(
                        self.session,
                        dataset.asset_url,
                        download_path / "datasets" / dataset.asset_url.split("/")[-1],
                    )
        for chapter in course.chapters:
            cpath = download_path / self._get_chapter_name(chapter)
            if slides and chapter.slides_link:
                download_file(
                    self.session,
                    chapter.slides_link,
                    cpath / chapter.slides_link.split("/")[-1],
                )
            if exercises or videos or audios or scripts:
                self.download_others(
                    course.id,
                    chapter,
                    cpath,
                    videos=videos,
                    exercises=exercises,
                    audios=audios,
                    scripts=scripts,
                    subtitles=subtitles,
                )

    def _get_chapter_name(self, chapter: Chapter):
        if chapter.title and chapter.title_meta:
            return chapter.slug
        if chapter.title:
            return f"chapter-{chapter.number}-{chapter.slug}"
        return f"chapter-{chapter.number}"

    def download_normal_exercise(self, exercise: Exercise, path: Path):
        save_text(path, str(exercise))
        subexs = exercise.data.subexercises
        if subexs:
            for i, subexercise in enumerate(subexs, 1):
                exercise = self._get_exercise(subexercise)
                self.download_normal_exercise(
                    exercise, path.parent / (path.name[:-3] + f"_sub{i}.md")
                )

    def download_others(self, course_id, chapter: Chapter, path: Path, **kwargs):
        exercises = kwargs.get("exercises")
        videos = kwargs.get("videos")
        audios = kwargs.get("audios")
        scripts = kwargs.get("scripts")
        subtitles = kwargs.get("subtitles")
        ids = self._get_exercises_ids(course_id, chapter.id)
        exercise_counter = 1
        video_counter = 1
        for i, id in enumerate(ids, 1):
            print_progress(i, len(ids), f"chapter {chapter.number}")
            exercise = self._get_exercise(id)
            if not exercise:
                continue
            if exercises and not exercise.is_video:
                self.download_normal_exercise(
                    exercise, path / "exercises" / f"ex{exercise_counter}.md"
                )
                exercise_counter += 1
            if exercise.is_video:
                video = self._get_video(exercise.data.get("projector_key"))
                video_path = path / "videos" / f"ch{chapter.number}_{video_counter}"
                if videos and video.video_mp4_link:
                    download_file(
                        self.session,
                        video.video_mp4_link,
                        video_path.with_suffix(".mp4"),
                        False,
                    )
                if audios and video.audio_link:
                    download_file(
                        self.session,
                        video.audio_link,
                        path / "audios" / f"ch{chapter.number}_{video_counter}.mp3",
                        False,
                    )
                if scripts and video.script_link:
                    download_file(
                        self.session,
                        video.script_link,
                        path / "scripts" / (video_path.name + "_script.md"),
                        False,
                    )
                if subtitles and video.subtitles:
                    for sub in subtitles:
                        subtitle = self._get_subtitle(sub, video)
                        if not subtitle:
                            continue
                        download_file(
                            self.session,
                            subtitle.link,
                            video_path.parent / (video_path.name + f"_{sub}.vtt"),
                            False,
                        )
                video_counter += 1
        sys.stdout.write("\n")

    @animate_wait
    def get_completed_tracks(self):
        self.tracks = []
        profile = self.session.get(PROFILE_URL.format(slug=self.login_data["slug"]))
        soup = BeautifulSoup(profile.text, "html.parser")
        tracks_name = soup.findAll("div", {"class": "track-block__main"})
        tracks_link = soup.findAll(
            "a", {"href": re.compile("^/tracks"), "class": "shim"}
        )
        for i in range(len(tracks_link)):
            link = "https://www.datacamp.com" + tracks_link[i]["href"]
            self.tracks.append(
                Track(i + 1, tracks_name[i].getText().replace("\n", " ").strip(), link)
            )
        self.session.save()
        return self.tracks

    @animate_wait
    def get_completed_courses(self):
        self.courses = []
        profile = self.session.get(PROFILE_URL.format(slug=self.login_data["slug"]))
        soup = BeautifulSoup(profile.text, "html.parser")
        courses_id = soup.findAll("article", {"class": re.compile("^js-async")})
        for id_tag in courses_id:
            id = id_tag.get("data-id")
            course = self._get_course(id)
            if course:
                self.courses.append(course)

        self.session.save()
        return self.courses

    def _get_subtitle(self, sub, video: Video):
        if not LANGMAP.get(sub):
            return
        for subtitle in video.subtitles:
            if subtitle.language == LANGMAP[sub]:
                return subtitle

    @try_except_request
    def _get_video(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get(VIDEO_DETAILS_API.format(hash=id))
        if "error" in res.json():
            raise ValueError("Cannot get info.")
        return Video(**res.json())

    @try_except_request
    def _get_exercises_ids(self, course_id, chapter_id):
        if not course_id or not chapter_id:
            raise ValueError("ID tags not found.")
        res = self.session.get(
            PROGRESS_API.format(course_id=course_id, chapter_id=chapter_id)
        )
        data = res.json()
        if "error" in data:
            raise ValueError("Cannot get info.")
        ids = [e["exercise_id"] for e in data]
        return ids

    @try_except_request
    def _get_exercise(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get(EXERCISE_DETAILS_API.format(id=id))
        if "error" in res.json():
            raise ValueError("Cannot get info.")
        return Exercise(**res.json())

    @try_except_request
    def _get_course(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get(COURSE_DETAILS_API.format(id=id))
        if "error" in res.json():
            raise ValueError("Cannot get info.")
        return Course(**res.json())

    @animate_wait
    def get_course(self, id):
        for course in self.courses:
            if course.id == id:
                return course
        return self._get_course(id)