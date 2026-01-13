function generateNickname() {
  const adjectives = ["Angry", "Furious", "Irritated", "Salty", "Spicy", "Annoyed"];
  const animals = ["Fox", "Penguin", "Tiger", "Sloth", "Gorilla", "Panda"];
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
  const animal = animals[Math.floor(Math.random() * animals.length)];
  const num = Math.floor(Math.random() * 1000);
  return `${adj}${animal}${num}`;
}

function getNickname() {
  const NICKNAME_EXPIRY_MS = 10 * 60 * 1000; // 10 minutes

  console.log('[Nickname] Checking localStorage...');
  const stored = localStorage.getItem('rage_room_nickname');
  console.log('[Nickname] Stored data:', stored);

  if (stored) {
    try {
      const data = JSON.parse(stored);
      const now = Date.now();
      const age = now - data.timestamp;
      const remaining = NICKNAME_EXPIRY_MS - age;

      console.log('[Nickname] Parsed data:', data);
      console.log('[Nickname] Age (ms):', age);
      console.log('[Nickname] Remaining (ms):', remaining);

      // Check if nickname is still valid (less than 10 minutes old)
      if (remaining > 0) {
        console.log(`✅ Reusing nickname: ${data.nickname} (${Math.floor(remaining / 1000 / 60)} min ${Math.floor((remaining % 60000) / 1000)} sec remaining)`);
        return data.nickname;
      } else {
        console.log('⏰ Nickname expired, generating new one');
      }
    } catch (e) {
      console.log('❌ Invalid stored nickname, generating new one:', e);
    }
  } else {
    console.log('[Nickname] No stored nickname found');
  }

  // Generate new nickname and store it
  const newNickname = generateNickname();
  const data = {
    nickname: newNickname,
    timestamp: Date.now()
  };

  try {
    localStorage.setItem('rage_room_nickname', JSON.stringify(data));
    console.log(`✨ New nickname generated and stored: ${newNickname}`);
    console.log('[Nickname] Stored data:', JSON.stringify(data));
  } catch (e) {
    console.error('❌ Failed to store nickname in localStorage:', e);
  }

  return newNickname;
}

const nickname = getNickname();

// Update nickname display
function updateNicknameDisplay() {
  const NICKNAME_EXPIRY_MS = 10 * 60 * 1000; // 10 minutes
  const stored = localStorage.getItem('rage_room_nickname');

  if (stored) {
    try {
      const data = JSON.parse(stored);
      const now = Date.now();
      const elapsed = now - data.timestamp;
      const remaining = NICKNAME_EXPIRY_MS - elapsed;

      if (remaining > 0) {
        const minutes = Math.floor(remaining / 60000);
        const seconds = Math.floor((remaining % 60000) / 1000);

        document.getElementById('current-nickname').textContent = data.nickname;
        document.getElementById('nickname-timer').textContent = `(${minutes}:${seconds.toString().padStart(2, '0')})`;
      } else {
        // Nickname expired, reload to get new one
        location.reload();
      }
    } catch (e) {
      console.error('Error updating nickname display', e);
    }
  }
}

// Update timer every second
updateNicknameDisplay();
setInterval(updateNicknameDisplay, 1000);

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
  // Message history will be sent automatically by the server
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log("Received message:", msg);
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
