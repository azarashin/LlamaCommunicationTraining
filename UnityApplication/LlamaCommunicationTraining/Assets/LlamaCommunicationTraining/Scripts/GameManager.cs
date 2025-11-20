using llama_communication_training.data;
using llama_communication_training.network;
using llama_communication_training.ui;
using System;
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
            _resultPanel.Setup(_score);
            _resultPanel.gameObject.SetActive(true); 
        }
    }
}
