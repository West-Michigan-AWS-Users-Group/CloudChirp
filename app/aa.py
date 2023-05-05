import os

from jinja2 import Environment, FileSystemLoader

import settings
from app_logger import logger


def save_to_file(script_text, _site_abbv, file_name):
    """save output file"""
    with open(f'./{_site_abbv}/{_site_abbv}{file_name}.txt', 'w') as f:
        f.write(script_text)


def script_generation():
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    aa_during = env.get_template('aa_during_hours.j2')
    aa_after = env.get_template('aa_after_hours.j2')
    aa_no_answer = env.get_template('aa_no_answer.j2')

    for x in settings.site_locations:
        output = aa_during.render(**x)
        path = f'./{x["site_abbv"]}'
        permissions = 0o777
        try:
            os.mkdir(path, mode=permissions)
            os.chmod(str(path), permissions)
        except FileExistsError:
            logger.info(f'Directory {path} already exists')
        except Exception as e:
            logger.info(f'An error occurred: {e}')
        save_to_file(output, x['site_abbv'], '_During_Hours')
        output2 = aa_after.render(**x)
        save_to_file(output2, x['site_abbv'], '_After_Hours')
        output3 = aa_no_answer.render(**x)
        save_to_file(output3, x['site_abbv'], '_During_Hours_No_Answer')
