import subprocess
from telebot import logging
import os

logger = logging.getLogger(__name__)

def download(track_link, cwd):
    try:
        # download track
        normal_download_command = ['spotdl', "--bitrate", "128k", track_link]
        command = normal_download_command

        os.makedirs(cwd, exist_ok=True)
        logger.info("Download Started ...")
        result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
        
        # Print the output of the command
        logger.info(result.stdout)

        logger.info("Finished download...")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing process {e}")
        logger.error(f"Outputs {e.output}")

        # Retry with downloading ffmpeg if necessary
        ffmpeg_command = ['spotdl', "--download-ffmpeg"]
        subprocess.run(ffmpeg_command)

        try:
            # Retry the normal download
            normal_download_command = ['spotdl', "--bitrate", "128k", track_link]
            command = normal_download_command
            subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing process {e}")
            logger.error(f"Outputs {e.output}")
            return False

    return True
