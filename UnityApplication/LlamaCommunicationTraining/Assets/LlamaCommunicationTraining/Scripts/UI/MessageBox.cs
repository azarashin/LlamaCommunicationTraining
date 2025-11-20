using Codice.Client.BaseCommands.BranchExplorer;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using TMPro;
using UnityEditor.VersionControl;
using UnityEngine;
using UnityEngine.UI;

namespace llama_communication_training.ui
{
    public class MessageReserve
    {
        public string TalkerName;
        public int NamePlateIndex;
        public string Message;
    }
    public class MessageBox : MonoBehaviour
    {
        [SerializeField] 
        TextMeshProUGUI _nameLabel;

        [SerializeField]
        TextMeshProUGUI _message;

        [SerializeField]
        Image _namePlate;

        [SerializeField]
        Sprite[] _namePlateList; 

        [SerializeField] 
        float _secondsPerCharacter = 0.05f;

        [SerializeField]
        float _intervalForEachMessage = 2.0f; 

        [SerializeField]
        GameObject _nextIcon; 

        private Coroutine _typingCoroutine;
        private List<MessageReserve> _messageQueue = new List<MessageReserve>();

        private void Start()
        {
            _typingCoroutine = StartCoroutine(TypeText());


            StartTyping("緒方", 0, "これはテストです。これはテストです。これはテストです。");
            StartTyping("だれか", 1, "これはこれはこれはこれはこれはこれはこれはこれはこれはこれは");
        }

        public void StartTyping(string talkerName, int index, string message)
        {
            _messageQueue.Add(new MessageReserve
            {
                TalkerName = talkerName,
                NamePlateIndex = index,
                Message = message
            });
        }

        private IEnumerator TypeText()
        {
            while (true)
            {
                if (_messageQueue.Count == 0)
                {
                    yield return null;
                    continue;
                }
                MessageReserve nextMessage = _messageQueue[0];
                _messageQueue.RemoveAt(0);

                string message = nextMessage.Message;
                _nameLabel.text = nextMessage.TalkerName;
                int index = nextMessage.NamePlateIndex;
                if (index >= 0 && index < _namePlateList.Length)
                {
                    _namePlate.sprite = _namePlateList[index];
                    _namePlate.gameObject.SetActive(true);
                }
                else
                {
                    _namePlate.gameObject.SetActive(false);
                }
                _nextIcon.SetActive(false);


                _message.text = message;
                _message.maxVisibleCharacters = 0;

                int totalLength = message.Length;

                for (int i = 0; i <= totalLength; i++)
                {
                    _message.maxVisibleCharacters = i;
                    yield return new WaitForSeconds(_secondsPerCharacter);
                }
                _nextIcon.SetActive(true);
                yield return new WaitForSeconds(_intervalForEachMessage);

            }

        }
    }
}
