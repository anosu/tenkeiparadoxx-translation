using BepInEx.Configuration;

namespace TenparaMod
{
    public static class Config
    {
        public static ConfigEntry<bool> Mosaic;
        public static ConfigEntry<bool> Translation;
        public static ConfigEntry<string> TranslationCDN;
        public static ConfigEntry<string> FontBundlePath;
        public static ConfigEntry<string> FontAssetName;
        public static ConfigEntry<string> OutlineMaterialName;

        public static void Initialize()
        {
            Mosaic = Plugin.Config.Bind("General", "InGameMosaic", false, "是否开启游戏内马赛克");
            Translation = Plugin.Config.Bind("Translation", "Enabled", true, "是否开启翻译");
            TranslationCDN = Plugin.Config.Bind("Translation", "CdnURL", "https://tenkeiparadox.ntr.best", "翻译加载的CDN");
            FontBundlePath = Plugin.Config.Bind("Translation", "FontBundlePath", "font/jiangchengyuanti", "TMP字体AssetBundle的路径");
            FontAssetName = Plugin.Config.Bind("Translation", "FontAssetName", "JiangChengYuanTi SDF", "AssetBundle中TMP_FontAsset的名称");
            OutlineMaterialName = Plugin.Config.Bind("Translation", "OutlineMaterialName", "JiangChengYuanTi SDF Base Outline", "AssetBundle中描边材质的名称");
        }
    }
}
