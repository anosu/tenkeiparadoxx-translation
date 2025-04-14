import json
from pathlib import Path
from itertools import chain
from typing import Callable

from serialize import deserialize
from master import (
    Code,
    deserialize_master,
    LocationNodeMaster,
    EpisodeMaster,
    CharacterEpisodeMaster
)

from client import TenkeiparadoxClient

BASE_URL = 'https://cdne-paripari-prod.tenkei-paradox.com/master-data'


class MasterData:
    LocationNode: dict[int, LocationNodeMaster]
    Episode: dict[int, EpisodeMaster]
    CharacterEpisode: dict[int, CharacterEpisodeMaster]

    def __init__(self, location_node=None, episode=None, character_episode=None):
        self.LocationNode = location_node
        self.Episode = episode
        self.CharacterEpisode = character_episode


class UserData:
    LocationNode: set[int]
    CharacterEpisode: set[int]

    def __init__(self, location_node=None, character_episode=None):
        self.LocationNode = location_node
        self.CharacterEpisode = character_episode


class ScriptDownloader(TenkeiparadoxClient):
    user: UserData | None
    master: MasterData | None

    scenes: dict[str, str] | None  # Optional

    @staticmethod
    def read_json(file_path: str | Path):
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: str | Path, data):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
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
            result.append({
                'name': name.replace('%username%', '皇子') if name else '',
                'message': message if message else ''
            })
        return episode_id, result

    def __init__(self, token: str):
        super().__init__(token)
        self.user = None
        self.master = None

    def login(self, token: str = None):
        if token:
            self.token = token
        else:
            super().login()

    def init_master(self):
        print('Requesting master data...')
        path, ver = self.get_master()
        data = self.session.get(f'{self.MASTER_BASE_URL}/{path}')
        master, version = deserialize_master(data.content)
        location_node: LocationNodeMaster
        episode: EpisodeMaster
        character_episode: CharacterEpisodeMaster
        self.master = MasterData(
            location_node={ln.Id: ln for ln in master[Code.LocationNodeMaster]},
            episode={e.Id: e for e in master[Code.EpisodeMaster]},
            character_episode={ce.Id: ce for ce in master[Code.CharacterEpisodeMaster]}
        )
        print(f'Total master location nodes: {len(self.master.LocationNode)}')
        print(f'Total master episodes: {len(self.master.Episode)}')
        print(f'Total master character episodes: {len(self.master.CharacterEpisode)}')
        print(
            f'Total scene assets: {sum(len(e.SceneAssetIds + e.AdultSceneAssetIds) for e in self.master.Episode.values())}')
        print('-' * 50)

    def init_user(self):
        print('Requesting user data...')
        resp = self.request('GET', 'data/user')
        result = resp.json()['result']
        location_nodes: set[int] = set()
        character_episodes: set[int] = set()
        for data in result:
            match data[0]:
                case 22:
                    location_nodes.add(data[1][1])
                case 34:
                    character_episodes.add(data[1][1])
                case _:
                    pass
        self.user = UserData(location_nodes, character_episodes)
        print(f'Total user location nodes: {len(self.user.LocationNode)}')
        print(f'Total user character episodes: {len(self.user.CharacterEpisode)}')
        print('-' * 50)

    def download(self, scene_dir: str | Path = 'scenes',
                 exist_func: Callable[['ScriptDownloader', str | int], bool] = None):
        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)

        def _exists(downloader, asset_id: str | int) -> bool:
            return (scene_dir / f'{asset_id}.json').exists()

        exists = exist_func if exist_func else _exists

        owned_location_nodes = filter(
            lambda x: x.Id in self.user.LocationNode and x.EpisodeMasterId,
            self.master.LocationNode.values()
        )
        owned_character_episodes = filter(
            lambda x: x.Id in self.user.CharacterEpisode,
            self.master.CharacterEpisode.values()
        )

        # 尝试读取所有活动和主线剧情
        # ------------------------------------
        # owned_location_nodes = filter(
        #     lambda x: x.EpisodeMasterId,
        #     self.master.LocationNode.values()
        # )
        # ------------------------------------

        print('Starting download...')

        category = {
            LocationNodeMaster: 'Quest',
            CharacterEpisodeMaster: 'Character'
        }

        data_obj: LocationNodeMaster | CharacterEpisodeMaster
        for data_obj in chain(owned_location_nodes, owned_character_episodes):
            episode_master = self.master.Episode[data_obj.EpisodeMasterId]
            scene_asset_ids = episode_master.SceneAssetIds + episode_master.AdultSceneAssetIds
            if all(exists(asset_id) for asset_id in scene_asset_ids):
                continue

            episode_type = category[type(data_obj)]

            resp = self.request(
                'POST',
                f'Episodes/{episode_type}/{data_obj.Id}/getDetails'
            ).json()

            if errors := resp['errors']:
                print(f'Error: {errors[0][0]}, {errors[0][1]}')
                continue

            scene_details: list[tuple[int, str]] = resp['result'][2]

            for sid, path in scene_details:
                if exists(sid): continue
                scene_data = self.session.get(f'{self.MASTER_BASE_URL}/{path}')
                sid, data = self.parse(deserialize(scene_data.content))
                self.write_json(scene_dir / f'{sid}.json', data)
                print(f'Saved => Type: {episode_type}, AssetID: {sid}')

        print('-' * 50)

    def generate_names(self, scene_dir: str | Path = 'scenes', path: str | Path = 'names.json'):
        if isinstance(scene_dir, str):
            scene_dir = Path(scene_dir)
        names = self.read_json(path) if Path(path).exists() else {}
        for file in scene_dir.rglob('*.json'):
            data = self.read_json(file)
            for name in set(i.get('name') for i in data):
                if not name or name in names:
                    continue
                names[name] = ''
        self.write_json(path, names)

    def generate_titles(self, path: str | Path = 'titles.json'):
        titles = self.read_json(path)
        for episode in self.master.Episode.values():
            if episode.Title in titles:
                continue
            titles[episode.Title] = ''
        self.write_json(path, titles)

        self.write_json('titles.json', [
            {'message': o}
            for o, t in titles.items()
            if o and not t
        ])
