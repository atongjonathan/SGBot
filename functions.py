import subprocess
from logging import getLogger

logger = getLogger(__name__)


def download(track_link):
    try:
        # download track
        normal_download_command = ['spotdl', "--bitrate", "128k",
                                   track_link]  # nomal download
        command = normal_download_command  # normal download
        logger.info("Starting to download")
        result = subprocess.run(command,
                                cwd="output",
                                check=True,
                                text=True,
                                capture_output=True)
        logger.info(result.stdout)
        logger.info("Finished download...")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing process {e}")
        logger.error(f"Outputs {e.output}")
        ffmpeg_command = ['spotdl', "--download-ffmpeg"]
        subprocess.run(ffmpeg_command)
        try:
            normal_download_command = ['spotdl', "--bitrate", "128k",
                                       track_link]  # nomal download
            command = normal_download_command  # normal download
            subprocess.run(command, cwd="output")
            return True
        except:
            logger.error(f"Error executing process {e}")
            logger.error(f"Outputs {e.output}")
        return False
