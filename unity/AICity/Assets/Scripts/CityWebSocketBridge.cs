using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace AICity
{
    /// <summary>
    /// Connects Unity 6 renderer to the AI City Python backend.
    /// Supports HTTP polling and WebSocket streaming.
    /// </summary>
    public class CityWebSocketBridge : MonoBehaviour
    {
        [Header("Backend Settings")]
        public string backendUrl = "http://127.0.0.1:8000";
        public float pollInterval = 2.0f;

        [Header("References")]
        public AgentNPCController npcController;
        public BuildingManager buildingManager;
        public GameHUDManager hudManager;

        private void Start()
        {
            StartCoroutine(PollCityStateRoutine());
        }

        private IEnumerator PollCityStateRoutine()
        {
            while (true)
            {
                yield return StartCoroutine(FetchWorldState());
                yield return StartCoroutine(FetchAgentsState());
                yield return new WaitForSeconds(pollInterval);
            }
        }

        private IEnumerator FetchWorldState()
        {
            using (UnityWebRequest req = UnityWebRequest.Get($"{backendUrl}/world"))
            {
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    string json = req.downloadHandler.text;
                    if (hudManager != null) hudManager.UpdateWorldHUD(json);
                }
            }
        }

        private IEnumerator FetchAgentsState()
        {
            using (UnityWebRequest req = UnityWebRequest.Get($"{backendUrl}/agents"))
            {
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    string json = req.downloadHandler.text;
                    if (npcController != null) npcController.UpdateAgentsFromBackend(json);
                }
            }
        }

        public void SubmitGoalToCity(string goalText)
        {
            StartCoroutine(PostGoalRoutine(goalText));
        }

        private IEnumerator PostGoalRoutine(string goal)
        {
            string payload = $"{{\"title\":\"Unity Goal\",\"goal\":\"{goal}\",\"priority\":0.9,\"target_role\":\"manager\"}}";
            byte[] bodyRaw = Encoding.UTF8.GetBytes(payload);

            using (UnityWebRequest req = new UnityWebRequest($"{backendUrl}/tasks", "POST"))
            {
                req.uploadHandler = new UploadHandlerRaw(bodyRaw);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                yield return req.SendWebRequest();

                if (req.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[AI City Unity] Goal submitted successfully: {goal}");
                }
            }
        }
    }
}
