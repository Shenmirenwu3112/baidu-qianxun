let history = [];

const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("send");
const messagesEl = document.getElementById("messages");

sendBtn.onclick = handleSend;
inputEl.addEventListener("keypress", e => {
  if (e.key === "Enter") handleSend();
});

window.onload = () => inputEl.focus();

async function handleSend() {
  const text = inputEl.value.trim();
  if (!text) return;

  inputEl.value = "";
  inputEl.disabled = true;
  sendBtn.disabled = true;

  appendMessage("user", text);

  const loader = appendLoading();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text, history }),
    });

    const data = await res.json();
    history = data.history;

    // 替换 loading 为空容器
    const botBubble = document.createElement("div");
    botBubble.className = "msg bot";
    messagesEl.replaceChild(botBubble, loader);

    // 打字效果显示
    await typeText(botBubble, data.reply);

  } catch (err) {
    console.error("Error:", err);
    loader.innerText = "⚠️ 出错了，请稍后再试～";
  } finally {
    inputEl.disabled = false;
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

// 插入用户或机器人气泡
function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `msg ${role}`; // 外层用于对齐

  const bubble = document.createElement("div");
  bubble.className = "bubble"; // 内容气泡，宽度自动决定
  bubble.innerText = text;

  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  return bubble;
}


// 插入 loading 波浪动画
function appendLoading() {
  const div = document.createElement("div");
  div.className = "msg bot loading";
  div.innerHTML = `<span></span><span></span><span></span>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

// 打字机效果
async function typeText(element, text) {
  for (let i = 0; i < text.length; i++) {
    element.innerText += text[i];
    messagesEl.scrollTop = messagesEl.scrollHeight;
    await new Promise(resolve => setTimeout(resolve, 20)); // 控制打字速度
  }
}
