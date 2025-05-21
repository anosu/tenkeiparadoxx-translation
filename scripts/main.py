import sys

from pathlib import Path

import httpx

from tenkeiparadox.downloader import ScriptDownloader

current_dir = Path(sys.argv[0]).resolve().parent


def merge():
    src = Path(r"E:\Quick Access\Downloads\transl_cache")
    dst = current_dir.parent / "translation" / "scenes"
    cache_file: Path
    for cache_file in src.iterdir():
        data = ScriptDownloader.read_json(cache_file)
        result = {cache["pre_jp"]: cache["post_zh_preview"] for cache in data}
        out_path = dst / cache_file.stem / "zh_Hans.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ScriptDownloader.write_json(out_path, result)


def main():
    token = "Bearer token"
    download_scenes_dir = Path("scenes")
    # translation_dir = current_dir.parent / "translation"
    # translation_scenes_dir = translation_dir / "scenes"
    # translation_names_path = translation_dir / "names/zh_Hans.json"
    # translation_titles_path = translation_dir / "titles/zh_Hans.json"

    # 从本地文件查重
    # def exists(downloader: ScriptDownloader, asset_id: str | int) -> bool:
    #     translated_dir = translation_scenes_dir / str(asset_id)
    #     downloaded_path = download_scenes_dir / f"{asset_id}.json"
    #     return translated_dir.exists() or downloaded_path.exists()

    # 从接口查重
    existed_scenes = set(
        httpx.get("https://tenkeiparadox.ntr.best/existed/scenes").json()
    )

    def exists(downloader: ScriptDownloader, asset_id: str | int) -> bool:
        return str(asset_id) in existed_scenes

    downloader = ScriptDownloader(token)
    downloader.init_user()
    downloader.init_master()
    downloader.download(scene_dir=download_scenes_dir, exist_func=exists)
    downloader.generate_names(scene_dir=download_scenes_dir)
    # downloader.generate_titles(path=translation_titles_path)


if __name__ == "__main__":
    main()
