using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace llama_communication_training.ui
{
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
        GameObject _nextIcon; 

        private Coroutine _typingCoroutine;

        private void Start()
        {
            StartTyping("緒方", 0, "これはテストです。これはテストです。これはテストです。");
        }

        public void StartTyping(string talkerName, int index, string message)
        {
            // 前回のコルーチンを停止
            if (_typingCoroutine != null)
                StopCoroutine(_typingCoroutine);

            _nameLabel.text = talkerName;
            if(index >= 0 && index < _namePlateList.Length)
            {
                _namePlate.sprite = _namePlateList[index];
                _namePlate.gameObject.SetActive(true);
            }
            else
            {
                _namePlate.gameObject.SetActive(false); 
            }
            _nextIcon.SetActive(false); 

            _typingCoroutine = StartCoroutine(TypeText(message));
        }

        private IEnumerator TypeText(string message)
        {
            _message.text = message;
            _message.maxVisibleCharacters = 0;

            int totalLength = message.Length;

            for (int i = 0; i <= totalLength; i++)
            {
                _message.maxVisibleCharacters = i;
                yield return new WaitForSeconds(_secondsPerCharacter);
            }
            _nextIcon.SetActive(true);
        }
    }
}
