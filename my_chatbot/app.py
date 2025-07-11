import os
import time
import jwt
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder="static", template_folder="templates")

API_KEY = os.environ.get("API_KEY", "686f18704c78b04e5af33978.DODekikfIgRQYtSGl+eS0NS3T3ohROGT")
APP_ID  = os.environ.get("APP_ID",  "68677beeb381ac407d4fe27d")
JWT_EXP = 3600*24*30  # token 有效期

def generate_token(apikey: str, exp_seconds: int):
    id, secret = apikey.split(".")
    payload = {
        "api_key": id,
        "exp": int(time.time()) + exp_seconds,
        "timestamp": int(time.time()),
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg":"HS256","typ":"JWT","sign_type":"SIGN"},
    )

# 先生成并缓存一份 token
JWT_TOKEN = generate_token(API_KEY, JWT_EXP)
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JWT_TOKEN}"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("prompt", "")
    history = data.get("history", [])

    payload = {
        "appId": APP_ID,
        "prompt": user_message,
        "history": history,
        "stream": False
    }


    # 重试逻辑
    while True:
        resp = requests.post(
            "https://jiutian.10086.cn/largemodel/api/v2/completions",
            json=payload,
            headers=HEADERS
        )
        if resp.status_code != 200:
            time.sleep(0.5)
            continue
        j = resp.json()
        if j.get("code") == 500:
            time.sleep(0.5)
            continue
        break
    # print(j)

    ai_reply = j["choices"][0]["text"]
    history.append([user_message, ai_reply])

    print(payload['history'])

    return jsonify({"reply": ai_reply, "history": history})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
