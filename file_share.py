import os
import webbrowser
import qrcode
from flask import Flask, send_file, send_from_directory, render_template_string
from pyngrok import ngrok
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

# Flask app setup
app = Flask(__name__)

# Selection variables
selected_path = ""
is_folder = False
public_url = ""

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
            text-align: center;
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
            padding: 10px;
        }
        .public-url {
            margin: 20px 0;
            font-weight: bold;
        }
        .qr-code img {
            width: 200px;
            height: 200px;
        }
        .file-list {
            text-align: left;
            display: inline-block;
            margin-top: 10px;
        }
        .file-list a {
            display: block;
            text-decoration: none;
            color: #007bff;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">File Share</div>
            <div class="card-body">
                <div class="public-url">
                    Public URL: <a href="{{ public_url }}" target="_blank">{{ public_url }}</a>
                </div>
                <div class="qr-code">
                    <p>Scan QR Code to Access:</p>
                    <img src="{{ qr_code_url }}" alt="QR Code">
                </div>
                {% if is_folder %}
                <div class="file-list">
                    <h3>Shared Files:</h3>
                    {% for file in files %}
                        <a href="{{ file }}" target="_blank">{{ file }}</a>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def file_page():
    if is_folder:
        files = [f"/download/{file}" for file in os.listdir(selected_path)]
    else:
        files = []
    return render_template_string(HTML_TEMPLATE, public_url=public_url, qr_code_url="/qr_code", is_folder=is_folder, files=files)

@app.route("/download/<filename>")
def download_from_folder(filename):
    return send_from_directory(selected_path, filename, as_attachment=True)

@app.route("/download")
def download_file():
    return send_file(selected_path, as_attachment=True)

@app.route("/qr_code")
def serve_qr():
    return send_file("qr_code.png", mimetype="image/png")

def generate_qr_code(url):
    """Generate and save a QR code for the given URL."""
    qr = qrcode.make(url)
    qr.save("qr_code.png")

def select_file_or_folder():
    """GUI for selecting a file or folder."""
    def browse_file():
        global selected_path, is_folder
        path = filedialog.askopenfilename()  # Select a file
        if path:
            selected_path = path
            is_folder = False
            path_entry.delete(0, ctk.END)
            path_entry.insert(0, selected_path)

    def browse_folder():
        global selected_path, is_folder
        path = filedialog.askdirectory()  # Select a folder
        if path:
            selected_path = path
            is_folder = True
            path_entry.delete(0, ctk.END)
            path_entry.insert(0, selected_path)

    def start_sharing():
        global public_url

        if not selected_path:
            status_label.configure(text="Please select a file or folder first!", text_color="red")
            return

        # Start ngrok and set public URL
        public_url = ngrok.connect(5000).public_url
        if is_folder:
            public_url += "/"  # Ensure it points to the folder view
        else:
            public_url += "/download"

        generate_qr_code(public_url)

        # Update UI with public URL and QR code
        url_label.configure(text=f"Public URL: {public_url}")

        # Load and display the QR code
        qr_img = Image.open("qr_code.png").resize((150, 150), Image.Resampling.LANCZOS)
        qr_image = ImageTk.PhotoImage(qr_img)
        qr_label.configure(image=qr_image, text="")
        qr_label.image = qr_image

        # Start Flask server (non-blocking)
        root.after(100, lambda: app.run(port=5000, use_reloader=False))

    # GUI Setup
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("File Share - Select File or Folder")
    root.geometry("500x500")

    # GUI Widgets
    header_label = ctk.CTkLabel(root, text="File Share Application", font=("Arial", 24, "bold"))
    header_label.pack(pady=10)

    path_entry = ctk.CTkEntry(root, width=300, placeholder_text="Select File or Folder")
    path_entry.pack(pady=10)

    browse_file_button = ctk.CTkButton(root, text="Browse File", command=browse_file)
    browse_file_button.pack(pady=5)

    browse_folder_button = ctk.CTkButton(root, text="Browse Folder", command=browse_folder)
    browse_folder_button.pack(pady=5)

    send_button = ctk.CTkButton(root, text="Start Sharing", command=start_sharing)
    send_button.pack(pady=10)

    # Public URL Display (Initially hidden)
    url_label = ctk.CTkLabel(root, text="Public URL: Not started yet", font=("Arial", 14))
    url_label.pack(pady=10)

    # QR Code Display (Initially empty)
    qr_label = ctk.CTkLabel(root, text="QR Code will appear here")
    qr_label.pack(pady=10)

    # Status Label (For errors)
    status_label = ctk.CTkLabel(root, text="", font=("Arial", 12))
    status_label.pack(pady=10)

    root.mainloop()

# Start GUI
if __name__ == "__main__":
    select_file_or_folder()
