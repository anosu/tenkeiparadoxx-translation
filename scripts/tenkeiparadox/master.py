from dataclasses import dataclass

from serialize import deserialize


class Code:
    LocationNodeMaster = 20
    EpisodeMaster = 32
    CharacterEpisodeMaster = 33


@dataclass
class LocationNodeMaster:
    Id: int
    LocationMasterId: int
    Order: int
    PreviousNodeId: int | None
    QuestMasterId: int | None
    EpisodeMasterId: int | None
    OpenDate: float | None
    CloseDate: float | None
    Rewards: list
    FlavorTitle: str
    FlavorText: str
    FlavorPositionIndex: int | None
    LocationNodeFlag: int
    AssetId: str
    LocationNodeSpecialEffectTypes: int | None
    LocationNodeSpecialEffectPoints: int | None
    Type: int


@dataclass
class EpisodeMaster:
    Id: int
    EpisodeOrderName: str
    Title: str
    HasAdultScene: bool
    MainCharacterMasterId1: int | None
    MainCharacterMasterId2: int | None
    MainCharacterMasterId3: int | None
    MainCharacterMasterId4: int | None
    SceneAssetIds: list[str]
    AdultSceneAssetIds: list[str]
    BackgroundImageAssetIds: list[str]
    StillAssetIds: list[str]
    BackgroundMusicAssetIds: list[str]
    CharacterAssetIds: list[int]
    Digest: str
    XPositionFlag: int


@dataclass
class CharacterEpisodeMaster:
    Id: int
    EpisodeMasterId: int
    EpisodeOrder: int
    CharacterMasterId: int
    CharacterEpisodeRewards: list


MasterDataType: dict[int, type] = {
    Code.LocationNodeMaster: LocationNodeMaster,
    Code.EpisodeMaster: EpisodeMaster,
    Code.CharacterEpisodeMaster: CharacterEpisodeMaster
}


def deserialize_master(data: bytes) -> tuple[dict[int, list], str]:
    source, version = deserialize(data)
    result = {}
    for code, args in source:
        cls = MasterDataType.get(code)
        result.setdefault(code, []).append(cls(*args) if cls else args)

    return result, version
