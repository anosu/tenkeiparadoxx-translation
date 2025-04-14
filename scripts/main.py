from pathlib import Path
from tenkeiparadox.downloader import ScriptDownloader


def merge():
    src = Path(r"E:\Quick Access\Downloads\transl_cache")
    dst = Path(r"E:\DMM\Extract\TP\tenkeiparadoxx-translation\translation\scenes")
    cache_file: Path
    for cache_file in src.iterdir():
        data = ScriptDownloader.read_json(cache_file)
        result = {cache["pre_jp"]: cache["post_zh_preview"] for cache in data}
        out_path = dst / cache_file.stem / "zh_Hans.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ScriptDownloader.write_json(out_path, result)


def main():
    token = "Bearer xxx"
    translation_dir = Path(r"E:\DMM\Extract\TP\tenkeiparadoxx-translation\translation")
    download_scenes_dir = Path("scenes")
    translation_scenes_dir = translation_dir / "scenes"
    translation_names_path = translation_dir / "names/zh_Hans.json"
    translation_titles_path = translation_dir / "titles/zh_Hans.json"

    def exists(downloader: ScriptDownloader, asset_id: str | int) -> bool:
        translated_dir = translation_scenes_dir / str(asset_id)
        downloaded_path = download_scenes_dir / f"{asset_id}.json"
        return translated_dir.exists() or downloaded_path.exists()

    downloader = ScriptDownloader(token)
    downloader.init_user()
    downloader.init_master()
    downloader.download(scene_dir=download_scenes_dir, exist_func=exists)
    downloader.generate_names(
        scene_dir=download_scenes_dir, path=translation_names_path
    )
    downloader.generate_titles(path=translation_titles_path)


if __name__ == "__main__":
    main()
