using llama_communication_training.data;
using llama_communication_training.network.payload;
using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace llama_communication_training.network
{


    public class Transmitter : MonoBehaviour
    {
        private Settings _setting; 
        internal void Setup(Settings setting)
        {
            _setting = setting; 
        }

        // Update is called once per frame
        void Update()
        {
        
        }

        public IEnumerator CoReset(RequestReset requestData, Action<bool, ResponseReset> notify)
        {
            string endPoint = $"{_setting.ServerURL}/reset";
            yield return CoSendData(endPoint, requestData, notify);
        }

        public IEnumerator CoSendPlayerMessage(RequestSendPlayerMessage requestData, Action<bool, ResponseSendPlayerMessage> notify)
        {
            string endPoint = $"{_setting.ServerURL}/send_message";
            yield return CoSendData(endPoint, requestData, notify);
        }

        private IEnumerator CoSendData<T_REQ, T_RES>(string endPoint, T_REQ requestData, Action<bool, T_RES> notify)
        {

            string json = JsonUtility.ToJson(requestData);
            Debug.Log($"[Request] {json}");

            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);

            using (UnityWebRequest www = new UnityWebRequest(endPoint, "POST"))
            {
                www.uploadHandler = new UploadHandlerRaw(bodyRaw);
                www.downloadHandler = new DownloadHandlerBuffer();

                // ヘッダーで JSON だと明示
                www.SetRequestHeader("Content-Type", "application/json");
                www.SetRequestHeader("Accept", "application/json");

                yield return www.SendWebRequest();

#if UNITY_2020_1_OR_NEWER
                if (www.result != UnityWebRequest.Result.Success)
#else
            if (www.isNetworkError || www.isHttpError)
#endif
                {
                    Debug.LogError($"[Error] {www.responseCode} : {www.error}");
                    Debug.LogError($"[Body] {www.downloadHandler.text}");
                }
                else
                {
                    string responseText = www.downloadHandler.text;
                    Debug.Log($"[Response Raw] {responseText}");

                    // JSON → C#オブジェクト
                    try
                    {
                        T_RES response =
                            JsonUtility.FromJson<T_RES>(responseText);
                        notify.Invoke(true, response);
                    }
                    catch (Exception e)
                    {
                        // T_RES が値型の場合、default(T_RES) を使う
                        notify.Invoke(false, default);
                        Debug.LogError($"JSON parse error: {e}");
                    }
                }
            }
        }

    }
}
