# server.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# ------------------------------------------------------------
# Unity から飛んでくる JSON と合わせた Request/Response モデル
# ------------------------------------------------------------

class RequestSendPlayerMessage(BaseModel):
    message: str = ""


class ResponseSendPlayerMessage(BaseModel):
    message: str
    face_type: int
    score: int
    end: bool

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
# Unity の Transmitter から呼ばれるエンドポイント
# ------------------------------------------------------------

@app.post("/send_message", response_model=ResponseSendPlayerMessage)
async def send_message(req: RequestSendPlayerMessage):
    print("▼ Received from Unity:")
    print(req.json())

    # ダミーのレスポンス生成
    response = ResponseSendPlayerMessage(
        message="サーバからのダミー返信です！",
        face_type=1,
        score=10,
        end=False
    )

    return response


# ------------------------------------------------------------
# アプリ起動
# ------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)