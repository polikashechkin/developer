#!/usr/bin/python3.6
import sys, os, shutil, json
#os.chdir(os.dirname(__file__))

from domino.core import log, Version, Server, ProductInfo, VersionInfo, DOMINO_ROOT
from domino.jobs import Job, Задача
from domino.globalstore import GlobalStore
from domino.cli import Console, print_error, print_comment, print_warning, print_help

def arg(n):
    try:
        return sys.argv[n].lower()
    except:
        return None

class PRODUCT:
    @staticmethod 
    def create(product):
        draft = max(Server.get_drafts('domino'))
        product_folder = Server.product_folder(product)
        version_folder = Server.version_folder(product, draft)
        os.makedirs(version_folder, exist_ok=True)
        os.makedirs(os.path.join(version_folder, 'web'), exist_ok=True)
        os.makedirs(os.path.join(version_folder, 'python'), exist_ok=True)

        with open(os.path.join(product_folder, 'info.json'), 'w') as f:
            json.dump({'id':product},f)

        info = VersionInfo()
        info.version = draft
        info.product = product
        info.write(version_folder)

        #manifest = {'', 'products' : []}

def help():
    print(os.path.abspath(__file__))
    print('')
    print('product.create\tСоздание нового продукта')
    print('')

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

def hard_link(file_name, common_folder, product_folder):
    common_file = os.path.join(common_folder, file_name)
    product_file = os.path.join(product_folder, file_name)
    if not os.path.isfile(common_file):
        print_warning(f'Нет файла "{common_file}"')
        return
    os.makedirs(os.path.dirname(product_file), exist_ok=True)
    if os.path.isfile(product_file):
        os.remove(product_file)
    os.link(common_file, product_file)
    print_help(file_name)
    print_comment(f'{common_file} => {product_file}')

def copy_folder(product, draft, folder):
    draft = f'{draft}'
    product_dir = os.path.join(DOMINO_ROOT, 'products', product, f'{draft}', 'python', 'domino', folder)
    common_dir = os.path.join(DOMINO_ROOT,'products','_system','python', folder)
    for name0 in os.listdir(common_dir):
        dir0 = os.path.join(common_dir, name0)
        if os.path.isdir(dir0):
            for name1 in os.listdir(dir0):
                dir1 = os.path.join(dir0, name1)
                if os.path.isdir(dir1):
                    for name2 in os.listdir(dir1):
                        dir2 = os.path.join(dir1, name2)
                        if os.path.isdir(dir2):
                            pass
                        else:
                            hard_link(os.path.join(name0, name1, name2), common_dir, product_dir)
                else:
                    hard_link(os.path.join(name0, name1), common_dir, product_dir)
        else:
            hard_link(name0, common_dir, product_dir)
    
if __name__ == "__main__":
    dir = os.path.dirname(os.path.abspath(__file__))
    gs = GlobalStore()
    action = arg(1)
    if action is None:
        help()

    elif action == 'create_next':
        product = arg(2)
        #draft = max(Server.get_drafts(product), default = None)
        draft = последняя_версия_продукта(product)
        if draft is None:
            raise Exception(f'Не найдено последней версии продукта "{product}"')
        #if draft is None:
        #    print (f'Не найдено рабочего макета для "{product}"')
        proc = os.path.join(dir, 'create_next_version.py')
        os.system(f'python3.6 {proc} {product} {draft}')

    elif action == 'download':
        path = arg(2)
        file = arg(3)
        if file is None:
            file = os.path.basename(path)
        gs.download(path, file)

    elif action == 'upload':
        gs.upload(arg(2), arg(3))
    elif action == 'upload_distro':
        gs.upload_distro(arg(2), arg(3), arg(4))
    elif action == 'listdir':
        for name in gs.listdir(arg(2)):
            print(name)
    elif action == 'get_versions':
        for version in gs.get_versions(arg(2)):
            print(version.id)
    elif action == 'download_distro':
        gs.download_distro(arg(2), arg(3), arg(4))

    elif action == 'include':
        c = Console()
        product = arg(2)
        if product is None:
            print_warning('Формат вызова: domino include <продукт> <модуль>')
            print_warning('  <модуль> := <имя модуля> | domino | templates | exists > ')
            sys.exit()
        module = arg(3)
        if module is None:
            c.error(f'Не задан модуль')
            sys.exit()
        else:
            print_comment(f'{module}')

        product_draft = max(Server.get_drafts(product), default = None)
        if product_draft is None:
            c.error(f'Нет макета для "{product}"')

        print_comment(f'{product}.{product_draft}')

        filenames = []
        # определение директорй
        if module == 'templates':
            product_folder = f'/DOMINO/products/{product}/{product_draft}/python/templates'
            common_folder = '/DOMINO/products/_system/python/templates'
            # определение списка файлов
            for filename in os.listdir(common_folder):
                filenames.append(filename)

        elif module == 'tables':
            product_folder = f'/DOMINO/products/{product}/{product_draft}/python/domino/tables'
            common_folder = '/DOMINO/products/_system/python/tables'
            for database_name in os.listdir(common_folder):
                database_folder = os.path.join(common_folder, database_name)
                if os.path.isdir(database_folder):
                    for table_name in os.listdir(database_folder):
                        hard_link(os.path.join(database_name, table_name), common_folder, product_folder)

        elif module in ['components', 'responses', 'pages', 'databases', 'dicts', 'enums']:
            copy_folder(product, product_draft, module)

        elif module == 'all':
            for module in ['components', 'responses', 'pages', 'databases', 'dicts', 'enums', 'tables']:
                copy_folder(product, product_draft, module)

        elif module == 'domino':
            product_folder = f'/DOMINO/products/{product}/{product_draft}/python/domino'
            common_folder = '/DOMINO/products/_system/python/domino'
            for filename in os.listdir(common_folder):
                filenames.append(filename)
        else:
            product_folder = f'/DOMINO/products/{product}/{product_draft}/python/domino'
            common_folder = '/DOMINO/products/_system/python/domino'
            # определение списка файлов
            if module == 'exists':
                filenames = os.listdir(product_folder)
            else:
                for filename in os.listdir(common_folder):
                    #print(filename)
                    if filename.startswith(module):
                        filenames.append(filename)
                for address, dirs, files in os.walk(common_folder):
                    print('------------')
                    print(address, dirs, files)

        #print(f'From "{common_folder}"')
        #print(f'To "{product_folder}"')
        #print(f'{filenames}')
        #print(f'{filenames}')
        for filename in filenames:
            hard_link(filename, common_folder, product_folder)

    else:
        print(f'Неизвестная команда {action}')
