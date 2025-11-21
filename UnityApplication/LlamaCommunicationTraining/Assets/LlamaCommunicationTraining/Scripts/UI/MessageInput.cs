using llama_communication_training.network;
using llama_communication_training.network.payload;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace llama_communication_training.ui
{
    public class MessageInput : MonoBehaviour
    {
        [SerializeField]
        GameManager _gameManager;

        [SerializeField]
        Transmitter _transmitter;

        [SerializeField]
        MessageBox _messageBox;

        [SerializeField]
        CanvasGroup _uiBody;

        [SerializeField]
        TMP_InputField _inputField;

        // Start is called once before the first execution of Update after the MonoBehaviour is created
        void Start()
        {

        }

        // Update is called once per frame
        void Update()
        {

        }

        public void OnSendMessage(string message)
        {
            _uiBody.alpha = 0.5f;
            _uiBody.interactable = false;
            _inputField.text = ""; 
            _messageBox.StartTyping("自分", 0, message, -1);
            StartCoroutine(_transmitter.CoSendPlayerMessage(new network.payload.RequestSendPlayerMessage
            {
                message = message
            }, (bool success, ResponseSendPlayerMessage response) =>
            {
                if (success)
                {
                    string talkerName = "相手";
                    int talkerIndex = 1; 
                    
                    Debug.Log($"[Response] {JsonUtility.ToJson(response)}");
                    _messageBox.StartTyping(talkerName, talkerIndex, response.message, response.face_type, () =>
                    {
                        _gameManager.AddScore(response.score);
                        if(response.end)
                        {
                            _gameManager.FinishGame();
                        }
                        else
                        {
                            _uiBody.alpha = 1.0f;
                            _uiBody.interactable = true;
                        }
                    });
                }
                else
                {
                    Debug.LogError("Failed to send message.");
                }
            }));
        }
    }
}
