using HarmonyLib;
using System.Text;
using System.Threading.Tasks;
using ParipariApi.Shared.Results;
using System.Collections.Generic;
using Assets.Paripari.Scripts.UIComponents.Scenario;
using Assets.Paripari.CustomRendererFeatures.Mosaic;
using Il2CppSystem;

namespace TenparaMod
{
    public class Patch
    {
        public static long episodeId;
        static readonly TimeZoneInfo TZ = TimeZoneInfo.FindSystemTimeZoneByIdWinRTFallback("Tokyo Standard Time");

        public static void Initialize()
        {
            Harmony.CreateAndPatchAll(typeof(Patch));
        }

        [HarmonyPostfix]
        [HarmonyPatch(typeof(TimeZoneInfo), nameof(TimeZoneInfo.Local), MethodType.Getter)]
        public static void SetTimeZoneInfo(ref TimeZoneInfo __result)
        {
            __result = TZ;
        }

        [HarmonyPostfix]
        [HarmonyPatch(typeof(MosaicRendererFeature), nameof(MosaicRendererFeature.Create))]
        public static void RemoveMosaic(MosaicRendererFeature __instance)
        {
            if (!Config.Mosaic.Value)
            {
                __instance.passSettings.Keyword = "114514";
            }
        }

        //[HarmonyPostfix]
        //[HarmonyPatch(typeof(ScenarioSceneContainer), nameof(ScenarioSceneContainer.Load))]
        //public static void FetchTranslation(SceneDetail sceneDetail)
        //{
        //    Plugin.Log.LogInfo($"Id: {sceneDetail.Id}, AssetId: {sceneDetail.AssetId}");
        //    if (!Config.Translation.Value)
        //    {
        //        return;
        //    }
        //    episodeId = sceneDetail.Id;
        //    Translation.GetScenarioTranslationAsync(episodeId).GetAwaiter().GetResult();
        //    if (Translation.scenes.ContainsKey(episodeId))
        //    {
        //        Translation.LoadFontAsset();
        //    }
        //}

        [HarmonyPrefix]
        [HarmonyPatch(typeof(ScenarioPresenter), nameof(ScenarioPresenter.Show))]
        public static void FetchTranslation(ScenarioPresenter __instance)
        {
            if (!Config.Translation.Value)
            {
                return;
            }
            var tasks = new List<Task>();
            StringBuilder sb = new StringBuilder();
            foreach (var detail in __instance.episodeDetails.SceneDetails)
            {
                tasks.Add(Translation.GetScenarioTranslationAsync(detail.Id));
                sb.Append($"{detail.Id}, ");
            }
            sb.Remove(sb.Length - 2, 2);
            Plugin.Log.LogInfo($"Loaded scenes: {sb}");
            Task.WaitAll(tasks.ToArray());
        }

        [HarmonyPrefix]
        [HarmonyPatch(typeof(ScenarioLifeCycleManager), nameof(ScenarioLifeCycleManager.PrepareScene))]
        public static void LoadTranslationFont(SceneDetail sceneDetail)
        {
            if (!Config.Translation.Value)
            {
                return;
            }
            episodeId = sceneDetail.Id;
            if (Translation.scenes.ContainsKey(episodeId))
            {
                foreach (var frameDetail in sceneDetail.SceneFrameDetails)
                {
                    if (frameDetail.SpeakerName != null && Translation.names.TryGetValue(frameDetail.SpeakerName, out string name))
                    {
                        frameDetail.SpeakerName = name;
                    }
                    if (frameDetail.PhraseContents != null && Translation.scenes[episodeId].TryGetValue(frameDetail.PhraseContents, out string phrase))
                    {
                        frameDetail.PhraseContents = phrase;
                    }
                }
                Translation.LoadFontAsset();
            }
        }

        [HarmonyPrefix]
        [HarmonyPatch(typeof(ScenarioTitle), nameof(ScenarioTitle.Show))]
        public static void ReplaceTitleText(ScenarioTitle __instance, ref string mainText, string subText)
        {
            if (!Config.Translation.Value || !Translation.scenes.ContainsKey(episodeId))
            {
                return;
            }
            if (mainText != null && Translation.titles.TryGetValue(mainText, out string title))
            {
                mainText = title;
                if (Translation.fontAsset != null)
                {
                    __instance.titleMainText.font = Translation.fontAsset;
                }
            }
        }

        [HarmonyPrefix]
        [HarmonyPatch(typeof(ScenarioPhrase), nameof(ScenarioPhrase.SetFontMaterial))]
        public static void ReplaceMessageTextFontMaterial(ScenarioPhrase __instance)
        {
            if (!Config.Translation.Value || !Translation.scenes.ContainsKey(episodeId) || Translation.fontAsset == null)
            {
                return;
            }
            __instance.nameText.font = Translation.fontAsset;
            __instance.phraseText.font = Translation.fontAsset;
            __instance.fontDefaultMaterial = Translation.fontAsset.material;
            __instance.fontOutlineMaterial = Translation.outlineMaterial;
        }

        [HarmonyPrefix]
        [HarmonyPatch(typeof(ScenarioLogPanelContent), nameof(ScenarioLogPanelContent.Show))]
        public static void ReplaceLogFont(ScenarioLogPanelContent __instance)
        {
            if (!Config.Translation.Value || !Translation.scenes.ContainsKey(episodeId) || Translation.fontAsset == null)
            {
                return;
            }
            __instance.speakerNameText.font = Translation.fontAsset;
            __instance.phraseContentText.font = Translation.fontAsset;
            __instance.phraseContentText.lineSpacing = -42f;
        }

    }
}
