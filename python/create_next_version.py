
import os, json, shutil, sys
import datetime, time
import xml.etree.ElementTree as ET
import zipf
import time
import requests

from domino.core import log, Version, Server
from domino.jobs import Job, JobReport
from domino.distro import Distro
from domino.globalstore import GlobalStore

# --------------------------------------------------
# Публикация
# --------------------------------------------------

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




def modify_info_json(folder, version):
    info_file = os.path.join(folder, 'info.json')
    with open(info_file) as f:    
        info = json.load(f)
    info['version'] = str(version)
    info['creation_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(info_file, 'w') as f:
        json.dump(info, f)

def modify_info_xml(folder, version) :
    xml_file = os.path.join(folder, "info.xml")
    if os.path.isfile(xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        root.set('version', version)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        root.set('creation_time', now)
        tree.write(xml_file)

def create_change_log(product, version_folder):
    pass
#    txt_file = os.path.join(Server.product_folder(product), "{0}.txt".format(product))
#    html_file = os.path.join(version_folder, "chnage_log.html")
#    if os.path.exists(txt_file):
#        with open(html_file, "w") as html, open(txt_file, 'r', encoding='cp1251') as txt:
#            html.writeline('<pre>')
#            html.write(txt.read())
#            html.writeline('</pre>')

def modify_index_html(version_folder, draft, version):
    '''
    Для продукта login в файле index.html в определенных
    местах должна быть записан номер вверсии.
    Соответственно процедура меняет бывший номер (draft) на текущий (version)
    '''
    index_html = os.path.join(version_folder, 'web', 'index.html') 
    if os.path.isfile(index_html):
        lines = []
        with open(index_html, 'r') as f:
            lines = f.readlines()
        with open(index_html, 'w' ) as f:
            from_txt = str(draft)
            to_txt = str(version)
            for line in lines:
                new_line = line.replace(from_txt, to_txt) 
                f.write(new_line)

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

def create_next_version(product, draft):
    job_name = f"Создание новой сборки {product}.{draft}"
    #print(job_name + '...')
    with Job('developer', job_name) as job:
        if draft is None:
            draft = последняя_версия_продукта(product)
        log.debug(f'Версия продукта "{product}" : "{draft}"')

        draft_folder = Server.version_folder(product, draft)
        if not os.path.isdir(draft_folder):
            job.error(f"Не обнаружено папки для {product}.{draft}")

        latest = Server.get_latest_version_of_draft(product, draft)
        if latest is None:
            next_version = draft.next()
        else:
            next_version = latest.next()
        job.log(f'Сформирован номер сборки "{next_version}"')

        next_version_folder = os.path.join(job.temp, str(next_version))
        shutil.copytree(draft_folder, next_version_folder, symlinks=True)
        create_change_log(product, next_version_folder)
        modify_info_json(next_version_folder, next_version)
        modify_info_xml(next_version_folder, next_version)
        modify_index_html(next_version_folder, draft, next_version)
        shutil.move(next_version_folder, Server.version_folder(product, next_version))
        #job.success(f"Создано {product}.{next_version}")
        #print(f'{job_name} ... создана {next_version}')

def arg(i):
    try:
        return sys.argv[i]
    except:
        return None
    
if  __name__ ==  "__main__" :
    product = arg(1) 
    version = Version.parse(arg(2))
    if product is None:
        print ('Не задан продукт')
    if version is None:
        print ('Не задана версия макета')
       
    create_next_version(product, version)

