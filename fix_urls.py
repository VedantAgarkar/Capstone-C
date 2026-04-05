import os

files = [
    'frontend/js/bot.js',
    'frontend/js/diabetes.js',
    'frontend/js/heart.js',
    'frontend/js/parkinsons.js',
    'frontend/js/dashboard.js',
    'frontend/js/login.js',
    'frontend/js/signup.js'
]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace API_BASE = '' with the new logic
    logic = "const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://your-render-backend-url.onrender.com';"
    content = content.replace("const API_BASE = '';", logic)
    content = content.replace('const API_BASE = "";', logic)
    content = content.replace("const API_BASE = ''; ", logic)
    
    # Replace hardcoded localhost in fetch
    content = content.replace('http://localhost:8000/api', '${API_BASE}/api')
    content = content.replace('"http://localhost:8000/api', '`${API_BASE}/api')
    content = content.replace('\'http://localhost:8000/api', '`${API_BASE}/api')
    content = content.replace('`http://localhost:8000/api', '`${API_BASE}/api')
    # Fix quotes if they ended up like '${API_BASE}/api/login' (single quoted generic template)
    content = content.replace("'${API_BASE}/api/login'", "`${API_BASE}/api/login`")
    content = content.replace("'${API_BASE}/api/register'", "`${API_BASE}/api/register`")
    
    # Add API_BASE if not exists in dashboard, login, signup
    if 'const API_BASE' not in content:
        content = logic + "\n" + content
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print('Done editing JS files')
