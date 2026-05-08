import re

with open('run.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all @app.route("/...") with @app.route("/api/...") except for "/", "/api", "/assets", and catch_all
def replacer(match):
    path = match.group(1)
    if path in ['/', '/api', '/<path:path>'] or path.startswith('/assets'):
        return match.group(0)
    return f'@app.route("/api{path}"'

new_content = re.sub(r'@app\.route\("(/.*?)"', replacer, content)

with open('run.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated run.py")
