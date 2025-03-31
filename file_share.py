import os
import webbrowser
import qrcode
from flask import Flask, send_from_directory, render_template_string
from pyngrok import ngrok
import customtkinter as ctk
from tkinter import filedialog

# Default shared folder path
SHARED_FOLDER = r"C:\\Users\\Prince Soni\\Pictures\\Screenshots"
PORT = 5000

if not os.path.exists(SHARED_FOLDER):
    os.makedirs(SHARED_FOLDER)

app = Flask(__name__)

# HTML Template for Flask
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Share</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            font-family: Arial, sans-serif;
        }
        .container {
            margin-top: 50px;
        }
        .file-list a {
            text-decoration: none;
            color: #007bff;
        }
        .file-list a:hover {
            text-decoration: underline;
        }
        .card {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }
        .card-header {
            font-size: 24px;
            font-weight: bold;
            background-color: #007bff;
            color: white;
            text-align: center;
        }
        .public-url {
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
        }
        .qr-code {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                Shared Files
            </div>
            <div class="card-body">
                <div class="public-url">
                    Public URL: <a href="{{ public_url }}" target="_blank">{{ public_url }}</a>
                </div>
                <div class="qr-code">
                    <p>Scan QR Code to Access:</p>
                    <img src="{{ qr_code_url }}" alt="QR Code">
                </div>
                <ul class="list-group file-list">
                    {% for file in files %}
                        <li class="list-group-item">
                            <a href="{{ file }}">{{ file }}</a>
                        </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def list_files():
    files = os.listdir(SHARED_FOLDER)
    file_links = [f"/download/{file}" for file in files]
    return render_template_string(HTML_TEMPLATE, files=file_links, public_url=public_url, qr_code_url="/qr_code")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)

@app.route("/qr_code")
def serve_qr():
    return send_from_directory(os.getcwd(), "qr_code.png", as_attachment=False)

def generate_qr_code(url):
    qr = qrcode.make(url)
    qr.save("qr_code.png")

def select_folder():
    """Enhanced GUI with customtkinter."""
    def browse_folder():
        global SHARED_FOLDER
        folder_path = filedialog.askdirectory()
        if folder_path:
            SHARED_FOLDER = folder_path
            folder_entry.delete(0, ctk.END)
            folder_entry.insert(0, folder_path)

    def start_server():
        root.destroy()
        webbrowser.open(f"http://localhost:{PORT}")
        app.run(port=PORT)

    # GUI Setup
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("File Share - Folder Selection")
    root.geometry("500x300")

    # GUI Widgets
    header_label = ctk.CTkLabel(root, text="File Share Application", font=("Arial", 24, "bold"))
    header_label.pack(pady=20)

    folder_entry = ctk.CTkEntry(root, width=300, placeholder_text="Select Folder")
    folder_entry.pack(pady=10)

    browse_button = ctk.CTkButton(root, text="Browse", command=browse_folder)
    browse_button.pack(pady=5)

    send_button = ctk.CTkButton(root, text="Start Sharing", command=start_server)
    send_button.pack(pady=20)

    root.mainloop()

# Start Flask and ngrok
if __name__ == "__main__":
    public_url = ngrok.connect(PORT).public_url
    print(f"Public URL: {public_url}")
    generate_qr_code(public_url)
    select_folder()
