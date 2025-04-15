from dataclasses import dataclass

from serialize import deserialize


class Code:
    CharacterMaster = 4
    EventMaster = 18
    LocationMaster = 19
    LocationNodeMaster = 20
    EpisodeMaster = 32
    CharacterEpisodeMaster = 33
    PaidEpisodeMaster = 145


@dataclass
class CharacterMaster:
    Id: int
    CharacterBaseId: int
    PassiveShareGroupId: int
    Name: str | None
    AnotherName: str | None
    AssetId: str | None
    ModelAssetId: str | None
    ModelAssetConfigurationJson: str | None
    WeaponAssetConfigurationJson: str | None
    Rarity: int
    Affiliation: int
    Type: int
    MaxLevel: int
    PvpCost: int
    SelfIntroduction: str | None
    Race: str | None
    Birthday: float | None
    Bust: int | None
    Waist: int | None
    Hip: int | None
    Likes: str
    Dislikes: str | None
    GoodAt: str | None
    FirstSecret: str | None
    SecondSecret: str | None
    CharacterIconMasterId: int
    MinLevelStatus: list[int]
    MaxLevelStatus: list[int] | None
    LevelPatternId: int
    RankPatternId: int
    AwakeningPatternId: int
    AwakeningPointItemMasterId: int
    Resistances: list[list[int | float]]
    Skills: list[list]
    ExchangeItemMasterId: int
    VoiceMessages: dict[int, str]
    AwakeningRewardPatternId: int
    CharacterExtraLevelGroupMasterId: int
    AiType: int
    BirthdayCustomDescription: str | None
    WeaponOverrideCategoryId: int
    DisplayStatus: list[int]
    DisplayStatusIgnoreExtraLevelBonus: list[int]
    IsNotAvailableHomeCharacterDoubleSetting: bool
    IsCollaboration: bool


@dataclass
class EventMaster:
    Id: int
    Name: str | None
    Type: int
    StartDate: float
    EndDate: float | None
    AvailableDayOfWeek: int
    BackgroundAssetId: str | None
    NavigatorAssetId: str | None
    OriginalEventMasterId: int | None
    ExchangeMasterId: int | None
    BackgroundMusicAssetId: str | None
    IsRevival: bool
    LayoutAssetId: str | None
    IconAssetId: str | None
    Order: int
    TopDisplayName: str | None
    IsBackgroundInversion: bool


@dataclass
class LocationMaster:
    Id: int
    EventMasterId: int
    Type: int
    Name: str | None
    GroupOrder: int
    InGroupOrder: int
    OpenDate: float | None
    CloseDate: float | None
    AvailableDayOfWeek: int | None
    UnlockItemMasterId: int | None
    DailyVictoryLimit: int | None
    WorldMapCountryType: int
    BunnerAssetId: str | None
    BackGroundAssetId: str | None
    NavigatorAssetId: str | None
    HomeDisplayName: str | None
    LocationRewards: list
    DisplayCharacterMasterId: int | None
    IsBackgroundInversion: bool


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
    FlavorTitle: str | None
    FlavorText: str | None
    FlavorPositionIndex: int | None
    LocationNodeFlag: int
    AssetId: str | None
    LocationNodeSpecialEffectType: int | None
    LocationNodeSpecialEffectPoints: int | None
    Type: int


@dataclass
class EpisodeMaster:
    Id: int
    EpisodeOrderName: str | None
    Title: str | None
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
    Digest: str | None
    XPositionFlag: int


@dataclass
class CharacterEpisodeMaster:
    Id: int
    EpisodeMasterId: int
    EpisodeOrder: int
    CharacterMasterId: int
    CharacterEpisodeRewards: list


@dataclass
class PaidEpisodeMaster:
    Id: int
    EpisodeMasterId: int
    ActivateItemMasterId: int
    ShopItemMasterId: int | None
    AssetId: str | None
    Order: int
    ShopStartDate: float | None
    ShopEndDate: float | None
    Type: int
    StartDate: float
    EndDate: float | None
    XPositionFlag: int


MasterDataType: dict[int, type] = {
    Code.CharacterMaster: CharacterMaster,
    Code.EventMaster: EventMaster,
    Code.LocationMaster: LocationMaster,
    Code.LocationNodeMaster: LocationNodeMaster,
    Code.EpisodeMaster: EpisodeMaster,
    Code.CharacterEpisodeMaster: CharacterEpisodeMaster,
    Code.PaidEpisodeMaster: PaidEpisodeMaster
}


def deserialize_master(data: bytes) -> tuple[dict[int, list], str]:
    source, version = deserialize(data)
    result = {}
    for code, args in source:
        cls = MasterDataType.get(code)
        result.setdefault(code, []).append(cls(*args) if cls else args)

    return result, version
