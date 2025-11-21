import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import prompts  # prompts.py をインポート

app = FastAPI(title="Communication Evaluator API")

# 使用するモデル名
MODEL_NAME = "hf.co/mmnga/Llama-3.1-Swallow-8B-Instruct-v0.3-gguf:latest"

# リクエストボディの定義
class EvaluationRequest(BaseModel):
    before_response: str
    userinput1: str
    response1: str
    log: str

# レスポンスボディの定義
class EvaluationResponse(BaseModel):
    relevance: int  # 的確性
    clarity: int    # 論理性
    attitude: int   # 態度

def extract_score(text: str) -> int:
    """
    LLMの応答テキストから数字(1-5)を抽出するヘルパー関数
    想定外の文字が含まれていた場合の対策
    """
    match = re.search(r'[1-5]', text)
    if match:
        return int(match.group(0))
    else:
        # 数字が見つからない場合はエラー値として0またはデフォルト値(3など)を返す
        # ここではエラー扱いとして0とします
        return 0

def query_ollama(prompt_template: str, data: EvaluationRequest) -> int:
    """
    Ollamaに問い合わせてスコア(int)を返す
    """
    formatted_prompt = prompt_template.format(
        before_response=data.before_response,
        userinput1=data.userinput1,
        response1=data.response1,
        log=data.log
    )
    
    try:
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=formatted_prompt,
            options={"temperature": 0.0} # 評価の安定性のためランダム性を排除
        )
        raw_content = response['response'].strip()
        return extract_score(raw_content)
        
    except Exception as e:
        print(f"Ollama Error: {e}")
        # エラー時は0を返す、または例外をraiseする設計にする
        return 0

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest):
    """
    会話データをPOSTで受け取り、3観点の評価スコアを返す
    """
    
    # 1. 回答の的確性
    score_relevance = query_ollama(prompts.prompt_relevance, request)
    
    # 2. 論理性・わかりやすさ
    score_clarity = query_ollama(prompts.prompt_clarity, request)
    
    # 3. 態度・協調性
    score_attitude = query_ollama(prompts.prompt_attitude, request)

    return EvaluationResponse(
        relevance=score_relevance,
        clarity=score_clarity,
        attitude=score_attitude
    )

if __name__ == "__main__":
    import uvicorn
    # 開発用サーバー起動設定
    uvicorn.run(app, host="0.0.0.0", port=5000)