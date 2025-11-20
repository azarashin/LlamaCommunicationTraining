using UnityEngine;

namespace llama_communication_training.data
{
    [CreateAssetMenu(fileName = "Settings", menuName = "LlamaCommunicationTraining/Settings")]
    public class Settings : ScriptableObject
    {
        public string ServerURL = "http://localhost:5000";

    }
}
