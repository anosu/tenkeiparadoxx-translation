import sys
from pathlib import Path
from typing import Literal

import httpx

from tenkeiparadox import ScriptDownloader

client = httpx.Client()
current_dir = Path(sys.argv[0]).resolve().parent
scene_dir = current_dir.joinpath("scenes")


def get_input_token():
    token = input("输入Token: ")
    if not token:
        print("Token不能为空")
        sys.exit(1)
    return token


def get_existed(type: Literal["names", "titles", "scenes"]):
    resp = client.get(f"https://tenkeiparadox.ntr.best/existed/{type}")
    resp.raise_for_status()
    return set(resp.json())


def main():
    token = get_input_token()
    existed_names = get_existed("names")
    existed_titles = get_existed("titles")
    existed_scenes = get_existed("scenes")

    print(
        f"已有翻译数量: 人名({len(existed_names)}), 标题({len(existed_titles)}), 剧本({len(existed_scenes)})"
    )

    def exists(downloader: ScriptDownloader, asset_id: str | int) -> bool:
        return str(asset_id) in existed_scenes

    downloader = ScriptDownloader(token)
    downloader.init_user()
    downloader.init_master()
    downloader.download(scene_dir, exist_func=exists)
    downloader.generate_names(scene_dir, existed_names=existed_names)
    downloader.generate_titles(existed_titles=existed_titles)

    input("按Enter键退出...")


if __name__ == "__main__":
    main()
