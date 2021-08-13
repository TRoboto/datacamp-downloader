import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

import datacamp_downloader.session as session

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
from .helper import (
    Logger,
    animate_wait,
    correct_path,
    download_file,
    fix_track_link,
    get_table,
    print_progress,
    save_text,
)
from .templates.course import Chapter, Course
from .templates.exercise import Exercise
from .templates.track import Track
from .templates.video import Video


def login_required(f):
    def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(f"{login_required.__name__} can only decorate Datacamp class.")
            return
        if not self.loggedin:
            Logger.error("Login first!")
            return
        return f(*args, **kwargs)

    return wrapper


def try_except_request(f):
    def wrapper(*args, **kwargs):
        self = args[0]
        if not isinstance(self, Datacamp):
            Logger.error(
                f"{try_except_request.__name__} can only decorate Datacamp class."
            )
            return

        try:
            return f(*args, **kwargs)
        except Exception as e:
            if str(e):
                Logger.error(e)
        return

    return wrapper


class Datacamp:
    def __init__(self, session: "session.Session") -> None:

        self.session = session
        self.init()

    def init(self):
        self.username = None
        self.password = None
        self.token = None
        self.has_active_subscription = False
        self.loggedin = False
        self.login_data = None
        self.profile_data = None

        self.courses = []
        self.tracks = []

        self.not_found_courses = set()

    @animate_wait
    @try_except_request
    def login(self, username, password):
        if username == self.username and self.password == password and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.init()

        self.username = username
        self.password = password

        req = self.session.get(LOGIN_URL)
        if not req:
            Logger.error("Cannot access datacamp website!")
            return
        self.session.wait_for_element_by_css_selector("#user_email")
        email = self.session.get_element_by_id("user_email")
        email.send_keys(username)
        # click remember me
        # self.session.click_element("remember_me_modal")
        next_button = self.session.get_element_by_xpath('//button[@tabindex="2"]')
        next_button.click()

        # self.session.wait_for_element("user_password")
        self.session.wait_for_element_by_css_selector(
            "#user_password", "#flash_messages"
        )
        password_field = self.session.get_element_by_id("user_password")
        try:
            password_field.send_keys(password)
        except Exception:
            Logger.error("Incorrect email!")
            return

        submit_button = self.session.get_element_by_xpath('//input[@tabindex="4"]')
        submit_button.click()
        self.session.wait_for_element_by_css_selector("#__next", "#flash_messages")

        page = self.session.driver.page_source
        if not page or "/users/sign_up" in page:
            Logger.error("Incorrect password")
            return

        self.token = self.session.driver.get_cookie("_dct")["value"]
        self._set_profile()

    @animate_wait
    @try_except_request
    def set_token(self, token):
        if self.token == token and self.loggedin:
            Logger.info("Already logged in!")
            return

        self.init()
        self.session.start()

        self.token = token
        self.session.add_token(token)
        self._set_profile()

    def get_profile_data(self):
        if not self.profile_data:
            profile = self.session.get(PROFILE_URL.format(slug=self.login_data["slug"]))
            self.session.driver.minimize_window()
            soup = BeautifulSoup(profile, "html.parser")
            self.profile_data = self.session.to_json(
                soup.find(id="__NEXT_DATA__").string
            )
        return self.profile_data

    @login_required
    @animate_wait
    def list_completed_tracks(self, refresh):
        table = get_table()
        table.set_cols_width([6, 40, 10])
        table.add_row(["ID", "Title", "Courses"])
        table_so_far = table.draw()
        Logger.clear_and_print(table_so_far)
        for track in self.get_completed_tracks(refresh):
            table.add_row([track.id, track.title, len(track.courses)])
            table_str = table.draw()
            Logger.clear_and_print(table_str.replace(table_so_far, "").strip())
            table_so_far = table_str

    @login_required
    @animate_wait
    def list_completed_courses(self, refresh):
        table = get_table()
        table.set_cols_width([6, 40, 10, 10, 10])
        table.add_row(["ID", "Title", "Datasets", "Exercises", "Videos"])
        table_so_far = table.draw()
        Logger.clear_and_print(table_so_far)
        for i, course in enumerate(self.get_completed_courses(refresh), 1):
            all_exercises_count = sum([c.nb_exercises for c in course.chapters])
            videos_count = sum([c.number_of_videos for c in course.chapters])
            course.order = i
            table.add_row(
                [
                    i,
                    course.title,
                    len(course.datasets),
                    all_exercises_count - videos_count,
                    videos_count,
                ]
            )
            table_str = table.draw()
            Logger.clear_and_print(table_str.replace(table_so_far, "").strip())
            table_so_far = table_str

    @login_required
    def download(self, ids, directory, **kwargs):
        self.overwrite = kwargs.get("overwrite")
        if "all-t" in ids:
            if not self.tracks:
                Logger.error(
                    "No tracks to download! Maybe run `datacamp tracks` first!"
                )
                return
            to_download = self.tracks
        elif "all" in ids:
            if not self.courses:
                Logger.error(
                    "No courses to download! Maybe run `datacamp courses` first!"
                )
                return
            to_download = self.courses
        else:
            to_download = []
            for id in ids:
                if "t" in id:
                    track = self.get_track(id)
                    if not track:
                        Logger.warning(f"Track {id} is not fetched. Ignoring it.")
                        continue
                    to_download.append(track)
                elif id.isnumeric():
                    course = self.get_course_by_order(int(id))
                    if not course:
                        Logger.warning(f"Course {id} is not fetched. Ignoring it.")
                        continue
                    to_download.append(course)

        if not to_download:
            Logger.error("No courses/tracks to download!")
            return

        path = Path(directory) if not isinstance(directory, Path) else directory

        self.session.start()
        self.session.driver.minimize_window()

        for i, material in enumerate(to_download, 1):
            if not material:
                continue
            Logger.info(
                f"[{i}/{len(to_download)}] Start to download ({material.id}) {material.title}"
            )
            if isinstance(material, Course):
                self.download_course(material, path, **kwargs)
            else:
                self.download_track(material, path, **kwargs)

    def download_normal_exercise(
        self, exercise: Exercise, path: Path, include_last_attempt: bool = False
    ):
        save_text(path, str(exercise), self.overwrite)
        if include_last_attempt and exercise.is_python and exercise.last_attempt:
            save_text(
                path.parent / (path.name[:-3] + f".py"),
                exercise.last_attempt,
                self.overwrite,
            )
        subexs = exercise.data.subexercises
        if subexs:
            for i, subexercise in enumerate(subexs, 1):
                exercise = self._get_exercise(subexercise)
                self.download_normal_exercise(
                    exercise, path.parent / (path.name[:-3] + f"_sub{i}.md")
                )

    def download_track(self, track: Track, path: Path, **kwargs):
        path = path / correct_path(track.title)
        for i, course in enumerate(track.courses, 1):
            Logger.info(
                f"[{i}/{len(track.courses)}] Download ({course.id}) {course.title} from ({track.title} Track)"
            )
            self.download_course(course, path, f"{i}-", **kwargs)

    def download_course(self, course: Course, path: Path, index="", **kwargs):
        download_path = path / (
            index + correct_path(course.slug or course.title.lower().replace(" ", "-"))
        )
        if kwargs.get("datasets") and course.datasets:
            for i, dataset in enumerate(course.datasets, 1):
                print_progress(i, len(course.datasets), f"datasets")
                if dataset.asset_url:
                    download_file(
                        dataset.asset_url,
                        download_path
                        / "datasets"
                        / correct_path(dataset.asset_url.split("/")[-1]),
                        False,
                        overwrite=self.overwrite,
                    )
            sys.stdout.write("\n")
        for chapter in course.chapters:
            cpath = download_path / self._get_chapter_name(chapter)
            if kwargs.get("slides") and chapter.slides_link:
                download_file(
                    chapter.slides_link,
                    cpath / correct_path(chapter.slides_link.split("/")[-1]),
                    overwrite=self.overwrite,
                )
            if (
                kwargs.get("exercises")
                or kwargs.get("videos")
                or kwargs.get("audios")
                or kwargs.get("scripts")
            ):
                self.download_others(course.id, chapter, cpath, **kwargs)

    def download_others(self, course_id, chapter: Chapter, path: Path, **kwargs):
        exercises = kwargs.get("exercises")
        videos = kwargs.get("videos")
        audios = kwargs.get("audios")
        scripts = kwargs.get("scripts")
        subtitles = kwargs.get("subtitles")
        last_attempt = kwargs.get("last_attempt")
        ids = self._get_exercises_ids(course_id, chapter.id)
        last_attempts = self.get_exercises_last_attempt(course_id, chapter.id)
        exercise_counter = 1
        video_counter = 1
        for i, id in enumerate(ids, 1):
            print_progress(i, len(ids), f"chapter {chapter.number}")
            exercise = self._get_exercise(id)
            exercise.last_attempt = last_attempts[id]
            if not exercise:
                continue
            if exercises and not exercise.is_video:
                self.download_normal_exercise(
                    exercise,
                    path / "exercises" / f"ex{exercise_counter}.md",
                    last_attempt,
                )
                exercise_counter += 1
            if exercise.is_video:
                video = self._get_video(exercise.data.get("projector_key"))
                if not video:
                    continue
                video_path = path / "videos" / f"ch{chapter.number}_{video_counter}"
                if videos and video.video_mp4_link:
                    download_file(
                        video.video_mp4_link,
                        video_path.with_suffix(".mp4"),
                        overwrite=self.overwrite,
                    )
                if audios and video.audio_link:
                    download_file(
                        video.audio_link,
                        path / "audios" / f"ch{chapter.number}_{video_counter}.mp3",
                        False,
                        overwrite=self.overwrite,
                    )
                if scripts and video.script_link:
                    download_file(
                        video.script_link,
                        path / "scripts" / (video_path.name + "_script.md"),
                        False,
                        overwrite=self.overwrite,
                    )
                if subtitles and video.subtitles:
                    for sub in subtitles:
                        subtitle = self._get_subtitle(sub, video)
                        if not subtitle:
                            continue
                        download_file(
                            subtitle.link,
                            video_path.parent / (video_path.name + f"_{sub}.vtt"),
                            False,
                            overwrite=self.overwrite,
                        )
                video_counter += 1
            print_progress(i, len(ids), f"chapter {chapter.number}")
        sys.stdout.write("\n")

    def get_completed_tracks(self, refresh=False):
        if self.tracks and not refresh:
            yield from self.tracks
            return

        self.tracks = []

        data = self.get_profile_data()
        completed_tracks = data["props"]["pageProps"]["completed_tracks"]
        for i, track in enumerate(completed_tracks, 1):
            self.tracks.append(Track(f"t{i}", track["title"].strip(), track["url"]))
        all_courses = set()
        # add courses
        for track in self.tracks:
            courses = list(self._get_courses_from_link(fix_track_link(track.link)))
            if not courses:
                continue
            track.courses = courses
            all_courses.update(track.courses)
            yield track
        # add to courses
        current_ids = [c.id for c in self.courses]
        for course in all_courses:
            if course.id not in current_ids:
                self.courses.append(course)

        self.session.save()

    def get_completed_courses(self, refresh=False):
        if self.courses and not refresh:
            yield from self.courses
            return

        self.courses = []

        data = self.get_profile_data()
        completed_courses = data["props"]["pageProps"]["completed_courses"]
        for course in completed_courses:
            fetched_course = self.get_course(course["id"])
            if not fetched_course:
                continue
            self.session.driver.minimize_window()
            self.courses.append(fetched_course)
            yield fetched_course

        if not self.courses:
            return []

        self.session.save()

    def get_course(self, id):
        if id in self.not_found_courses:
            return
        for course in self.courses:
            if course.id == id:
                return course
        return self._get_course(id)

    def get_course_by_order(self, order):
        for course in self.courses:
            if course.order == order and course.id not in self.not_found_courses:
                return course

    @try_except_request
    def get_exercises_last_attempt(self, course_id, chapter_id):
        data = self.session.get_json(
            PROGRESS_API.format(course_id=course_id, chapter_id=chapter_id)
        )
        if "error" in data:
            raise ValueError(
                f"Cannot get exercises for course {course_id}, chapter {chapter_id}."
            )
        last_attempt = {e["exercise_id"]: e["last_attempt"] for e in data}
        return last_attempt

    def get_track(self, id):
        for track in self.tracks:
            if track.id == id:
                return track

    @try_except_request
    def _get_courses_from_link(self, link: str):
        html = self.session.get(link)
        self.session.driver.minimize_window()

        soup = BeautifulSoup(html, "html.parser")
        courses_ids = soup.findAll("article", {"class": re.compile("^js-async")})
        for i, id_tag in enumerate(courses_ids, 1):
            id = id_tag.get("data-id")
            if not id:
                continue
            course = self.get_course(int(id))
            if course:
                yield course

    def _get_chapter_name(self, chapter: Chapter):
        if chapter.title and chapter.title_meta:
            return correct_path(chapter.slug)
        if chapter.title:
            return correct_path(
                f"chapter-{chapter.number}-{chapter.title.replace(' ', '-').lower()}"
            )
        return f"chapter-{chapter.number}"

    def _set_profile(self):
        try:
            data = self.session.get_json(LOGIN_DETAILS_URL)
        except Exception as e:
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
        res = self.session.get_json(VIDEO_DETAILS_API.format(hash=id))
        if "error" in res:
            raise ValueError()
        return Video(**res)

    @try_except_request
    def _get_exercises_ids(self, course_id, chapter_id):
        if not course_id or not chapter_id:
            raise ValueError("ID tags not found.")
        data = self.session.get_json(
            PROGRESS_API.format(course_id=course_id, chapter_id=chapter_id)
        )
        if "error" in data:
            raise ValueError(
                f"Cannot get exercises for course {course_id}, chapter {chapter_id}."
            )
        ids = [e["exercise_id"] for e in data]
        return ids

    @try_except_request
    def _get_exercise(self, id):
        if not id:
            raise ValueError("ID tag not found.")
        res = self.session.get_json(EXERCISE_DETAILS_API.format(id=id))
        if "error" in res:
            raise ValueError(f"Cannot get exercise with id: {id}.")
        return Exercise(**res)

    @try_except_request
    def _get_course(self, id):
        if not id:
            self.not_found_courses.add(id)
            raise ValueError("ID tag not found.")
        res = self.session.get_json(COURSE_DETAILS_API.format(id=id))
        if "error" in res:
            self.not_found_courses.add(id)
            raise ValueError()
        return Course(**res)
