// ========== 登录 / 注册 切换 ==========
function switchMode(mode) {
  sessionStorage.setItem('authMode', mode);
  location.reload();
}

function switchSubTab(panel, sub) {
  const panelEl = document.getElementById(panel + 'Panel');
  if (!panelEl) return;

  panelEl.querySelectorAll('.sub-tab').forEach(tab => tab.classList.remove('active'));
  const targetTab = Array.from(panelEl.querySelectorAll('.sub-tab'))
    .find(tab => tab.textContent.includes(sub === 'sms' ? '短信' : '账号'));
  if (targetTab) targetTab.classList.add('active');

  panelEl.querySelectorAll('.sub-form').forEach(form => form.classList.remove('active'));
  const targetForm = panelEl.querySelector(`.sub-form[data-sub="${sub}"]`);
  if (targetForm) targetForm.classList.add('active');
}

(function initMode() {
  const mode = sessionStorage.getItem('authMode') || 'login';

  const loginPanel = document.getElementById('loginPanel');
  const registerPanel = document.getElementById('registerPanel');
  const loginTab = document.getElementById('loginTab');
  const registerTab = document.getElementById('registerTab');

  loginTab.classList.remove('active');
  registerTab.classList.remove('active');

  if (mode === 'register') {
    loginPanel.classList.remove('active');
    registerPanel.classList.add('active');
    registerTab.classList.add('active');
  } else {
    registerPanel.classList.remove('active');
    loginPanel.classList.add('active');
    loginTab.classList.add('active');
  }
})();

// ========== 密码显示切换 ==========
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon = btn.querySelector('i');
  if (!icon) return;
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.remove('far', 'fa-eye');
    icon.classList.add('far', 'fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.remove('far', 'fa-eye-slash');
    icon.classList.add('far', 'fa-eye');
  }
}

// ========== 验证工具 ==========
function isValidEmailOrPhone(value) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRegex = /^1[3-9]\d{9}$/;
  return emailRegex.test(value) || phoneRegex.test(value);
}

function clearAllMessages() {
  document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
  document.querySelectorAll('.success-message').forEach(el => el.classList.remove('show'));
}

// ========== 登录 ==========
async function handleLogin(e) {
  e.preventDefault();
  clearAllMessages();

  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value.trim();
  let isValid = true;

  if (!email) {
    const el = document.getElementById('loginEmailError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请输入邮箱或手机号';
    isValid = false;
  } else if (!isValidEmailOrPhone(email)) {
    const el = document.getElementById('loginEmailError');
    el.classList.add('show');
    el.querySelector('span').textContent = '邮箱或手机号格式不正确';
    isValid = false;
  }

  if (!password) {
    const el = document.getElementById('loginPasswordError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请输入密码';
    isValid = false;
  } else if (password.length < 6) {
    const el = document.getElementById('loginPasswordError');
    el.classList.add('show');
    el.querySelector('span').textContent = '密码不能少于6位';
    isValid = false;
  }

  if (isValid) {
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account: email,
          password: password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('nickname', data.nickname || '');
        document.getElementById('loginSuccess').classList.add('show');
        setTimeout(() => {
          document.getElementById('loginSuccess').classList.remove('show');
          showChat();
        }, 1000);
      } else {
        const el = document.getElementById('loginPasswordError');
        el.classList.add('show');
        el.querySelector('span').textContent = data.detail || '账号或密码错误';
      }
    } catch (err) {
      console.error(err);
      alert('无法连接服务器，请确认后端已启动（http://localhost:8000）');
    }
  }
}

// ========== 注册 ==========
async function handleRegister(e) {
  e.preventDefault();
  clearAllMessages();

  const name = document.getElementById('registerName').value.trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value.trim();
  const confirm = document.getElementById('registerConfirm').value.trim();
  const agree = document.getElementById('agreeTerms').checked;
  let isValid = true;

  if (!name) {
    const el = document.getElementById('registerNameError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请输入昵称';
    isValid = false;
  }

  if (!email) {
    const el = document.getElementById('registerEmailError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请输入邮箱或手机号';
    isValid = false;
  } else if (!isValidEmailOrPhone(email)) {
    const el = document.getElementById('registerEmailError');
    el.classList.add('show');
    el.querySelector('span').textContent = '邮箱或手机号格式不正确';
    isValid = false;
  }

  if (!password) {
    const el = document.getElementById('registerPasswordError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请输入密码';
    isValid = false;
  } else if (password.length < 6) {
    const el = document.getElementById('registerPasswordError');
    el.classList.add('show');
    el.querySelector('span').textContent = '密码不能少于6位';
    isValid = false;
  }

  if (!confirm) {
    const el = document.getElementById('registerConfirmError');
    el.classList.add('show');
    el.querySelector('span').textContent = '请再次输入密码';
    isValid = false;
  } else if (password !== confirm) {
    const el = document.getElementById('registerConfirmError');
    el.classList.add('show');
    el.querySelector('span').textContent = '两次密码不一致';
    isValid = false;
  }

  if (!agree) {
    document.getElementById('agreeError').classList.add('show');
    isValid = false;
  } else {
    document.getElementById('agreeError').classList.remove('show');
  }

  if (isValid) {
    try {
      const res = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nickname: name,
          account: email,
          password: password,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        document.getElementById('registerSuccess').classList.add('show');
        document.getElementById('registerForm').reset();
        setTimeout(() => {
          document.getElementById('registerSuccess').classList.remove('show');
          switchMode('login');
        }, 1500);
      } else {
        const el = document.getElementById('registerEmailError');
        el.classList.add('show');
        el.querySelector('span').textContent = data.detail || '注册失败';
      }
    } catch (err) {
      console.error(err);
      alert('无法连接服务器，请确认后端已启动（http://localhost:8000）');
    }
  }
}

// ========== 输入时清除错误 ==========
document.addEventListener('DOMContentLoaded', () => {
  const agreeTerms = document.getElementById('agreeTerms');
  if (agreeTerms) {
    agreeTerms.addEventListener('change', function () {
      if (this.checked) {
        document.getElementById('agreeError').classList.remove('show');
      }
    });
  }

  document.querySelectorAll('.input-field input').forEach(input => {
    input.addEventListener('input', function () {
      const parentGroup = this.closest('.input-group');
      if (parentGroup) {
        const error = parentGroup.querySelector('.error-message');
        if (error) error.classList.remove('show');
      }
    });
  });
});

// ========== 聊天功能 ==========
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const text = input.value.trim();

  if (!text) return;

  const token = localStorage.getItem('token');
  if (!token) {
    alert('登录已过期，请重新登录');
    logout();
    return;
  }

  appendMessage('user', text);
  input.value = '';

  const typingEl = appendTyping();
  sendBtn.disabled = true;

  try {
    // ⚠️ 调用 /agent/chat（Agent 接口）
    const res = await fetch('http://localhost:8000/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    typingEl.remove();

    if (res.ok) {
      // ⚠️ 过滤掉 "📖 来源" 部分（前端隐藏）
      let cleanReply = data.reply || '';
      const sourceIndex = cleanReply.indexOf('📖 来源:');
      if (sourceIndex !== -1) {
        cleanReply = cleanReply.substring(0, sourceIndex).trim();
      }
      appendMessage('bot', cleanReply);
    } else if (res.status === 401) {
      alert('登录已过期，请重新登录');
      logout();
    } else {
      appendMessage('bot', `抱歉，出错了：${data.detail || '未知错误'}`);
    }
  } catch (err) {
    typingEl.remove();
    appendMessage('bot', '网络错误，请检查后端是否启动');
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

function appendMessage(role, text) {
  const messagesEl = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendTyping() {
  const messagesEl = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message bot typing';
  div.innerHTML = `<div class="bubble"></div>`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ========== 界面切换 ==========
function showChat() {
  document.getElementById('authModal').style.display = 'none';
  document.getElementById('chatContainer').style.display = 'flex';
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('nickname');
  document.getElementById('chatContainer').style.display = 'none';
  document.getElementById('authModal').style.display = 'flex';
}

(function checkAuth() {
  const token = localStorage.getItem('token');
  if (token) {
    showChat();
  }
})();