import os
import subprocess
import sys

from clear_folder import clear_folder
from copy_folder import copy_folder
from p4_reconcile import p4_reconcile
from p4_submit import p4_submit
from p4_update import p4_update

P4 = r"C:\Program Files\Perforce\p4.exe"

# ✅ 在这里提前写好路径，只写一次
RELEASE_ROOT = r"C:\worldx_robot_HZPCC0420018_2708"
VER001_ROOT = r"C:\worldx_robot_HZPCC0420018_1001"
RELEASE_WORLDSPACE = r"worldx_robot_HZPCC0420018_2708"
VER001_WORLDSPACE = r"worldx_robot_HZPCC0420018_1001"
RELEASE_DEPOT = r"//world_x/ver_0.01"
VER001_DEPOT = r"//world_x/release"


def getreleasepath(user_path: str):
    return os.path.join(RELEASE_ROOT, user_path)


def getver001path(user_path: str):
    return os.path.join(VER001_ROOT, user_path)


def getreleasedepot(user_path: str):
    return os.path.join(RELEASE_DEPOT, user_path)


def getver001pdepot(user_path: str):
    return os.path.join(VER001_DEPOT, user_path)


def mergever001torelease(target_folder: str):
    ver001path = getver001path(target_folder)
    releasepath = getreleasepath(target_folder)
    ver001depot = getreleasedepot(target_folder)
    releasedepot = getreleasedepot(target_folder)

    p4_update(ver001depot, VER001_WORLDSPACE)
    p4_update(releasedepot, RELEASE_WORLDSPACE)

    subprocess.run([P4, "edit", releasepath + "/..."])
    clear_folder(releasepath)
    subprocess.run([P4, "edit", ver001path + "/..."])
    copy_folder(ver001path, releasepath)

    changelistnum = p4_reconcile(releasepath, RELEASE_WORLDSPACE)

    # p4_submit("release", changelistnum, RELEASE_WORLDSPACE)

    pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python clear_folder.py <文件夹路径>")
        sys.exit(1)

    target_folder = sys.argv[1]
    mergever001torelease(target_folder)
    print(getreleasepath(target_folder))
