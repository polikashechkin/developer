# job.check_on_break() : ууауауауауауауау
# job.error(msg) : ууауауауауауауау
# job.check_on_break() : ууауауауауауауау
# job.account_id : ууауауауауауауау
#
# job.pg_connection : ууауауауауауауау
# job:version : ууауауауауауауау

## create_and_publicate:import
import os, json, shutil, sys
import datetime, time
import xml.etree.ElementTree as ET
import zipf
import requests
## create_and_publicate:import

def create_and_publicate_stop(job):
    pass 

def create_and_publicate_start(job):
    pass 

def create_and_publicate(job):
    pass 

from domino.core import log, Version, DOMINO_ROOT
from domino.jobs import Proc

#def создать_zip_файл(job, zip_файл, исходная_папка):
#    папка = os.path.abspath(исходная_папка)
#    os.system(f'zip -qr {job.folder}/distro_zip.zip {исходная_папка}/*')
#    job.log(f'zip -qr {job.folder}/distro_zip.zip {исходная_папка}/*')


def make_archive(job, output_filename, source_dir):
    relroot = os.path.abspath(source_dir)
    with zipf.ZipFile(output_filename, "w", zipf.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir, topdown=False):
            #job.log(f'{root} {dirs} {files}')
            #zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    pos = arcname.find('/')
                    DIR = arcname[:pos]
                    if DIR != 'src':
                        #job.log(arcname)
                        zip.write(filename, arcname)
                    else:
                        #job.log(f'SKIP {arcname}')
                        pass

'''

def создание_дистрибутива(job, дистрибутив, рабочая_папка):
    correction_times(job, рабочая_папка)
    make_archive(дистрибутив, рабочая_папка)
    создать_zip_файл(job, дистрибутив + '_new', рабочая_папка)
    job.log(f'Создание дистрибутива "{дистрибутив}"')


def публикация(job, дистрибутив, product, версия):
    data = {'product_id':str(product), 'version_id':str(версия)}
    url = 'http://rs.domino.ru:88/api/product/upload'
    files = {'file' : (дистрибутив, open(дистрибутив, 'rb'), 'multipart/form-data')}
    r = requests.post(url, data=data, files=files)
    if r.status_code != 200:
        msg = 'HTTP Error {0} : {1}'.format(r.status_code, r.text)
        raise Exception(msg)
    job.log(f'Публикация "{url}"')

def последняя_версия_продукта(product):
    последняя_версия = None
    for name in os.listdir(f'/DOMINO/products/{product}'):
        try:
            версия = Version.parse(name)
            if версия is not None and версия.is_draft:
                if последняя_версия is None or последняя_версия < версия:
                    последняя_версия = версия
        except:
            pass
    return последняя_версия

def создать_и_опубликовать(job, product, версия):
    if версия is None:
        версия = последняя_версия_продукта(product)
    if версия is None:
        job.error(f'Не найдено последней версии продукта "{product}"')
    job.log(f'СОЗДАНИЕ НОВОЙ СБОРКИ "{product}.{версия}"')

    папка_версии = f'/DOMINO/products/{product}/{версия}'
    if not os.path.isdir(папка_версии):
        job.error(f"Не обнаружено папки для {product}.{версия}")

    рабочая_папка = os.path.join(job.folder, 'next_release_folder')
    shutil.copytree(папка_версии, рабочая_папка, symlinks=True)
    job.log(f'Копирование : "{папка_версии}" => "{рабочая_папка}"')

    дистрибутив = os.path.join(job.folder, f'{product}.zip')
    создание_дистрибутива(job, дистрибутив, рабочая_папка)
    публикация(job, дистрибутив, product, версия)
'''
class TheJob(Proc.Job):
    def __init__(self, ID):
        super().__init__(ID)

    
    def __call__(self):
        info = Proc.Job.get_info(self.ID)
        self.version = info.get('version')
        self.product = info.get('product')
        if self.version is None or self.product is None:
            self.error(f'Не задано продукта или версии')

        #if версия is None:
        #    версия = последняя_версия_продукта(product)
        #if версия is None:
        #    job.error(f'Не найдено последней версии продукта "{product}"')
        self.log(f'СОЗДАНИЕ НОВОЙ СБОРКИ "{self.product}.{self.version}"')

        self.version_folder = os.path.join(DOMINO_ROOT, 'products', self.product, self.version)
        if not os.path.isdir(self.version_folder):
            job.error(f"Не обнаружено папки для {self.product}.{self.version}")

        self.work_folder = os.path.join(self.folder, 'next_release_folder')
        shutil.copytree(self.version_folder, self.work_folder, symlinks=False, ignore=self.ignore_src)
        self.log(f'Копирование : "{self.version_folder}" => "{self.work_folder}"')

        self.correction_times(self.work_folder)

        self.дистрибутив = os.path.join(self.folder, f'{self.product}.zip')

        # создание zip файла
        #FOLDER = os.path.abspath(self.work_folder)
        #os.system(f'zip -qr {self.folder}/{self.product}.zip {FOLDER}/*')
        #self.log(f'zip -qr {self.folder}/{self.product}.zip {FOLDER}/*')

        make_archive(self, self.дистрибутив, self.work_folder)
        #создать_zip_файл(f'{self.дистрибутив}_new', self.work_folder)
        #job.log(f'Создание дистрибутива "{self.дистрибутив}"')

        # публикация
        data = {'product_id':str(self.product), 'version_id':str(self.version)}
        url = 'http://rs.domino.ru:88/api/product/upload'
        files = {'file' : (self.дистрибутив, open(self.дистрибутив, 'rb'), 'multipart/form-data')}
        r = requests.post(url, data=data, files=files)
        if r.status_code != 200:
            msg = 'HTTP Error {0} : {1}'.format(r.status_code, r.text)
            self.error(msg)
        self.log(f'Публикация "{url}"')

    def ignore_src(self, dir, content):
        #self.log(f'{dir} {content}')
        if dir == os.path.join(self.version_folder, 'src'):
            return content
        else:
            return []

    def correction_times(self, PathForBackup):
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
                self.correction_times(path)

if  __name__ ==  "__main__" :
    log.debug(f'{__name__} {sys.argv}')
    try:
        with TheJob(sys.argv[1]) as job:
            job()
    except:
        log.exception(__name__)

