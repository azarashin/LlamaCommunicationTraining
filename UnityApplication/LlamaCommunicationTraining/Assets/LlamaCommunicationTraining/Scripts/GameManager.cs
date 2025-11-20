using llama_communication_training.data;
using llama_communication_training.network;
using UnityEngine;

namespace llama_communication_training
{
    public class GameManager : MonoBehaviour
    {
        [SerializeField]
        Settings _setting;

        [SerializeField]
        Transmitter _transmitter; 

        // Start is called once before the first execution of Update after the MonoBehaviour is created
        void Start()
        {
            Setup(); 
        }

        private void Setup()
        {
            _transmitter.Setup(_setting); 
        }

        // Update is called once per frame
        void Update()
        {
        
        }
    }
}
