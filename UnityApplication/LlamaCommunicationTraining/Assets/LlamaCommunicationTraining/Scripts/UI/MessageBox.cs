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
        public int FaceType; 
        public Action Notify;
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

        [SerializeField]
        AnimationController _animationController;

        [SerializeField]
        AudioSource _seKeyTypeMyself;

        [SerializeField]
        AudioSource _seKeyTypeYou;


        private Coroutine _typingCoroutine;
        private List<MessageReserve> _messageQueue = new List<MessageReserve>();

        private void Start()
        {
            _typingCoroutine = StartCoroutine(TypeText());
        }

        public void StartTyping(string talkerName, int index, string message, int faceType, Action notify = null)
        {
            _messageQueue.Add(new MessageReserve
            {
                TalkerName = talkerName,
                NamePlateIndex = index,
                Message = message,
                FaceType = faceType, 
                Notify = notify
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

                _animationController.SetFaceType(nextMessage.FaceType); 
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
                    if(IsOtherMessage(nextMessage))
                    {
                        UpdateMouce(i, message);
                        _seKeyTypeYou.Play();
                    }
                    else
                    {
                        _seKeyTypeMyself.Play();
                    }
                    yield return new WaitForSeconds(_secondsPerCharacter);
                }
                if (IsOtherMessage(nextMessage))
                {
                    _animationController.SetPronounce("-");
                }
                _nextIcon.SetActive(true);
                yield return new WaitForSeconds(_intervalForEachMessage);
                nextMessage.Notify?.Invoke();

            }

        }

        private bool IsOtherMessage(MessageReserve message)
        {
            return (message.NamePlateIndex > 0);
        }

        private void UpdateMouce(int index, string message)
        {
            string pr_a = "あかさたなはまやらわアカサタナハマヤラワがざだばぱガザダババa";
            string pr_i = "いきしちにひみりイキシチニヒミリぎじぢびぴギジヂビピi";
            string pr_u = "うくすつぬふむゆるウクスツヌフムユルぐずづぶぷグズヅブプu";
            string pr_e = "えけせてねへめれエケセテネヘメレげぜでべぺゲゼデベペe";
            string pr_o = "おこそとのほもろをオコソトノホモロヲごぞどぼぽゴゾドポボo";

            string ch = "-";
            if (index < message.Length)
            {
                ch = message.Substring(index, 1);
            }
            if (pr_a.IndexOf(ch) >= 0)
            {
                _animationController.SetPronounce("a");
            }
            if (pr_i.IndexOf(ch) >= 0)
            {
                _animationController.SetPronounce("i");
            }
            if (pr_u.IndexOf(ch) >= 0)
            {
                _animationController.SetPronounce("u");
            }
            if (pr_e.IndexOf(ch) >= 0)
            {
                _animationController.SetPronounce("e");
            }
            if (pr_o.IndexOf(ch) >= 0)
            {
                _animationController.SetPronounce("o");
            }
        }
    }
}
