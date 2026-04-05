// JavaScript for Medical AI Bot

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://healthpredict-i5qi.onrender.com';
const messages = [];  // Conversation history

// Welcome messages
const lang = localStorage.getItem('healthpredict_lang') || 'en';
const welcome = lang === 'mr'
  ? '👋 नमस्कार! मी हृदय आरोग्य, मधुमेह, पार्किन्सन रोग आणि सामान्य वैद्यकीय प्रश्नांबद्दल माहिती देऊ शकतो. कृपया लक्षात ठेवा: मी व्यावसायिक वैद्यकीय सल्ल्याचा पर्याय नाही. तुम्हाला काय जाणून घ्यायला आवडेल?'
  : "👋 Hello! I can provide information about heart health, diabetes, Parkinson's disease, and general medical questions. Please note: I'm not a substitute for professional medical advice. What would you like to know?";

// Initialize chat
document.addEventListener('DOMContentLoaded', () => {
    // Sync UI with Marathi if needed
    if (lang === 'mr') {
        document.getElementById('sidebarTitle').textContent = '🤖 वैद्यकीय एआय बॉट';
        document.getElementById('sidebarSubtitle').textContent = 'हृदय आरोग्य, मधुमेह किंवा पार्किन्सन बाबत विचारा.';
        document.querySelector('.disclaimer').innerHTML = '<strong>अस्वीकरण:</strong> हा बॉट माहिती पुरवतो, वैद्यकीय सल्ला नाही. आपत्कालीन परिस्थितीत कृपया डॉक्टरांशी संपर्क साधा.';
        document.getElementById('clearBtn').textContent = '🗑️ चॅट साफ करा';
        document.getElementById('chatInput').placeholder = 'वैद्यकीय प्रश्न विचारा... (पाठवण्यासाठी Enter दाबा)';
        document.getElementById('sendBtn').textContent = 'पाठवा ➤';
    }

    messages.push({ role: 'assistant', content: welcome });
    appendBubble('bot', welcome);
});

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    input.style.height = 'auto';

    appendBubble('user', text);
    messages.push({ role: 'user', content: text });

    const typingId = showTyping();

    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ messages, lang })
        });
        
        removeTyping(typingId);
        
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();

        // Simulate typing animation
        await typeOutMessage(data.reply);
        messages.push({ role: 'assistant', content: data.reply });

    } catch (err) {
        removeTyping(typingId);
        appendBubble('bot', '❌ Failed to get a response. Please try again.');
        console.error(err);
    }
}

async function typeOutMessage(text) {
    const bubble = appendBubble('bot', '');
    const words = text.split(' ');
    let displayed = '';
    
    for (const word of words) {
        displayed += word + ' ';
        bubble.innerHTML = renderMarkdown(displayed) + '<span class="cursor">▌</span>';
        scrollToBottom();
        await sleep(30); 
    }
    bubble.innerHTML = renderMarkdown(text); 
}

function appendBubble(role, html) {
    const win = document.getElementById('chatWindow');
    const div = document.createElement('div');
    div.className = `message-bubble ${role === 'user' ? 'from-user' : 'from-bot'}`;
    div.innerHTML = html ? renderMarkdown(html) : '';
    win.appendChild(div);
    scrollToBottom();
    return div;
}

function showTyping() {
    const win = document.getElementById('chatWindow');
    const div = document.createElement('div');
    div.className = 'message-bubble from-bot typing-bubble';
    const id = 'typing-' + Date.now();
    div.id = id;
    div.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    win.appendChild(div);
    scrollToBottom();
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    const win = document.getElementById('chatWindow');
    win.scrollTop = win.scrollHeight;
}

function sleep(ms) { 
    return new Promise(r => setTimeout(r, ms)); 
}

function renderMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^## (.*$)/gm, '<h3>$1</h3>')
        .replace(/^- (.*$)/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
        .replace(/\n\n+/g, '</p><p>')
        .replace(/\n/g, '<br>');
}

// Event Listeners
document.getElementById('sendBtn').addEventListener('click', sendMessage);

document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { 
        e.preventDefault(); 
        sendMessage(); 
    }
});

document.getElementById('chatInput').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

document.getElementById('clearBtn')?.addEventListener('click', () => {
    messages.length = 0;
    messages.push({ role: 'assistant', content: welcome });
    
    const win = document.getElementById('chatWindow');
    while (win.children.length > 0) {
        win.removeChild(win.lastChild);
    }
    
    appendBubble('bot', welcome);
});
