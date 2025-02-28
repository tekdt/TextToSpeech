from gtts import gTTS
import os
import threading
import pydub
from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox
import time
import random
import sys
import traceback

# LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "debug_log.txt")
LOG_FILE = ("debug_log.txt")

def log_error(error_message):
    """Ghi log lỗi vào file để kiểm tra sau khi chạy EXE."""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")

# Xác định thư mục chứa file EXE
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Chạy dưới dạng EXE
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chạy bằng Python script

# Xác định đường dẫn FFmpeg
FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg", "bin")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
FFPLAY_PATH = os.path.join(FFMPEG_DIR, "ffplay.exe")
FFPROBE_PATH = os.path.join(FFMPEG_DIR, "ffprobe.exe")

# Kiểm tra xem file ffmpeg có tồn tại không
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(f"Không tìm thấy ffmpeg tại {FFMPEG_PATH}")

# Thêm thư mục ffmpeg vào PATH để đảm bảo subprocess có thể gọi được
os.environ["PATH"] += os.pathsep + FFMPEG_DIR

# Ghi log kiểm tra file FFmpeg
for path, name in [(FFMPEG_PATH, "FFMPEG"), (FFPLAY_PATH, "FFPLAY"), (FFPROBE_PATH, "FFPROBE")]:
    if os.path.exists(path):
        log_error(f"Đã tìm thấy {name}_PATH tại: {path}")
    else:
        log_error(f"{name}_PATH không tồn tại tại: {path}")

# Cấu hình pydub
pydub.AudioSegment.converter = FFMPEG_PATH
pydub.AudioSegment.ffmpeg = FFMPEG_PATH
pydub.AudioSegment.ffplay = FFPLAY_PATH
pydub.AudioSegment.ffprobe = FFPROBE_PATH

# Các hàm xử lý tiếp tục không thay đổi...


def change_audio_speed(input_file, output_file, speed, format):
    try:
        input_file = os.path.abspath(input_file)
        output_file = os.path.abspath(output_file)

        log_error(f"Nhận file âm thanh: {input_file}")
        log_error(f"Xuất file âm thanh: {output_file}")
        log_error(f"Định dạng: {format} - Tốc độ: {speed}")

        if not os.path.exists(input_file):
            log_error(f"LỖI: File đầu vào không tồn tại - {input_file}")
            return
        
        audio = AudioSegment.from_file(input_file)
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)

        audio.export(output_file, format=format)
        log_error("Chuyển đổi âm thanh hoàn tất.")

    except Exception as e:
        log_error(f"LỖI trong change_audio_speed: {traceback.format_exc()}")


def update_progress(value):
    progress_var.set(value)
    progress_label.config(text=f"Đang xử lý: {value}%")
    root.update_idletasks()

# def ask_questions():
    # questions = [
        # "(Câu hỏi chỉ dành cho Bảo Bối ♥♥♥ thôi nha) Em yêu Anh nhiều lắm mà đúng hơm nhỉ?",
        # "(Câu hỏi chỉ dành cho Bảo Bối ♥♥♥ thôi nha) Bảo Bối yêu Anh nhiều hơm?",
        # "(Câu hỏi chỉ dành cho Bảo Bối ♥♥♥ thôi nha) Em có biết Anh yêu Em nhiều lắm hong?"
    # ]
    # question = random.choice(questions)
    # return messagebox.askyesno("Xác nhận", question)

root = tk.Tk()
root.title("Text To Speech Unlimited - TekDT")

# if not ask_questions():
    # root.destroy()
    # exit()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(pady=20)

def text_to_speech(input_file, output_dir, lang, speed=1.0, output_format="mp3", voice="female"):
    try:
        log_error(f"Nhận file văn bản: {input_file}")
        log_error(f"Thư mục đầu ra: {output_dir}")
        log_error(f"Ngôn ngữ: {lang} - Giọng: {voice} - Định dạng: {output_format}")

        input_file = os.path.abspath(input_file)
        output_dir = os.path.abspath(output_dir)        

        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read()
        
        if not text.strip():
            log_error("LỖI: File văn bản trống.")
            messagebox.showerror("Lỗi", "File trống, không có nội dung để chuyển đổi.")
            return
        
        update_progress(10)

        tld = "com" if voice == "female" else "co.uk"
        tts = gTTS(text=text, lang=lang, tld=tld)
        temp_file = os.path.abspath("temp_audio.mp3")
        tts.save(temp_file)

        log_error(f"File tạm thời đã được tạo: {temp_file}")

        update_progress(50)

        file_name = os.path.splitext(os.path.basename(input_file))[0] + f"_output.{output_format}"
        output_file = os.path.join(output_dir, file_name)
        log_error(f"File đầu ra dự kiến: {output_file}")

        if not os.path.exists(output_dir):
            log_error(f"LỖI: Thư mục đầu ra không tồn tại - {output_dir}")
            return

        change_audio_speed(temp_file, output_file, speed, output_format)

        os.remove(temp_file)
        log_error(f"Đã xóa file tạm: {temp_file}")

        for i in range(51, 101, 5):
            update_progress(i)
            time.sleep(0.1)

        messagebox.showinfo("Thành công", f"File âm thanh đã được lưu: {output_file}")
        log_error(f"Hoàn thành. File đã lưu tại: {output_file}")

        update_progress(0)

    except Exception as e:
        log_error(f"LỖI trong text_to_speech: {traceback.format_exc()}")
        messagebox.showerror("Lỗi", str(e))
        update_progress(0)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def select_output_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_output_dir.delete(0, tk.END)
        entry_output_dir.insert(0, folder_selected)

def generate_audio():
    input_file = entry_file.get()
    output_dir = entry_output_dir.get()
    speed = float(speed_var.get())
    output_format = format_var.get()
    voice = voice_var.get()
    lang = lang_var.get()
    if not output_dir:
        messagebox.showerror("Lỗi", "Vui lòng chọn thư mục lưu file.")
        return
    
    thread = threading.Thread(target=text_to_speech, args=(input_file, output_dir, lang, speed, output_format, voice))
    thread.start()
    
def show_info():
    info_text = "Text To Speech Unlimited - TekDT\nVersion: 1.0\nTác giả: TekDT\nEmail: dinhtrungtek@gmail.com\nMô tả: Chuyển đổi văn bản thành giọng nói không giới hạn với nhiều tùy chọn ngôn ngữ và tốc độ."
    messagebox.showinfo("Thông tin phần mềm", info_text)

tk.Label(frame, text="Chọn file văn bản:").grid(row=0, column=0)
entry_file = tk.Entry(frame, width=50)
entry_file.grid(row=0, column=1)
tk.Button(frame, text="Duyệt...", command=open_file).grid(row=0, column=2)

tk.Label(frame, text="Chọn thư mục lưu:").grid(row=1, column=0)
entry_output_dir = tk.Entry(frame, width=50)
entry_output_dir.grid(row=1, column=1)
tk.Button(frame, text="Duyệt...", command=select_output_directory).grid(row=1, column=2)

tk.Label(frame, text="Tốc độ đọc (0.5 - 2.0):").grid(row=2, column=0)
speed_var = tk.StringVar(value="1.0")
tk.Entry(frame, textvariable=speed_var, width=10).grid(row=2, column=1)

tk.Label(frame, text="Định dạng đầu ra:").grid(row=3, column=0)
format_var = tk.StringVar(value="mp3")
format_combobox = Combobox(frame, textvariable=format_var, values=["mp3", "wav", "ogg", "flac"])
format_combobox.grid(row=3, column=1)
format_combobox.current(0)

tk.Label(frame, text="Giọng đọc:").grid(row=4, column=0)
voice_var = tk.StringVar(value="female")
voice_combobox = Combobox(frame, textvariable=voice_var, values=["female", "male"])
voice_combobox.grid(row=4, column=1)
voice_combobox.current(0)

tk.Label(frame, text="Ngôn ngữ đọc:").grid(row=5, column=0)
lang_var = tk.StringVar(value="vi")
lang_combobox = Combobox(frame, textvariable=lang_var, values=["vi", "en", "fr", "de", "es", "it", "ja", "ko", "zh-cn"])
lang_combobox.grid(row=5, column=1)
lang_combobox.current(0)

tk.Button(frame, text="Chuyển đổi", command=generate_audio).grid(row=6, column=0, columnspan=3, pady=10)

progress_var = tk.IntVar()
progress_bar = Progressbar(root, length=300, mode='determinate', variable=progress_var)
progress_bar.pack(pady=10)

progress_label = tk.Label(root, text="Đang xử lý: 0%")
progress_label.pack()

# Thêm nút Thông tin vào giao diện
info_button = tk.Button(root, text="Thông tin", command=show_info)
info_button.pack(pady=5)

root.mainloop()