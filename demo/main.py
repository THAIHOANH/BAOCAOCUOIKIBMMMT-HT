import tkinter as tk
from tkinter import messagebox, filedialog
import rsa  # type: ignore
import base64
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF

from playfair_gui import open_playfair_window
from rsa_gui import open_rsa_window

# ============================
# PlayFair Helper
# ============================
def number_to_text(num_str):
    num_dict = {"0": "ZERO", "1": "ONE", "2": "TWO", "3": "THREE", "4": "FOUR",
                "5": "FIVE", "6": "SIX", "7": "SEVEN", "8": "EIGHT", "9": "NINE"}
    return "".join(num_dict[digit] for digit in num_str)

def prepare_text_for_playfair(text):
    text = text.upper().replace('J', 'I').replace(" ", "")
    result = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char.isdigit():
            num = ""
            while i < len(text) and text[i].isdigit():
                num += text[i]
                i += 1
            result += number_to_text(num)
        else:
            result += char
            i += 1
    return result

def generate_matrix(key):
    key = key.upper().replace('J', 'I')
    result = []
    for c in key:
        if c not in result and c.isalpha():
            result.append(c)
    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in result:
            result.append(c)
    return [result[i:i+5] for i in range(0, 25, 5)]

def find_position(matrix, letter):
    for i, row in enumerate(matrix):
        for j, char in enumerate(row):
            if char == letter:
                return i, j
    return None

def playfair_encrypt(text, matrix):
    text = prepare_text_for_playfair(text)
    i = 0
    result = []
    while i < len(text):
        a = text[i]
        b = text[i+1] if i+1 < len(text) else 'X'
        if a == b:
            b = 'X'
            i += 1
        else:
            i += 2
        row1, col1 = find_position(matrix, a)
        row2, col2 = find_position(matrix, b)

        if row1 == row2:
            result.append(matrix[row1][(col1+1)%5])
            result.append(matrix[row2][(col2+1)%5])
        elif col1 == col2:
            result.append(matrix[(row1+1)%5][col1])
            result.append(matrix[(row2+1)%5][col2])
        else:
            result.append(matrix[row1][col2])
            result.append(matrix[row2][col1])
    return ''.join(result)

# ============================
# GUI Functions
# ============================
def show_playfair():
    open_playfair_window()

def show_rsa():
    open_rsa_window()

def show_comparison():
    win = tk.Toplevel()
    win.title("So sánh Playfair và RSA")
    win.geometry("950x800")

    tk.Label(win, text="Nhập văn bản để mã hóa:", font=('Arial', 12)).pack(pady=5)
    input_text = tk.Text(win, height=4)
    input_text.pack(padx=10, fill=tk.X)

    result_frame = tk.Frame(win)
    result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    pf_frame = tk.LabelFrame(result_frame, text="Playfair Result")
    pf_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
    pf_result = tk.Text(pf_frame, height=10)
    pf_result.pack(expand=True, fill=tk.BOTH)

    rsa_frame = tk.LabelFrame(result_frame, text="RSA Result")
    rsa_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)
    rsa_result = tk.Text(rsa_frame, height=10)
    rsa_result.pack(expand=True, fill=tk.BOTH)

    time_frame = tk.LabelFrame(win, text="Thời gian xử lý (ms)")
    time_frame.pack(padx=10, pady=10, fill=tk.X)
    time_label = tk.Label(time_frame, text="")
    time_label.pack()

    chart_frame = tk.Frame(win)
    chart_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def export_to_pdf():
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="So sánh mã hóa Playfair vs RSA", ln=True, align="C")
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Văn bản: {input_text.get('1.0', tk.END).strip()}\n")
        pdf.multi_cell(0, 10, f"Mã hóa Playfair: {pf_result.get('1.0', tk.END).strip()}\n")
        pdf.multi_cell(0, 10, f"Mã hóa RSA: {rsa_result.get('1.0', tk.END).strip()}\n")
        pdf.multi_cell(0, 10, time_label.cget("text") + "\n")

        pdf.output(file_path)
        messagebox.showinfo("Thành công", "Đã xuất kết quả ra PDF!")

    def run_comparison():
        text = input_text.get("1.0", tk.END).strip()

        # Playfair - Run multiple times to get measurable time
        pf_matrix = generate_matrix("KEYWORD")
        start_pf = time.time()
        for _ in range(1000):  # Repeat 1000 times to make the timing measurable
            pf_enc = playfair_encrypt(text, pf_matrix)
        end_pf = time.time()

        pf_result.delete("1.0", tk.END)
        pf_result.insert(tk.END, pf_enc)

        # RSA
        try:
            start_rsa = time.time()
            (pubkey, privkey) = rsa.newkeys(512)
            rsa_enc = rsa.encrypt(text.encode(), pubkey)
            rsa_dec = rsa.decrypt(rsa_enc, privkey).decode()
            end_rsa = time.time()

            rsa_result.delete("1.0", tk.END)
            rsa_result.insert(tk.END, f"Encrypted (base64):\n{base64.b64encode(rsa_enc).decode()}\n\nDecrypted:\n{rsa_dec}")

            pf_time = round((end_pf - start_pf)*1000 / 1000, 2)  # Average time per encryption
            rsa_time = round((end_rsa - start_rsa)*1000, 2)
            time_label.config(text=f"Thời gian mã hóa:\n- Playfair: {pf_time} ms\n- RSA: {rsa_time} ms")

            for widget in chart_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(5, 3))
            bars = ax.bar(["Playfair", "RSA"], [pf_time, rsa_time], color=["orange", "skyblue"])
            ax.set_ylabel("Thời gian (ms)")
            ax.set_title("So sánh thời gian mã hóa")
            ax.bar_label(bars, fmt='%.2f ms')

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            rsa_result.delete("1.0", tk.END)
            rsa_result.insert(tk.END, f"Lỗi: {e}")

    tk.Button(win, text="So sánh mã hóa", command=run_comparison, bg="lightblue").pack(pady=10)
    tk.Button(win, text="Xuất PDF kết quả", command=export_to_pdf, bg="lightgreen").pack(pady=5)

# ============================
# GUI Layout
# ============================
root = tk.Tk()
root.title("ĐỒ ÁN NHÓM  - BẢO MẬT MẠNG MÁY TÍNH & HỆ THỐNG")
root.geometry("700x500")
root.configure(bg="white")

tk.Label(root, text="ĐỒ ÁN MÔN HỌC", font=("Helvetica", 18, "bold"), bg="white").pack(pady=5)
tk.Label(root, text="BẢO MẬT MẠNG MÁY TÍNH & HỆ THỐNG", font=("Helvetica", 20, "bold"), bg="white", fg="black").pack()

tk.Label(root, text="Nhóm: Lớp 10_ĐH_CNPM1", font=("Helvetica", 12), bg="white").pack()
tk.Label(root, text="CÁC THÀNH VIÊN:", font=("Helvetica", 12, "bold"), bg="white").pack(pady=5)

tk.Label(root, text="Nguyễn Thái Hoành\tMSSV: 1050080014", font=("Helvetica", 11), bg="white").pack()
tk.Label(root, text="Nguyễn Hoàng Anh\tMSSV: 1050080002", font=("Helvetica", 11), bg="white").pack()

frame = tk.Frame(root, bg="white")
frame.pack(pady=30)

playfair_btn = tk.Button(frame, text="PLAYFAIR", font=("Helvetica", 14, "bold"), fg="#FF5733", width=15, height=2, command=show_playfair)
playfair_btn.grid(row=0, column=0, padx=20)

rsa_btn = tk.Button(frame, text="RSA", font=("Helvetica", 14, "bold"), fg="#FF5733", width=15, height=2, command=show_rsa)
rsa_btn.grid(row=0, column=1, padx=20)

compare_btn = tk.Button(frame, text="SO SÁNH", font=("Helvetica", 14, "bold"), fg="green", width=32, height=2, command=show_comparison)
compare_btn.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()