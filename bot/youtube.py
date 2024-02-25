import re
import os
from enum import Enum
from glob import glob
from pytube import YouTube, Stream
from pytube.extract import video_id


class AudioQuality(Enum):
    BEST = 'best'
    MEDIUM = 'medium'
    LOW = 'low'


class VideoQuality(Enum):
    _240p = '240p'
    _360p = '360p'
    _480p = '480p'
    _720p = '720p'
    _1080p = '1080p'


class YouTubeDownloader:
    def __init__(self, url: str):
        self.__url = url
        self.__yt = YouTube(self.__url)
        self.__output_base_path: str = "download/YouTube/"
        self.__audio_output_path: str = ""
        self.__video_output_path: str = ""

    @property
    def url(self) -> str:
        return self.__url

    @staticmethod
    def extract_video_id(url: str) -> str:
        return video_id(url)

    @staticmethod
    def get_url_from_id(id: str) -> str:
        """
        Constructs a YouTube URL from a video ID.

        Parameters:
        - id (str): The video ID.

        Returns:
        - str: The YouTube URL.
        - f"https://youtu.be/{id}"
        """
        return f"https://youtu.be/{id}"

    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        Checks if the provided URL is a valid YouTube URL.

        Supported YouTube URL formats include:
        - Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        - Shortened URL: https://youtu.be/VIDEO_ID
        - Embedded URL: https://www.youtube.com/embed/VIDEO_ID
        - No-cookie URL: https://www.youtube-nocookie.com/embed/VIDEO_ID
        - With additional parameters: https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID&index=INDEX_NUMBER

        Parameters:
        - url (str): The YouTube URL to be validated.

        Returns:
        - bool: True if the URL is a valid YouTube URL, False otherwise.
        """
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

        youtube_pattern = re.compile(youtube_regex)
        match = youtube_pattern.match(url)

        return True if match else False

    def download_audio(self, quality=AudioQuality.BEST) -> str:
        """Get the audio file of a youtube video."""
        audio_stream = self.__get_audio_stream(quality)

        if not audio_stream:
            print("This video does not have an audio-only version.")
            return ""

        self.__audio_output_path = audio_stream.download(
            output_path=f"{self.__output_base_path}/audio/",
            max_retries=5
        )
        return self.__audio_output_path

    def download_video(self, quality=VideoQuality._480p) -> str:
        """Downloads the video with the specified quality."""
        video_stream = self.__get_video_stream(quality)

        if not video_stream:
            print(f"Video quality '{quality.value}' not available.")
            return ""

        self.__video_output_path = video_stream.download(
            output_path=f"{self.__output_base_path}/video/",
            filename_prefix=quality.value,
            max_retries=5
        )

        return self.__video_output_path

    def get_audio_file(self) -> str | None:
        """Return the downloaded audio file."""
        if os.path.exists(self.__audio_output_path):
            return glob(f"{self.__audio_output_path}")[0]

    def get_video_file(self) -> str | None:
        """Return the downloaded video file."""
        if os.path.exists(self.__video_output_path):
            return glob(f"{self.__video_output_path}")[0]

    def delete_audio_file(self):
        """Delete the downloaded audio file."""
        file = self.get_audio_file()

        if file and os.path.isfile(file):
            os.remove(file)

    def delete_video_file(self):
        """Delete the downloaded video file."""
        file = self.get_video_file()

        if file and os.path.isfile(file):
            os.remove(file)

    def __get_audio_stream(self, quality: AudioQuality = AudioQuality.BEST) -> Stream | None:
        """Returns audio streams based on the specified quality."""
        valid_audio_streams = self.__get_available_audio_streams()

        if not valid_audio_streams:
            return None

        modes = {
            AudioQuality.BEST: lambda: max(
                valid_audio_streams, key=lambda s: s.bitrate),  # type: ignore

            AudioQuality.MEDIUM: lambda: sorted(
                valid_audio_streams, key=lambda s: s.bitrate)[len(valid_audio_streams) // 2],  # type: ignore

            AudioQuality.LOW: lambda: min(
                valid_audio_streams, key=lambda s: s.bitrate)  # type: ignore
        }

        return modes[quality]()

    def __get_video_stream(self, quality: VideoQuality) -> Stream | None:
        """
        Returns a video stream from a StreamQuery based on the specified quality.
        If the exact quality is not available, returns the closest available resolution.

        Args:
            video_query: A StreamQuery object from pytube.
            quality: The desired video quality from the VideoQuality enum.

        Returns:
            A video stream matching the closest available quality.
        """
        video_query = self.__yt.streams.filter(type="video")

        video_stream = video_query.get_by_resolution(quality.value)

        if not video_stream:
            # Find closest available resolution
            available_qualities = sorted(
                VideoQuality, key=lambda q: q.value,
                reverse=True
            )

            for q in available_qualities:
                stream = video_query.get_by_resolution(q.value)
                if stream:
                    print(
                        f"Requested quality '{quality.value}' not available. Downloading the closest: '{stream.resolution}'")
                    video_stream = stream
                    break

        return video_stream

    def __get_available_audio_streams(self) -> list[Stream]:
        stream_query = self.__yt.streams.filter(only_audio=True)

        audio_streams: list[Stream] = [stream for stream in stream_query]

        return [s for s in audio_streams if isinstance(s.bitrate, int)]

    def get_available_video_qualities(self) -> list[str]:
        """
        Returns a list of available video resolutions for the current YouTube video.

        Returns:
            A list of strings representing available resolutions.
        """

        return sorted([stream.resolution for stream in self.__yt.streams.filter(progressive=True, subtype="mp4") if stream.resolution])

    def delete_files(self):
        """Deletes all temporary files created by this class."""
        self.delete_audio_file()
        self.delete_video_file()

    def close(self):
        """Closes the FFmpeg process and deletes any remaining temporary files."""
        self.delete_files()

    def __del__(self):
        """Deletes temporary files upon object deletion."""
        self.close()
