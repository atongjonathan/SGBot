from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import os
import moviepy.config as mp_config

# Optionally set the path to ffmpeg manually
# mp_config.change_settings({"FFMPEG_BINARY": "path_to_your_ffmpeg_binary"})

def loop_video(video_clip, audio_duration):
    """
    Loop the video clip until the audio clip ends.
    """
    video_duration = video_clip.duration
    num_loops = int(audio_duration // video_duration) + 1
    video_clips = [video_clip] * num_loops
    
    final_video = concatenate_videoclips(video_clips).set_duration(audio_duration)
    return final_video

def combine_video_audio(video_path, audio_path, output_path):
    """
    Combine video and audio, looping the video until the audio ends.
    """    
    try:
        with VideoFileClip(video_path) as video_clip, AudioFileClip(audio_path) as audio_clip:
            final_video = loop_video(video_clip, audio_clip.duration)
            final_video = final_video.set_audio(audio_clip)
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            print(f"Output video saved to: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Paths to your video and audio files
video_path = r""
audio_path = r""
output_path = r""

combine_video_audio(video_path, audio_path, output_path)
