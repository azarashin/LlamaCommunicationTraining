# server1.py (Unity IF維持 + Ollama AI統合版)

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import ollama
from typing import List, Dict
import re

# ------------------------------------------------------------
# Unity から飛んでくる JSON と合わせた Request/Response モデル
#  ※ Unity側を壊さないように message は必須のまま
#  ※ user_id を optional で追加（Unityが送らなくてもOK）
# ------------------------------------------------------------

class RequestSendPlayerMessage(BaseModel):
    message: str = ""
    user_id: str = "default"  # Unityが未送信なら default で一括管理

    class Config:
        extra = "ignore"  # Unity側が余分なキーを送っても落ちないようにする


class ResponseSendPlayerMessage(BaseModel):
    message: str
    face_type: int
    score: int
    end: bool


class RequestReset(BaseModel):
    user_id: str = "default"

    class Config:
        extra = "ignore"


class ResponseReset(BaseModel):
    result: bool
    face_type: int
    first_message: str


# ------------------------------------------------------------
# FastAPI アプリ作成
# ------------------------------------------------------------

app = FastAPI()

# Unity からのアクセスを許可（必要なら）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# 会話履歴管理 (簡易メモリ保存)
# ------------------------------------------------------------

chat_history_store: Dict[str, List[Dict[str, str]]] = {}
count_store: Dict[str, int] = {}  # user_idごとの回数カウント

MODEL_NAME = "hf.co/mmnga/Llama-3.1-Swallow-8B-Instruct-v0.5-gguf:latest"


# ------------------------------------------------------------
# LLM処理関数群（②から移植）
# ------------------------------------------------------------

def check_input_validity(text: str) -> bool:
    """
    入力文書が会話として適切かを評価する (True: 適切, False: 不適切)
    """
    prompt = f"""
    You are a content moderator. Analyze the following user input.
    If it contains offensive content, nonsense, or is completely inappropriate for a chat, reply with "INVALID".
    Otherwise, reply with "VALID".
    
    User Input: "{text}"
    Answer (VALID or INVALID):
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip().upper()
        return "VALID" in content
    except Exception as e:
        print(f"Validation Error: {e}")
        return True  # エラー時は一旦通す安全策


def generate_ai_response(history: List[Dict[str, str]]) -> str:
    """
    過去の会話履歴を踏まえて回答を生成する
    """
    try:
        system_prompt = {
            'role': 'system',
            'content': 'あなたは親切で役に立つAIアシスタントです。日本語で簡潔に答えてください。'
        }
        messages = [system_prompt] + history

        response = ollama.chat(model=MODEL_NAME, messages=messages)
        return response['message']['content']
    except Exception as e:
        print(f"Generate Error: {e}")
        return "申し訳ありません。エラーが発生しました。"


def evaluate_emotion(text: str) -> int:
    """
    回答テキストに基づいて表情用スコア(0-15)を生成する
    """
    prompt = f"""
    Analyze the sentiment of the following text and assign an integer score from 0 to 15.
    
    Scale definition:
    0-4: Sad, Apologetic, Negative
    5-9: Neutral, Calm, Informative
    10-15: Happy, Excited, Positive

    Text: "{text}"
    
    Return ONLY the integer number. Do not explain.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip()

        match = re.search(r'\d+', content)
        if match:
            score = int(match.group())
            return max(0, min(15, score))
        return 7
    except Exception as e:
        print(f"Emotion Error: {e}")
        return 7


def determine_state(user_text: str, ai_text: str) -> int:
    """
    ルールベースで状態(1-10)を決定する
    """
    if "さようなら" in user_text or "終了" in user_text:
        return 10
    elif "エラー" in ai_text:
        return 9
    elif "?" in user_text or "？" in user_text:
        return 2

    return 1


# ------------------------------------------------------------
# Unity用の変換レイヤ
#  emotion_score(0-15) -> face_type(0-3)
#  emotion_score(0-15) -> score(0-100)
# ------------------------------------------------------------

def emotion_to_face_type(emotion_score: int) -> int:
    """
    Unity側の表情IDに変換（仮ルール）
    0: 悲しい/困り, 1: ニュートラル, 2: ちょいポジ, 3: かなりポジ
    """
    if emotion_score <= 4:
        return 0
    elif emotion_score <= 9:
        return 1
    elif emotion_score <= 12:
        return 2
    else:
        return 3


def emotion_to_score(emotion_score: int) -> int:
    """
    Unity側のスコアに変換（仮ルール）
    0-15 を 0-100 に線形変換
    """
    return int(round(emotion_score / 15 * 100))


# ------------------------------------------------------------
# Unity の Transmitter から呼ばれるエンドポイント
# ------------------------------------------------------------

@app.post("/reset", response_model=ResponseReset)
async def reset(req: RequestReset):
    user_id = req.user_id or "default"

    # カウントと履歴をリセット
    count_store[user_id] = 0
    chat_history_store[user_id] = []

    return ResponseReset(result=True, first_message = "最初のメッセージ", face_type = 0)


@app.post("/send_message", response_model=ResponseSendPlayerMessage)
async def send_message(req: RequestSendPlayerMessage):
    print("▼ Received from Unity:")
    print(req.json())

    user_id = req.user_id or "default"
    user_message = req.message

    # カウント初期化
    if user_id not in count_store:
        count_store[user_id] = 0
    count_store[user_id] += 1

    # 1) 入力チェック
    is_valid = check_input_validity(user_message)
    if not is_valid:
        reply_text = "申し訳ありませんが、その入力には回答できません。"
        emotion_score = 2
        state_code = 9
    else:
        # 2) 履歴準備
        if user_id not in chat_history_store:
            chat_history_store[user_id] = []

        chat_history_store[user_id].append(
            {'role': 'user', 'content': user_message}
        )

        recent_history = chat_history_store[user_id][-20:]

        # 3) AI返答生成
        reply_text = generate_ai_response(recent_history)
        chat_history_store[user_id].append(
            {'role': 'assistant', 'content': reply_text}
        )

        # 4) 感情スコア
        emotion_score = evaluate_emotion(reply_text)

        # 5) 状態判定
        state_code = determine_state(user_message, reply_text)

    # Unity向けに変換
    face_type = emotion_to_face_type(emotion_score)
    score = emotion_to_score(emotion_score)

    # 終了判定：
    # - state_code==10（ユーザー終了ワード）
    # - 念のため max_message 超えたら終了（①の挙動も残す）
    max_message = 9999  # ①の3回終了を消したいなら大きく、残したいなら 3
    end_flag = (state_code == 10) or (count_store[user_id] >= max_message)

    return ResponseSendPlayerMessage(
        message=reply_text,
        face_type=face_type,
        score=score,
        end=end_flag
    )


# ------------------------------------------------------------
# アプリ起動
# ------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
