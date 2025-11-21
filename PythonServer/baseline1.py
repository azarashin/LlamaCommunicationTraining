import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from typing import List, Dict
import re

app = FastAPI()

# =========================
# 設定（回数・コンテキスト）
# =========================
MAX_TURNS = 10          # 返答を作成する最大回数
CONTEXT_TURNS = 10      # コンテキストに入れる往復数（10往復）

# =========================
# モデル設定（役割ごとに分離）
# =========================
MODEL_NAME_MODERATION = "llama3.2"      # 入力妥当性チェック用（変更したければここ）
MODEL_NAME_REPLY      = "3.1swallow-8B" # 返答生成用
MODEL_NAME_EMOTION    = "3.1swallow 8B" # 表情推定用（空白あってもOKにする）

def normalize_model_name(name: str) -> str:
    """
    Ollamaのモデル名は空白なしのことが多いので、念のため正規化
    例: "3.1swallow 8B" -> "3.1swallow-8B"
    """
    return name.strip().replace(" ", "-")


# --- データモデル定義 ---

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply_text: str
    emotion_score: int
    state_code: int
    end: bool


# --- 会話履歴管理 (簡易メモリ保存) ---
chat_history_store: Dict[str, List[Dict[str, str]]] = {}
turn_count_store: Dict[str, int] = {}
end_flag_store: Dict[str, bool] = {}


# --- LLM処理関数群 ---

def check_input_validity(text: str) -> bool:
    """
    入力文書が会話として適切かを評価する (True: 適切, False: 不適切)
    ※ モデレーション専用モデルを使用
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
            model=normalize_model_name(MODEL_NAME_MODERATION),
            messages=[{'role': 'user', 'content': prompt}]
        )
        content = response['message']['content'].strip().upper()
        return "VALID" in content
    except Exception as e:
        print(f"Validation Error: {e}")
        return True


def generate_ai_response(history: List[Dict[str, str]]) -> str:
    """
    過去の会話履歴を踏まえて回答を生成する
    ※ 返答生成専用モデルを使用
    """
    try:
        system_prompt = {
            'role': 'system',
            'content': 'あなたは親切で役に立つAIアシスタントです。日本語で簡潔に答えてください。'
        }
        messages = [system_prompt] + history
        
        response = ollama.chat(
            model=normalize_model_name(MODEL_NAME_REPLY),
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        print(f"Generate Error: {e}")
        return "申し訳ありません。エラーが発生しました。"


def evaluate_emotion(text: str) -> int:
    """
    回答テキストに基づいて表情用スコア(0-15)を生成する
    ※ 表情推定専用モデルを使用
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
            model=normalize_model_name(MODEL_NAME_EMOTION),
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


# --- ルールベース処理 ---

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


# --- APIエンドポイント ---

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message

    # 初期化
    if user_id not in chat_history_store:
        chat_history_store[user_id] = []
    if user_id not in turn_count_store:
        turn_count_store[user_id] = 0
    if user_id not in end_flag_store:
        end_flag_store[user_id] = False

    # 0) すでに終了してたら返答を作らない
    if end_flag_store[user_id]:
        reply_text = "この会話はすでに終了しています。最初からやり直す場合はリセットしてください。"
        emotion_score = 5
        return ChatResponse(
            reply_text=reply_text,
            emotion_score=emotion_score,
            state_code=10,
            end=True
        )

    # 1) 入力内容の評価 (AI)
    is_valid = check_input_validity(user_message)
    if not is_valid:
        reply_text = "申し訳ありませんが、その入力には回答できません。"
        emotion_score = 2
        return ChatResponse(
            reply_text=reply_text,
            emotion_score=emotion_score,
            state_code=9,
            end=False
        )

    # 2) 履歴にユーザー入力を追加
    chat_history_store[user_id].append({'role': 'user', 'content': user_message})

    # コンテキストは「直近10往復分」だけ使う
    recent_history = chat_history_store[user_id][-2 * CONTEXT_TURNS:]

    # 3) 返答生成（最大10回）
    if turn_count_store[user_id] >= MAX_TURNS:
        end_flag_store[user_id] = True
        reply_text = "会話回数の上限に達したので終了します。"
        emotion_score = 5
        return ChatResponse(
            reply_text=reply_text,
            emotion_score=emotion_score,
            state_code=10,
            end=True
        )

    reply_text = generate_ai_response(recent_history)
    chat_history_store[user_id].append({'role': 'assistant', 'content': reply_text})

    turn_count_store[user_id] += 1

    # 4) 表情スコア算出（応答内容ベース）
    emotion_score = evaluate_emotion(reply_text)

    # 5) 状態判定 → 終了判定
    state_code = determine_state(user_message, reply_text)
    end_flag = (state_code == 10) or (turn_count_store[user_id] >= MAX_TURNS)

    end_flag_store[user_id] = end_flag

    # 6) レスポンス返却
    return ChatResponse(
        reply_text=reply_text,
        emotion_score=emotion_score,
        state_code=state_code,
        end=end_flag
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
