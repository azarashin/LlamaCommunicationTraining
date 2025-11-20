using System;
using UnityEngine;

namespace llama_communication_training.network.payload
{
    [Serializable]
    public class ResponseSendPlayerMessage
    {
        public string message;
        public int face_type;
        public int score;
        public bool end; 
    }
}
