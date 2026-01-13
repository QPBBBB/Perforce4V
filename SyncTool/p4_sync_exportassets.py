import os
import subprocess
import sys

from clear_asset import clear_asset
from copy_asset import copy_asset
from clear_folder import clear_folder
from copy_folder import copy_folder
from p4_reconcile import p4_reconcile, create_changelist
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

def p4_reconcile_multi(paths: list, workspace: str) -> str:
    changelist_num = create_changelist("p4-bypass p4-admin-bypass 001 to release", workspace)
    for path in paths:
        local_path = set_asset_directory(path)
        print(f"Reconcile: {local_path}")
        result = subprocess.run([
            P4, "-c", workspace, "reconcile", "-c", changelist_num, local_path
        ], capture_output=True, text=True, env=os.environ)
        print(result.stdout)
        print(result.stderr)
    return changelist_num



def is_unity_folder(path: str) -> bool:
    path = os.path.normpath(path)
    name = os.path.basename(path)
    if os.path.exists(path):
        return os.path.isdir(path)
    return "." not in name

# ---------------- Merge Logic ---------------- #

def sync_ver001_to_release(target_path: str,  submit: bool = True, one: bool = False, changelist_num: str = None) -> str:
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

    # Reconcile
    changelist_num = p4_reconcile(release_path, RELEASE_WORKSPACE, one, changelist_num)
    if submit:
        p4_submit("release", changelist_num, RELEASE_WORKSPACE)
    else:
        return release_path
    print(target_folder)
    return changelist_num

import argparse

def is_valid_path(path: str) -> bool:
    return bool(path and path.strip())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="同步 ver_0.01 到 release")
    parser.add_argument("--paths", help="用英文逗号分隔的多个相对路径（相对于工作区根目录）")
    args = parser.parse_args()

    if args.paths and args.paths.strip():
        path_list = [p.strip() for p in args.paths.split(",") if p.strip()]
        if not path_list:
            print("未提供有效路径，已跳过同步。")
        else:
            os.environ["P4PORT"] = "p4-world.funplus.com.cn:1666"
            os.environ["P4USER"] = "worldx_robot"

            if RELEASE_WORKSPACE:
                os.environ["P4CLIENT"] = RELEASE_WORKSPACE
            elif not os.environ.get("P4CLIENT"):
                print("错误：未指定工作区 (--client)，且环境变量中没有 P4CLIENT。")
                sys.exit(1)
            all_release_paths = []
            changelist_num = create_changelist("p4-bypass p4-admin-bypass 001 to release", RELEASE_WORKSPACE)
            for path in path_list:
                print(get_release_path(path))
                release_path = sync_ver001_to_release(path, submit=False, one=True, changelist_num=changelist_num)
            newchangelist_num = p4_reconcile_multi(path_list,RELEASE_WORKSPACE)
            p4_submit("release", newchangelist_num, RELEASE_WORKSPACE)
    else:

        print("错误：shu输入")
    # else:
    #     paths_to_submit = [
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20001",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20002",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20003",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20005",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20006",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20007",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20010",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20011",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20012",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20013",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20014",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20015",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20016",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20017",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Random_Map_20018",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Temple_01",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_Roguelike_PVE",
    #         r"unity_project\Assets\Res\Level\LevelLayout\Level_FB_PhotoStudio_Main",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level0",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level1",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level2",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level3",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level11",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level12",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level13",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level21",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level22",
    #         r"unity_project\AssetsExtra\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level23",
    #         r"unity_project\AssetsExtra\raw\XGIProbe",
    #         r"unity_project\AssetsExtra\raw\config",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level0",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level1",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level2",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level3",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level11",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level12",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level13",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level21",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level22",
    #         r"server\SpaceRes\Voxel\Level_FB_Roguelike_PVE_BuildForTeleport_Level23"
    #         # r"unity_project\Assets\Res_Export\Texture",
    #         # r"unity_project\Assets\Res_Export\Environment",
    #         # r"unity_project\Assets\Res_Export\DissolveLevel",
    #         # r"unity_project\Assets\Res_Export\HLOD",
    #         # r"unity_project\Assets\Res_Export\MaterialEffect",
    #         # r"unity_project\Assets\Res_Export\XRenderMeshData"
    #     ]
    #
    #     for p in paths_to_submit:
    #         print(get_release_path(p))
    #         sync_ver001_to_release(p)
