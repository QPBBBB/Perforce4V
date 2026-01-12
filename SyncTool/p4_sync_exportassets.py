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


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="同步 ver_0.01 到 release")
    parser.add_argument(
        "--path",
        help="要同步的单个相对路径（相对于工作区根目录）"
    )
    args = parser.parse_args()

    if args.path:
        print(get_release_path(args.path))
        sync_ver001_to_release(args.path)
    else:
        paths_to_submit = [
            r"unity_project\Assets\Res_Export\Environment",
            r"unity_project\Assets\Res_Export\DissolveLevel",
            r"unity_project\Assets\Res_Export\HLOD",
            r"unity_project\Assets\Res_Export\MaterialEffect",
            r"unity_project\Assets\Res_Export\Texture",
            r"unity_project\Assets\Res_Export\XRenderMeshData",
            r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Temple_01",
            r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Roguelike_PVE",
            r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_PhotoStudio_Main",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level0",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level1",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level2",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level3",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level11",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level12",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level13",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level21",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level22",
            r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level23",
            r"unity_project\AssetsExtra\raw\XGIProbe",
            r"unity_project\AssetsExtra\raw\config",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level0",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level1",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level2",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level3",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level11",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level12",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level13",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level21",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level22",
            r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level23"
        ]

        for p in paths_to_submit:
            print(get_release_path(p))
            sync_ver001_to_release(p)
