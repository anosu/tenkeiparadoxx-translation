import json
from pathlib import Path
from itertools import chain
from typing import Callable
from dataclasses import dataclass

from .serialize import deserialize
from .master import (
    Code,
    deserialize_master,
    CharacterMaster,
    EventMaster,
    LocationMaster,
    LocationNodeMaster,
    EpisodeMaster,
    CharacterEpisodeMaster,
    PaidEpisodeMaster,
)

from .client import TenkeiparadoxClient

BASE_URL = "https://cdne-paripari-prod.tenkei-paradox.com/master-data"


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
        "LocationNodeMaster": "Episodes/Quest/{}/getDetails",
        "CharacterEpisodeMaster": "Episodes/Character/{}/getDetails",
        "PaidEpisodeMaster": "Episodes/{}/getPaidEpisodeDetails",
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
        result = []
        for frame_detail in details:
            name: str = frame_detail[10]
            message: str = frame_detail[12]
            if name is None and message is None:
                continue
            result.append(
                {
                    "name": name.replace("%username%", "皇子") if name else "",
                    "message": message if message else "",
                }
            )
        return episode_id, result

    def __init__(self, token: str):
        super().__init__(token)
        self.user = None
        self.master = None

        try:
            self.scenes = self.read_json("scenes.json")
        except:
            self.scenes = {}

    def login(self, token: str = None):
        if token:
            self.token = token
        else:
            super().login()

    def init_master(self):
        print("Requesting master data...")
        path, ver = self.get_master()
        data = self.session.get(f"{self.MASTER_BASE_URL}/{path}")
        master, version = deserialize_master(data.content)
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
        print("Requesting user data...")
        resp = self.request("GET", "data/user")
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
    ):
        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)

        def _exists(downloader, asset_id: str | int) -> bool:
            return (scene_dir / f"{asset_id}.json").exists()

        exists = exist_func if exist_func else _exists

        user_ln = self.user.LocationNode
        user_ce = self.user.CharacterEpisode
        user_pe = self.user.PaidEpisode
        master_ln = self.master.LocationNode.values()
        master_ce = self.master.CharacterEpisode.values()
        master_pe = self.master.PaidEpisode.values()

        # 仅读取用户已有的剧情
        # ------------------------------------
        owned_ln = filter(lambda x: x.Id in user_ln and x.EpisodeMasterId, master_ln)
        owned_ce = filter(lambda x: x.Id in user_ce and x.EpisodeMasterId, master_ce)
        owned_pe = filter(lambda x: x.Id in user_pe and x.EpisodeMasterId, master_pe)
        # ------------------------------------

        # 尝试读取所有活动、主线和角色剧情
        # ------------------------------------
        # owned_ln = filter(lambda x: x.EpisodeMasterId, master_ln)
        # owned_ce = filter(lambda x: x.EpisodeMasterId, master_ce)
        # owned_pe = filter(lambda x: x.EpisodeMasterId, master_pe)
        # ------------------------------------

        print("Starting download...")

        data_obj: LocationNodeMaster | CharacterEpisodeMaster | PaidEpisodeMaster
        for data_obj in chain(owned_ln, owned_ce, owned_pe):
            episode_master = self.master.Episode[data_obj.EpisodeMasterId]
            scene_asset_ids = (
                episode_master.SceneAssetIds + episode_master.AdultSceneAssetIds
            )
            if all(exists(self, asset_id) for asset_id in scene_asset_ids):
                continue

            episode_type = type(data_obj).__name__

            resp = self.request(
                "POST", self.API_PATH[episode_type].format(data_obj.Id)
            ).json()

            if errors := resp["errors"]:
                if episode_type == "CharacterEpisodeMaster":
                    character = self.master.Character[data_obj.CharacterMasterId]
                    message = f"Character: {character.AnotherName}{character.Name}"
                elif episode_type == "LocationNodeMaster":
                    location = self.master.Location[data_obj.LocationMasterId]
                    event = self.master.Event[location.EventMasterId]
                    message = f"Event: {event.Name} - {location.Name}"
                else:
                    episode = self.master.Episode[data_obj.EpisodeMasterId]
                    message = f"Episode: {episode.EpisodeOrderName} - {episode.Title}"
                print(f"Error: {errors[0][0]}, {errors[0][1]} {message}")
                print(data_obj)
                continue

            scene_details: list[tuple[int, str]] = resp["result"][2]

            for sid, path in scene_details:
                self.scenes[str(sid)] = path
                if exists(self, sid):
                    continue
                scene_data = self.session.get(f"{self.MASTER_BASE_URL}/{path}")
                sid, data = self.parse(deserialize(scene_data.content))
                if len(data) == 1 and data[0]["message"] == "仮":
                    continue
                self.write_json(scene_dir / f"{sid}.json", data)
                print(f"Saved => Type: {episode_type}, AssetID: {sid}")

            self.write_json("scenes.json", self.scenes)

        print("Download complete")
        print("-" * 50)

    def generate_names(
        self, scene_dir: str | Path = "scenes", path: str | Path = "names.json"
    ):
        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)
        names = self.read_json(path) if Path(path).exists() else {}
        for file in scene_dir.rglob("*.json"):
            data = self.read_json(file)
            for name in set(i.get("name") for i in data):
                if not name or name in names:
                    continue
                names[name] = ""
        self.write_json(path, names)

        print("Names generated")
        print("-" * 50)

    def generate_titles(self, path: str | Path = "titles.json"):
        try:
            titles = self.read_json(path)
        except:
            titles = {}
        for episode in self.master.Episode.values():
            if episode.Title in titles:
                continue
            titles[episode.Title] = ""
        self.write_json(path, titles)

        if new_titles := [{"message": o} for o, t in titles.items() if o and not t]:
            self.write_json("titles_gtl.json", new_titles)

        print("Titles generated")
        print("-" * 50)
