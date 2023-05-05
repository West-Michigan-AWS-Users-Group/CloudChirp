import os

from pydub import AudioSegment

import settings


def convert_to_wav():
    """converts mp3 file to wav"""
    for x in settings.site_locations:
        _site_abbv = x['site_abbv']
        file_path1 = f'./{_site_abbv}/{_site_abbv}_During_Hours.mp3'
        file_path2 = f'./{_site_abbv}/{_site_abbv}_During_Hours_No_Answer.mp3'
        file_path3 = f'./{_site_abbv}/{_site_abbv}_After_Hours.mp3'

        file_export1 = f'./{_site_abbv}/{_site_abbv}_During_Hours.wav'
        sound = AudioSegment.from_mp3(file_path1)
        sound.export(file_export1, format='wav')

        file_export2 = f'./{_site_abbv}/{_site_abbv}_During_Hours_No_Answer.wav'
        sound = AudioSegment.from_mp3(file_path2)
        sound.export(file_export2, format='wav')

        file_export3 = f'./{_site_abbv}/{_site_abbv}_After_Hours.wav'
        sound = AudioSegment.from_mp3(file_path3)
        sound.export(file_export3, format='wav')


def remove_old_files():
    """Removes the old mp3 files from the directory"""
    for x in settings.site_locations:
        _site_abbv = x['site_abbv']
        mp3_path = [f'./{_site_abbv}/{_site_abbv}_During_Hours.mp3',
                    f'./{_site_abbv}/{_site_abbv}_During_Hours_No_Answer.mp3',
                    f'./{_site_abbv}/{_site_abbv}_After_Hours.mp3']

        for mp3_file in mp3_path:
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
