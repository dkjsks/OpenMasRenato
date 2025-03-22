from os import rename, remove
from shutil import copy2
from subprocess import Popen
from sys import exit


def copy_new(disk):  # As Old
    copy2(f'{disk}MasRenato/MasRenato.exe', './MasRenato-new.exe')
    Popen('./MasRenato-new.exe --rename-old')
    exit()


def rename_old():  # As New
    rename('./MasRenato.exe', './MasRenato-old.exe')
    Popen('./MasRenato-new.exe --rename-new')
    exit()


def rename_new():  # As Old
    rename('./MasRenato-new.exe', './MasRenato.exe')
    Popen('./MasRenato.exe --remove-old')
    exit()


def remove_old():
    remove('./MasRenato-old.exe')