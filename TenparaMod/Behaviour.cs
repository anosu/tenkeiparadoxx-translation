using UnityEngine;

namespace TenparaMod
{
    public class PluginBehaviour : MonoBehaviour
    {
        private void Awake() { }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.F5))
            {
                Config.Mosaic.Value = !Config.Mosaic.Value;
                Plugin.Log.LogInfo($"{Config.Mosaic.Definition.Section}.{Config.Mosaic.Definition.Key}: {Config.Mosaic.Value}");
            }
        }

    }
}
