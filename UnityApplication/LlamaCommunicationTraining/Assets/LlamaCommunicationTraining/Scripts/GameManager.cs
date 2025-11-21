using llama_communication_training.data;
using llama_communication_training.network;
using llama_communication_training.network.payload;
using llama_communication_training.ui;
using System;
using System.Collections;
using UnityEngine;

namespace llama_communication_training
{
    public class GameManager : MonoBehaviour
    {
        [SerializeField]
        Settings _setting;

        [SerializeField]
        Transmitter _transmitter;

        [SerializeField]
        ResultPanel _resultPanel;

        [SerializeField]
        MessageInput _messageInput;

        private int _score = 0; 

        // Start is called once before the first execution of Update after the MonoBehaviour is created
        void Start()
        {
            Setup(); 
        }

        private void Setup()
        {
            _transmitter.Setup(_setting);
            _resultPanel.gameObject.SetActive(false);
            _score = 0;
            StartCoroutine(_transmitter.CoReset(new network.payload.RequestReset { }, (bool ret, ResponseReset res) =>
            {
                Debug.Log($"Reset result: {ret}, {JsonUtility.ToJson(res)}");
                _messageInput.ReceiveFirstMessage(res.first_message, res.face_type);
            }));
        }

        // Update is called once per frame
        void Update()
        {
        
        }

        internal void AddScore(int score)
        {
            _score += score; 
        }

        internal void FinishGame()
        {
            StartCoroutine(CoFinishGame());
        }

        private IEnumerator CoFinishGame()
        {
            yield return new WaitForSeconds(2.0f);
            _resultPanel.gameObject.SetActive(true);
            _resultPanel.Setup(_score);
        }
    }
}
