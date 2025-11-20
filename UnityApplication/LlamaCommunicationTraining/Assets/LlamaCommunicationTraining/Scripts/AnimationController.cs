using UnityEngine;

public class AnimationController : MonoBehaviour
{
    public enum Emotion
    {
        Neutral,
        Happy,
        Sad,
        Angry,
        Surprised
    }

    [SerializeField]
    Animator _animator;

    [SerializeField]
    string _pronouce;

    [SerializeField]
    Emotion _currentEmotion = Emotion.Neutral;

    private Emotion _previousEmotion; 

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        _previousEmotion = _currentEmotion;
    }

    // Update is called once per frame
    void Update()
    {
        UpdateMouce();
        UpdateEmotion();
    }

    private void UpdateEmotion()
    {
        if(_previousEmotion != _currentEmotion)
        {
            switch(_currentEmotion)
            {
                case Emotion.Neutral:
                    _animator.SetTrigger("Neutral");
//                    _animator.SetLayerWeight(2, 1);
                    break;
                case Emotion.Happy:
                    _animator.SetTrigger("Happy");
                    //                    _animator.SetLayerWeight(2, 1);
                    break;
                case Emotion.Sad:
                    _animator.SetTrigger("Sad");
                    //                    _animator.SetLayerWeight(2, 1);
                    break;
                case Emotion.Angry:
                    _animator.SetTrigger("Angry");
                    //                    _animator.SetLayerWeight(2, 1);
                    break;
                case Emotion.Surprised:
                    _animator.SetTrigger("Surprised");
                    //                    _animator.SetLayerWeight(2, 1);
                    break;
                default:
                    _animator.SetTrigger("Neutral");
                    //                    _animator.SetLayerWeight(2, 1);
                    break;
            }
            _previousEmotion = _currentEmotion;
        }
    }

    private void UpdateMouce()
    { 
        if(string.IsNullOrEmpty(_pronouce))
        {
        }
        else if(_pronouce == "a")
        {
            _animator.SetTrigger("PronounceA");
            //            _animator.SetLayerWeight(1, 1);
            _pronouce = ""; 
        }
        else if (_pronouce == "i")
        {
            _animator.SetTrigger("PronounceI");
            //            _animator.SetLayerWeight(1, 1);
            _pronouce = "";
        }
        else if (_pronouce == "u")
        {
            _animator.SetTrigger("PronounceU");
            //            _animator.SetLayerWeight(1, 1);
            _pronouce = "";
        }
        else if (_pronouce == "e")
        {
            _animator.SetTrigger("PronounceE");
            //            _animator.SetLayerWeight(1, 1);
            _pronouce = "";
        }
        else if (_pronouce == "o")
        {
            _animator.SetTrigger("PronounceO");
            //            _animator.SetLayerWeight(1, 1);
            _pronouce = "";
        }
        else
        {
            _animator.SetTrigger("PronounceIdle");
            //            _animator.SetLayerWeight(1, 0);
            _pronouce = "";
        }
    }


}
