import os
import subprocess
import sys

from clear_asset import clear_asset
from copy_asset import copy_asset
from clear_folder import clear_folder
from copy_folder import copy_folder
from p4_reconcile import p4_reconcile
from p4_submit import p4_submit
from p4_update import p4_update

# Perforce executable
P4 = r"C:\Program Files\Perforce\p4.exe"

# Workspace and depot paths
RELEASE_ROOT = r"C:\worldx_robot_HZPCC0420018_2708"
VER001_ROOT = r"C:\worldx_robot_HZPCC0420018_1001"

RELEASE_WORKSPACE = r"worldx_robot_HZPCC0420018_2708"
VER001_WORKSPACE = r"worldx_robot_HZPCC0420018_1001"

VER001_DEPOT = r"//world_x/ver_0.01"
RELEASE_DEPOT = r"//world_x/release"


# ---------------- Path Helpers ---------------- #

def get_release_path(user_path: str):
    return os.path.join(RELEASE_ROOT, user_path)


def get_ver001_path(user_path: str):
    return os.path.join(VER001_ROOT, user_path)


def get_release_depot_path(user_path: str):
    return os.path.join(RELEASE_DEPOT, user_path)


def get_ver001_depot_path(user_path: str):
    return os.path.join(VER001_DEPOT, user_path)

def get_asset_directory(asset_path: str) -> str:
    asset_path = os.path.normpath(asset_path)
    return os.path.dirname(asset_path)

def set_asset_directory(asset_path: str) -> str:
    asset_path = asset_path.replace("\\", "/")
    if asset_path.endswith("..."):
        return asset_path
    if asset_path.endswith("/"):
        return asset_path + "..."
    return asset_path + "/..."


def is_unity_folder(path: str) -> bool:
    path = os.path.normpath(path)
    name = os.path.basename(path)
    if os.path.exists(path):
        return os.path.isdir(path)
    return "." not in name

# ---------------- Merge Logic ---------------- #

def sync_ver001_to_release(target_path: str):
    target_folder = target_path
    if not is_unity_folder(get_ver001_path(target_path)):
        target_folder = get_asset_directory(target_path)

    ver001_path = get_ver001_path(target_folder)
    release_path = get_release_path(target_folder)

    ver001_depot = get_ver001_depot_path(target_folder)
    release_depot = get_release_depot_path(target_folder)

    # Update both workspaces
    if not is_unity_folder(get_ver001_path(target_path)):
        p4_update(set_asset_directory(ver001_depot), VER001_WORKSPACE)
        p4_update(set_asset_directory(release_depot), RELEASE_WORKSPACE)
        print("001:" + set_asset_directory(ver001_depot))
        print("rls:" + set_asset_directory(release_depot))
    else:
        p4_update(set_asset_directory(ver001_depot), VER001_WORKSPACE)
        p4_update(set_asset_directory(release_depot), RELEASE_WORKSPACE)
    # Edit release folder
    subprocess.run([P4, "edit", release_path + "/..."], env=os.environ)

    if not is_unity_folder(get_ver001_path(target_path)):
        clear_asset(get_release_path(target_path))
    else:
        clear_folder(release_path)

    # Edit ver001 folder
    subprocess.run([P4, "edit", ver001_path + "/..."], env=os.environ)

    if not is_unity_folder(get_ver001_path(target_path)):
        copy_asset(get_ver001_path(target_path),get_release_path(target_path))
    else:
        copy_folder(ver001_path, release_path)

    # Reconcile and submit
    changelist_num = p4_reconcile(release_path, RELEASE_WORKSPACE)

    p4_submit("release", changelist_num, RELEASE_WORKSPACE)

    print(target_folder)
    return changelist_num


# ---------------- Main Entry ---------------- #

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No args, continue...")
    paths_to_submit = [ r"unity_project\Assets\Res_Export\Environment",
                        r"unity_project\Assets\Res_Export\HLOD",
                        r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Temple_01",
                        r"unity_project\AssetsExtra\raw\config\XRendererEffectData.bytes"]

    for p in paths_to_submit:
        print(get_release_path(p))
        sync_ver001_to_release(p)