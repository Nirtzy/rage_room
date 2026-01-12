function generateNickname() {
  const adjectives = ["Angry", "Furious", "Irritated", "Salty", "Spicy", "Annoyed"];
  const animals = ["Fox", "Penguin", "Tiger", "Sloth", "Gorilla", "Panda"];
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
  const animal = animals[Math.floor(Math.random() * animals.length)];
  const num = Math.floor(Math.random() * 1000);
  return `${adj}${animal}${num}`;
}

const nickname = generateNickname();

// Elements
const chatWindow = document.getElementById("chat-window");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

// Load today's headline
async function loadHeadline() {
  try {
    const res = await fetch("/api/today");
    const data = await res.json();

    document.getElementById("headline-title").textContent = data.title;
    document.getElementById("headline-subtitle").textContent = data.subtitle || "";
  } catch (err) {
    console.error("Failed to load headline", err);
  }
}

// Determine WS URL (works locally & on Render)
const loc = window.location;
let wsProtocol = loc.protocol === "https:" ? "wss:" : "ws:";
let wsUrl = `${wsProtocol}//${loc.host}/ws`;

const ws = new WebSocket(wsUrl);

ws.onopen = () => {
  console.log("WebSocket connected");
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  addMessage(msg);
};

ws.onclose = () => {
  console.log("WebSocket closed");
};

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  const msg = {
    user: nickname,
    text,
    timestamp: new Date().toISOString(),
  };

  ws.send(JSON.stringify(msg));
  input.value = "";
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

function addMessage(msg) {
  const div = document.createElement("div");
  div.className = "chat-message";

  const userSpan = document.createElement("span");
  userSpan.className = "chat-user";
  userSpan.textContent = msg.user + ": ";

  const textSpan = document.createElement("span");
  textSpan.className = "chat-text";
  textSpan.textContent = msg.text;

  div.appendChild(userSpan);
  div.appendChild(textSpan);

  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Initialize
loadHeadline();