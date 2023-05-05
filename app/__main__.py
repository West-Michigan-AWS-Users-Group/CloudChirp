import aa
import audio_conversion
import index
import polly
import transfer_to_s3
from app_logger import logger


def main():
    """
    Main function to generate auto attendants, and the front end index used to download them.
    """
    logger.info('Generating scripts')
    aa.script_generation()
    logger.info('Creating mp3s w/ AWS Polly')
    polly.create_mp3()
    logger.info('Converting mp3s to wav')
    audio_conversion.convert_to_wav()
    logger.info('Cleaning up old audio mp3s')
    audio_conversion.remove_old_files()
    logger.info('Syncing files to S3')
    transfer_to_s3.upload_auto_attendants()
    logger.info('Generating index.html')
    index.index_generation()


if __name__ == '__main__':
    main()
