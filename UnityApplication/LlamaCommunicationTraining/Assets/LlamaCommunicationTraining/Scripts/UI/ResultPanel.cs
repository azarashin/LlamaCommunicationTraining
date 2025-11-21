using TMPro;
using UnityEngine;

namespace llama_communication_training.ui
{
    public class ResultPanel : MonoBehaviour
    {
        [SerializeField]
        TextMeshProUGUI _score; 

        public void Setup(int score)
        {
            _score.text = score.ToString();
        }

    }
}
