using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using System;
using System.Text;

namespace TenparaMod;

[BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
public class Plugin : BasePlugin
{
    public static new ConfigFile Config;
    public static new ManualLogSource Log;

    public override void Load()
    {
        Console.OutputEncoding = Encoding.UTF8;

        // Plugin startup logic
        Log = base.Log;
        Config = base.Config;
        Log.LogInfo($"Plugin {MyPluginInfo.PLUGIN_GUID} is loaded!");
        TenparaMod.Config.Initialize();
        Patch.Initialize();
        Translation.Initialize();
        AddComponent<PluginBehaviour>();
    }
}
