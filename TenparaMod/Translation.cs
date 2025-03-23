using BepInEx;
using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using TMPro;
using UnityEngine;


namespace TenparaMod
{
    public class Translation
    {
        public static string cdn = "http://localhost:5000";
        public static HttpClient client = new();
        public static Dictionary<string, string> names = [];
        public static Dictionary<string, string> titles = [];
        public static Dictionary<long, Dictionary<string, string>> scenes = [];
        public static AssetBundle fontBundle = null;
        public static TMP_FontAsset fontAsset = null;
        public static Material outlineMaterial = null;

        public static void Initialize()
        {
            cdn = Config.TranslationCDN.Value;
            LoadTranslation();
            LoadFontAsset();
        }

        public static async Task<T> GetAsync<T>(string url) where T : class
        {
            try
            {
                var response = await client.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<T>();
                }
            }
            catch (Exception e)
            {
                Plugin.Log.LogError($"Error: {e.Message}");
            }
            return null;
        }

        public static async Task LoadTranslation()
        {
            if (!Config.Translation.Value)
            {
                return;
            }
            var nameTask = GetAsync<Dictionary<string, string>>($"{cdn}/translation/names/zh_Hans.json");
            var titleTask = GetAsync<Dictionary<string, string>>($"{cdn}/translation/titles/zh_Hans.json");
            await Task.WhenAll(nameTask, titleTask);

            if (nameTask.Result != null)
            {
                names = nameTask.Result;
                Plugin.Log.LogInfo($"Character names translation loaded. Total: {names.Count}");
            }
            else
            {
                Plugin.Log.LogWarning($"Character names translation load failed");
            }
            if (titleTask.Result != null)
            {
                titles = titleTask.Result;
                Plugin.Log.LogInfo($"Scenario titles translation loaded. Total: {titles.Count}");
            }
            else
            {
                Plugin.Log.LogWarning($"Scenario titles translation load failed");
            }

        }

        public static void LoadFontBundle()
        {
            string path = Config.FontBundlePath.Value;
            string bundlePath = Path.IsPathRooted(path) ? path : Path.Combine(Paths.PluginPath, path);
            if (!File.Exists(bundlePath) || fontBundle != null)
            {
                return;
            }
            fontBundle = AssetBundle.LoadFromFile(bundlePath);
        }

        public static void LoadFontAsset()
        {
            if (fontAsset != null || !Config.Translation.Value)
            {
                return;
            }
            LoadFontBundle();
            if (fontBundle == null)
            {
                Plugin.Log.LogWarning("Font bundle load failed");
                return;
            }
            fontAsset = fontBundle.LoadAsset(Config.FontAssetName.Value).TryCast<TMP_FontAsset>();
            outlineMaterial = fontBundle.LoadAsset(Config.OutlineMaterialName.Value).TryCast<Material>();
            Plugin.Log.LogInfo($"TMP_FontAsset {fontAsset.name} is loaded");
            Plugin.Log.LogInfo($"Material {outlineMaterial.name} is loaded");
        }

        public static async Task GetScenarioTranslationAsync(long episodeId)
        {
            if (scenes.ContainsKey(episodeId))
            {
                return;
            }
            var translations = await GetAsync<Dictionary<string, string>>($"{cdn}/translation/scenes/{episodeId}/zh_Hans.json");
            if (translations != null)
            {
                scenes[episodeId] = translations;
                Plugin.Log.LogInfo($"Scenario translation loaded. Total: {translations.Count}");
            }
            else
            {
                Plugin.Log.LogWarning($"Translations loaded failed: {episodeId}");
            }
        }

    }
}
