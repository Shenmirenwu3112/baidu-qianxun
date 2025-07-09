import time, jwt, requests, gradio as gr

# 生成 JWT 的函数（同你原版）
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
        headers={"alg": "HS256", "typ": "JWT", "sign_type": "SIGN"},
    )

# 在环境变量或直接填这里
API_KEY = "YOUR.APIKEY.HERE"
APP_ID  = "66054825b6bd1705872b27a8"
TOKEN   = generate_token(API_KEY, 3600)
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}

# 聊天函数
def chat_fn(user_message, history):
    history = history or []
    history.append({"role": "user", "content": user_message})

    payload = {
        "appId": APP_ID,
        "prompt": user_message,
        "history": history,
        "stream": False
    }
    resp = requests.post(
        "https://jiutian.10086.cn/largemodel/api/v2/completions",
        json=payload,
        headers=HEADERS
    )
    data = resp.json()
    # 提取回复（根据返回结构）
    ai_reply = data.get("result") or data["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": ai_reply})
    return ai_reply, history

# 启动 Gradio 界面，并自动生成公网链接 share=True
if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=chat_fn,
        title="AI Agent 聊天",
        description="点下面输入框提问，AI 会结合上下文回答",
    )
    demo.launch(share=True)
