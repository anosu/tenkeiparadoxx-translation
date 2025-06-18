import json
from pathlib import Path
from itertools import chain
from typing import Callable
from dataclasses import dataclass

from .serialize import deserialize, deserialize_master
from .master import (
    Code,
    CharacterMaster,
    EventMaster,
    LocationMaster,
    LocationNodeMaster,
    EpisodeMaster,
    CharacterEpisodeMaster,
    PaidEpisodeMaster,
)

from .client import TenkeiparadoxClient


@dataclass
class MasterData:
    Character: dict[int, CharacterMaster]
    Event: dict[int, EventMaster]
    Location: dict[int, LocationMaster]
    LocationNode: dict[int, LocationNodeMaster]
    Episode: dict[int, EpisodeMaster]
    CharacterEpisode: dict[int, CharacterEpisodeMaster]
    PaidEpisode: dict[int, PaidEpisodeMaster]


@dataclass
class UserData:
    LocationNode: set[int]
    CharacterEpisode: set[int]
    PaidEpisode: set[int]


class ScriptDownloader(TenkeiparadoxClient):
    API_PATH: dict[str, str] = {
        "LocationNode": "Episodes/Quest/{}/getDetails",
        "CharacterEpisode": "Episodes/Character/{}/getDetails",
        "PaidEpisode": "Episodes/{}/getPaidEpisodeDetails",
    }

    user: UserData | None
    master: MasterData | None

    @staticmethod
    def read_json(file_path: str | Path):
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: str | Path, data):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def parse(script: list):
        episode_id: str = script[0]
        details: list[list] = script[4]
        result: list[dict[str, str]] = []
        for frame_detail in details:
            name: str = frame_detail[10]
            message: str = frame_detail[12]
            if name is None and message is None:
                continue
            result.append(
                {
                    "name": name.replace("%username%", "皇子") if name else "",
                    "message": message or "",
                }
            )
        return episode_id, result

    def __init__(self, token: str):
        super().__init__(token)
        self.user = None
        self.master = None

    def init_master(self):
        print("Fetching master data...")

        path, ver = self.get_master()
        resp = self.session.get(f"{self.MASTER_BASE_URL}/{path}")
        resp.raise_for_status()
        master, version = deserialize_master(resp.content)
        self.master = MasterData(
            {e.Id: e for e in master[Code.CharacterMaster]},
            {e.Id: e for e in master[Code.EventMaster]},
            {e.Id: e for e in master[Code.LocationMaster]},
            {e.Id: e for e in master[Code.LocationNodeMaster]},
            {e.Id: e for e in master[Code.EpisodeMaster]},
            {e.Id: e for e in master[Code.CharacterEpisodeMaster]},
            {e.Id: e for e in master[Code.PaidEpisodeMaster]},
        )
        episodes = self.master.Episode.values()
        print(f"Total master location nodes: {len(self.master.LocationNode)}")
        print(f"Total master character episodes: {len(self.master.CharacterEpisode)}")
        print(f"Total master paid episodes: {len(self.master.PaidEpisode)}")
        print(f"Total master episodes: {len(self.master.Episode)}")
        print(
            f"Total scene assets: {sum(len(e.SceneAssetIds + e.AdultSceneAssetIds) for e in episodes)}"
        )

        print("-" * 50)

    def init_user(self):
        print("Fetching user data...")

        resp = self.request("GET", "data/user")
        resp.raise_for_status()
        result = resp.json()["result"]
        location_nodes: set[int] = set()
        character_episodes: set[int] = set()
        paid_episodes: set[int] = set()
        for data in result:
            match data[0]:
                case 22:
                    location_nodes.add(data[1][1])
                case 34:
                    character_episodes.add(data[1][1])
                case 146:
                    paid_episodes.add(data[1][1])
                case _:
                    pass
        self.user = UserData(location_nodes, character_episodes, paid_episodes)
        print(f"Total user location nodes: {len(self.user.LocationNode)}")
        print(f"Total user character episodes: {len(self.user.CharacterEpisode)}")
        print(f"Total user paid episodes: {len(self.user.PaidEpisode)}")

        print("-" * 50)

    def download(
        self,
        scene_dir: str | Path = "scenes",
        exist_func: Callable[["ScriptDownloader", str | int], bool] = None,
        try_all: bool = False,
    ):
        if try_all:
            print("尝试下载所有剧情: 已启用")

        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)

        def _exists(downloader, asset_id: str | int) -> bool:
            return (scene_dir / f"{asset_id}.json").exists()

        exists = exist_func if exist_func else _exists

        master_ln = self.master.LocationNode.values()
        master_ce = self.master.CharacterEpisode.values()
        master_pe = self.master.PaidEpisode.values()

        missing_episodes: dict[tuple[str, int], list[int]] = {}
        user_owned_episodes: list[tuple[str, int]] = []
        for obj in filter(
            lambda x: x.EpisodeMasterId, chain(master_ln, master_ce, master_pe)
        ):
            episode_master = self.master.Episode[obj.EpisodeMasterId]
            scene_asset_ids = (
                episode_master.SceneAssetIds + episode_master.AdultSceneAssetIds
            )
            missing_assets = [
                int(asset_id)
                for asset_id in scene_asset_ids
                if not exists(self, asset_id)
            ]
            if not missing_assets:
                continue

            episode_type = type(obj).__name__.replace("Master", "")
            episode_ientity = (episode_type, obj.Id)
            missing_episodes[episode_ientity] = missing_assets
            if obj.Id in getattr(self.user, episode_type):
                user_owned_episodes.append(episode_ientity)

        print(f"缺失的剧情: {len(missing_episodes)}")
        for (episode_type, master_id), assets in missing_episodes.items():
            print(f"Type: {episode_type}, ID: {master_id}, Assets: {assets}")
        print("-" * 50)

        print(f"用户拥有的剧情: {len(user_owned_episodes)}")
        for episode_type, master_id in user_owned_episodes:
            print(f"Type: {episode_type}, ID: {master_id}")
        print("-" * 50)

        print("Starting download...")

        data_obj: LocationNodeMaster | CharacterEpisodeMaster | PaidEpisodeMaster
        for episode_type, master_id in (
            missing_episodes if try_all else user_owned_episodes
        ):
            data_obj = getattr(self.master, episode_type)[master_id]

            resp = self.request(
                "POST", self.API_PATH[episode_type].format(data_obj.Id)
            ).json()

            if errors := resp["errors"]:
                if episode_type == "CharacterEpisode":
                    character = self.master.Character[data_obj.CharacterMasterId]
                    message = f"Character: {character.AnotherName}{character.Name}"
                elif episode_type == "LocationNode":
                    location = self.master.Location[data_obj.LocationMasterId]
                    event = self.master.Event[location.EventMasterId]
                    message = f"Event: {event.Name} - {location.Name}"
                else:
                    episode = self.master.Episode[data_obj.EpisodeMasterId]
                    message = f"Episode: {episode.EpisodeOrderName} - {episode.Title}"
                print(f"Error: {errors[0][0]}, {errors[0][1]} {message}")
                continue

            scene_details: list[tuple[int, str]] = resp["result"][2]

            for sid, path in scene_details:
                if exists(self, sid):
                    continue
                scene_data = self.session.get(f"{self.MASTER_BASE_URL}/{path}")
                scene_data.raise_for_status()
                sid, data = self.parse(deserialize(scene_data.content))
                if len(data) == 1 and data[0]["message"] == "仮":
                    continue
                self.write_json(scene_dir / f"{sid}.json", data)
                print(f"Saved => Type: {episode_type}, AssetID: {sid}")

        print("Download complete")
        print("-" * 50)

    def generate_names(
        self,
        scene_dir: str | Path = "scenes",
        save_path: str | Path = "names.json",
        existed_names: dict[str, str] | None = None,
    ):
        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)
        existed_names = existed_names or {}

        result: dict[str, str] = {
            name: ""
            for file in scene_dir.rglob("*.json")
            for name in set(i.get("name") for i in self.read_json(file))
            if name and name not in existed_names
        }

        if len(result) == 0:
            print("No new names found")
        else:
            self.write_json(save_path, result)
            print("Names generated")

        print("-" * 50)

    def generate_titles(
        self,
        save_path: str | Path = "titles_gtl.json",
        existed_titles: dict[str, str] | None = None,
    ):
        existed_titles = existed_titles or {}

        result: list[dict[str, str]] = [
            {"message": episode.Title}
            for episode in self.master.Episode.values()
            if episode.Title and episode.Title not in existed_titles
        ]

        if len(result) == 0:
            print("No new titles found")
        else:
            self.write_json(save_path, result)
            print("Titles generated")

        print("-" * 50)
