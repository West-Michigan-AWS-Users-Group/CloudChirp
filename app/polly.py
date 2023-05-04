import os
import sys
from contextlib import closing

import boto3
from botocore.exceptions import BotoCoreError, ClientError

import settings
from app_logger import logger

# section of the AWS credentials file (~/.aws/credentials).
polly = boto3.client('polly')


def create_mp3():
    """sends text files to Polly to be converted to .mp3 audio"""
    try:
        for x in settings.site_locations:
            _site_abbv = x['site_abbv']
            with open(f'./{_site_abbv}/{_site_abbv}_During_Hours.txt', 'r') as f:
                contents1 = f.read()
            with open(f'./{_site_abbv}/{_site_abbv}_During_Hours_No_Answer.txt', 'r') as f:
                contents2 = f.read()
            with open(f'./{_site_abbv}/{_site_abbv}_After_Hours.txt', 'r') as f:
                contents3 = f.read()
            response1 = polly.synthesize_speech(Engine='neural', Text=contents1, TextType='ssml', OutputFormat='mp3',
                                                VoiceId='Salli')
            response2 = polly.synthesize_speech(Engine='neural', Text=contents2, TextType='ssml', OutputFormat='mp3',
                                                VoiceId='Salli')
            response3 = polly.synthesize_speech(Engine='neural', Text=contents3, TextType='ssml', OutputFormat='mp3',
                                                VoiceId='Salli')
            # Access the audio stream from the response
            if 'AudioStream' in response1:
                # Note: Closing the stream is important because the service throttles on the
                # number of parallel connections. Here we are using contextlib.closing to
                # ensure the close method of the stream object will be called automatically
                # at the end of the with statement's scope.
                with closing(response1['AudioStream']) as stream:
                    output = os.path.join(f'./{_site_abbv}/', f'{_site_abbv}_During_Hours.mp3')

                    try:
                        # Open a file for writing the output as a binary stream
                        with open(output, 'wb') as file:
                            file.write(stream.read())
                    except IOError as error:
                        # Could not write to file, exit gracefully
                        logger.error(error)
                        sys.exit(-1)

            if 'AudioStream' in response2:
                # Note: Closing the stream is important because the service throttles on the
                # number of parallel connections. Here we are using contextlib.closing to
                # ensure the close method of the stream object will be called automatically
                # at the end of the with statement's scope.
                with closing(response2['AudioStream']) as stream:
                    output = os.path.join(f'./{_site_abbv}/', f'{_site_abbv}_During_Hours_No_Answer.mp3')

                    try:
                        # Open a file for writing the output as a binary stream
                        with open(output, 'wb') as file:
                            file.write(stream.read())
                    except IOError as error:
                        # Could not write to file, exit gracefully
                        logger.error(error)
                        sys.exit(-1)

            if 'AudioStream' in response3:
                # Note: Closing the stream is important because the service throttles on the
                # number of parallel connections. Here we are using contextlib.closing to
                # ensure the close method of the stream object will be called automatically
                # at the end of the with statement's scope.
                with closing(response3['AudioStream']) as stream:
                    output = os.path.join(f'./{_site_abbv}/', f'{_site_abbv}_After_Hours.mp3')

                    try:
                        # Open a file for writing the output as a binary stream
                        with open(output, 'wb') as file:
                            file.write(stream.read())
                    except IOError as error:
                        # Could not write to file, exit gracefully
                        logger.error(error)
                        sys.exit(-1)

            else:
                # The response didn't contain audio data, exit gracefully
                logger.error('Could not stream audio')
                sys.exit(-1)

    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        logger.error(error)
        sys.exit(-1)
