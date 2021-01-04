import os, json, shutil, sys
import datetime, time, zipf
import xml.etree.ElementTree as ET
import time
import requests

from domino.core import log, Version, Server
from domino.jobs import Job, JobReport
from domino.distro import Distro
from domino.globalstore import GlobalStore

def make_archive(output_filename, source_dir):
    relroot = os.path.abspath(source_dir)
    with zipf.ZipFile(output_filename, "w", zipf.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir, topdown=False):
            #zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)

def correction_times(PathForBackup):
    ''' Корректировка времен создания файлов
    Для нормальной работы архиватора требуется, чтобы время модификации или создания (кто разберет)
    файла было больше 1980 года (зачем то), ну и ладно
    Поэому у всех файлов(папток) время модификации или создания которых менее 1980 года (октуда то взялись)
    время выставляется на 1980 год
    '''
    for file in os.listdir(PathForBackup):
        path = os.path.join(PathForBackup, file) #file
        if not os.path.isdir(path):
            date_of_files = time.localtime(os.stat(path).st_mtime)
            if date_of_files[0] < 1980:
                ans_time = time.mktime(datetime.datetime.now().timetuple())
                log.info("Корректировка времени %s", path)
                os.utime(path, (ans_time, ans_time))
        else:
            date_of_files = time.localtime(os.stat(path).st_mtime)
            if date_of_files[0] < 1980:
                ans_time = time.mktime(datetime.datetime.now().timetuple())
                log.info("Корректировка времени %s", path)
                os.utime(path, (ans_time, ans_time))
            correction_times(path)

def publicate_version(product, version):
    job_name = f"Публикация {product}.{version}"
    #print(f'{job_name} ...')
    with Job('developer', job_name) as job:
        version_folder = Server.version_folder(product, version)
        if not os.path.isdir(version_folder):
            raise Exception(f"Не обнаружено версии {product}.{version}")
        
        correction_times(version_folder)
        distro = Distro(product, version)
        distro_file = os.path.join(job.temp, distro.file_name)
        make_archive(distro_file, version_folder)
        gs = GlobalStore()
        job.log(f'Публикация на {gs.server}')
        gs.upload_distro(product, version, distro_file)


if  __name__ ==  "__main__" :
    try:
        publicate_version(sys.argv[1], Version.parse(sys.argv[2]))
    except BaseException as ex:
        log.exception(__file__)
        print(ex)











