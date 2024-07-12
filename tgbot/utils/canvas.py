from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.editor import VideoFileClip, concatenate_videoclips

from telebot import logging

logger = logging.getLogger(__name__)


def loop_video(video_clip, audio_duration):
    """
    Loop the video clip until the audio clip ends.
    """
    video_duration = video_clip.duration
    num_loops = int(audio_duration // video_duration) + 1

    # Create a list of video clips to concatenate
    video_clips = [video_clip] * num_loops

    # Concatenate the video clips
    final_video = concatenate_videoclips(
        video_clips).set_duration(audio_duration)

    return final_video


def combine_video_audio(video_path, audio_path, output_path):
    """
    Combine video and audio, looping the video until the audio ends.
    """
    try:
        with VideoFileClip(video_path) as video_clip, AudioFileClip(audio_path) as audio_clip:
            final_video = loop_video(video_clip, audio_clip.duration)
            final_video = final_video.set_audio(audio_clip)
            final_video.write_videofile(
                output_path, codec='libx264', audio_codec='aac')
            logger.info(f"Output video saved to: {output_path}")
            return True
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False
