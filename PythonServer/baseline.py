import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from typing import List, Dict, Optional

app = FastAPI()

# --- データモデル定義 ---

# UIからの入力データ形式
class ChatRequest(BaseModel):
    user_id: str       # 会話履歴を管理するためのID
    message: str       # ユーザーの入力テキスト

# UIへの返却データ形式
class ChatResponse(BaseModel):
    reply_text: str    # AIからの回答
    emotion_score: int # 0-15の表情点数
    state_code: int    # 1-10の状態コード

# --- 会話履歴管理 (簡易メモリ保存) ---
# 本番運用ではRedisやDBへの保存を推奨します
chat_history_store: Dict[str, List[Dict[str, str]]] = {}

# --- LLM処理関数群 ---

MODEL_NAME = "llama3.2"

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
        response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content'].strip().upper()
        return "VALID" in content
    except Exception as e:
        print(f"Validation Error: {e}")
        return True # エラー時は一旦通す安全策

def generate_ai_response(history: List[Dict[str, str]]) -> str:
    """
    過去の会話履歴を踏まえて回答を生成する
    """
    try:
        # システムプロンプトを先頭に追加（キャラ設定など）
        system_prompt = {
            'role': 'system',
            'content': 'あなたは親切で役に立つAIアシスタントです。日本語で簡潔に答えてください。'
        }
        messages = [system_prompt] + history
        
        response = ollama.chat(model=MODEL_NAME, messages=messages)
        return response['message']['content']
    except Exception as e:
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
        response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content'].strip()
        
        # 数字以外が含まれている場合に備えて抽出
        import re
        match = re.search(r'\d+', content)
        if match:
            score = int(match.group())
            # 0-15の範囲に収める
            return max(0, min(15, score))
        return 7 # デフォルト値（ニュートラル）
    except Exception as e:
        print(f"Emotion Error: {e}")
        return 7

# --- ルールベース処理 ---

def determine_state(user_text: str, ai_text: str) -> int:
    """
    ルールベースで状態(1-10)を決定する
    """
    # 例: 特定のキーワードが含まれていたら状態を変える
    if "さようなら" in user_text or "終了" in user_text:
        return 10 # 終了状態
    elif "エラー" in ai_text:
        return 9  # エラー状態
    elif "?" in user_text or "？" in user_text:
        return 2  # 質問状態
    
    # デフォルト状態
    return 1

# --- APIエンドポイント ---

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message

    # 1. 入力内容の評価 (AI)
    is_valid = check_input_validity(user_message)
    
    if not is_valid:
        # 不適切な入力の場合の即時返却
        return ChatResponse(
            reply_text="申し訳ありませんが、その入力には回答できません。",
            emotion_score=2, # 困り顔/悲しみ
            state_code=9     # エラーまたは警告状態
        )

    # 2. 会話履歴の取得と更新
    if user_id not in chat_history_store:
        chat_history_store[user_id] = []
    
    # 履歴にユーザー入力を追加
    chat_history_store[user_id].append({'role': 'user', 'content': user_message})

    # 3. AIによる回答生成 (過去履歴参照) (AI)
    # コンテキストウィンドウ制御のため、最新の10往復程度に制限するのが一般的
    recent_history = chat_history_store[user_id][-20:] 
    reply_text = generate_ai_response(recent_history)

    # 履歴にAI回答を追加
    chat_history_store[user_id].append({'role': 'assistant', 'content': reply_text})

    # 4. 回答に対する表情スコア算出 (AI)
    emotion_score = evaluate_emotion(reply_text)

    # 5. ルールベースの状態判定
    state_code = determine_state(user_message, reply_text)

    # 6. レスポンス返却
    return ChatResponse(
        reply_text=reply_text,
        emotion_score=emotion_score,
        state_code=state_code
    )

if __name__ == "__main__":
    # サーバー起動
    # python main.py で実行
    uvicorn.run(app, host="0.0.0.0", port=8000)