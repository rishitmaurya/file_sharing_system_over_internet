import os
from flask import Flask, send_from_directory, render_template_string
from pyngrok import ngrok

SHARED_FOLDER = r"C:\\Users\\rishi\\OneDrive\\Pictures\\Camera Roll"  # Folder path
PORT = 5000

if not os.path.exists(SHARED_FOLDER):
    os.makedirs(SHARED_FOLDER)

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Share</title>
</head>
<body>
    <h2>Shared Files</h2>
    <ul>
        {% for file in files %}
            <li><a href="{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def list_files():
    files = os.listdir(SHARED_FOLDER)
    file_links = [f"/download/{file}" for file in files]
    return render_template_string(HTML_TEMPLATE, files=file_links)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)

# Start Flask and ngrok
if __name__ == "__main__":
    # Connect ngrok
    public_url = ngrok.connect(PORT).public_url
    print(f"Public URL: {public_url}")  # Share this link
    app.run(port=PORT)
