using System;
using UnityEngine;

namespace llama_communication_training.network.payload
{
    [Serializable]
    public class ResponseReset
    {
        public bool result;
        public string first_message;
        public int face_type; 
    }
}
