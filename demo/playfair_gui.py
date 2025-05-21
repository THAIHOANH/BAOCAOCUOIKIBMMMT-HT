import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

# ==== Hàm hỗ trợ Playfair ====
def number_to_text(num_str):
    num_dict = {"0": "ZERO", "1": "ONE", "2": "TWO", "3": "THREE", "4": "FOUR",
                "5": "FIVE", "6": "SIX", "7": "SEVEN", "8": "EIGHT", "9": "NINE"}
    return "".join(num_dict[digit] for digit in num_str)

def prepare_text_for_playfair(text):
    text = text.upper().replace("J", "I").replace(" ", "")
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

def create_matrix(key, size=5):
    key = key.upper().replace("J", "I")
    chars = [chr(i) for i in range(65, 91)]  # A-Z
    if size == 6:
        chars.append("0")  # Optional: for 6x6
    seen = set()
    matrix = []
    for c in key + ''.join(chars):
        if c not in seen and c.isalpha():
            seen.add(c)
            matrix.append(c)
    return [matrix[i:i+size] for i in range(0, size*size, size)]

def find_pos(matrix, char):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char:
                return i, j
    return None, None

def prepare_text(text):
    text = prepare_text_for_playfair(text)
    i = 0
    pairs = []
    while i < len(text):
        a = text[i]
        b = text[i+1] if i+1 < len(text) else 'X'
        if a == b:
            pairs.append((a, 'X'))
            i += 1
        else:
            pairs.append((a, b))
            i += 2
    return pairs

def playfair_encrypt(text, matrix, size=5):
    result = ""
    for a, b in prepare_text(text):
        r1, c1 = find_pos(matrix, a)
        r2, c2 = find_pos(matrix, b)
        if r1 == r2:
            result += matrix[r1][(c1+1)%size] + matrix[r2][(c2+1)%size]
        elif c1 == c2:
            result += matrix[(r1+1)%size][c1] + matrix[(r2+1)%size][c2]
        else:
            result += matrix[r1][c2] + matrix[r2][c1]
    return result

def playfair_decrypt(text, matrix, size=5):
    result = ""
    pairs = [(text[i], text[i+1]) for i in range(0, len(text), 2)]
    for a, b in pairs:
        r1, c1 = find_pos(matrix, a)
        r2, c2 = find_pos(matrix, b)
        if r1 == r2:
            result += matrix[r1][(c1-1)%size] + matrix[r2][(c2-1)%size]
        elif c1 == c2:
            result += matrix[(r1-1)%size][c1] + matrix[(r2-1)%size][c2]
        else:
            result += matrix[r1][c2] + matrix[r2][c1]
    return result

# ==== Giao diện Playfair ====
def open_playfair_window():
    pf = tk.Toplevel()
    pf.title("PLAYFAIR")
    pf.geometry("800x400")

    def load_file():
        file = filedialog.askopenfilename()
        if file:
            with open(file, 'r') as f:
                msg_text.delete('1.0', tk.END)
                msg_text.insert(tk.END, f.read())

    def export_file():
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file, 'w') as f:
                f.write(result_box.get('1.0', tk.END).strip())
            messagebox.showinfo("Done", "File exported successfully.")

    def init_matrix():
        key = key_entry.get()
        size = 6 if var.get() == 2 else 5
        mat = create_matrix(key, size)
        msg = "\n".join([' '.join(row) for row in mat])
        messagebox.showinfo("Matrix", msg)

    def encrypt():
        key = key_entry.get()
        msg = msg_text.get('1.0', tk.END).strip()
        size = 6 if var.get() == 2 else 5
        matrix = create_matrix(key, size)
        encrypted = playfair_encrypt(msg, matrix, size)
        result_box.delete('1.0', tk.END)
        result_box.insert(tk.END, encrypted)

    def decrypt():
        key = key_entry.get()
        msg = msg_text.get('1.0', tk.END).strip()
        size = 6 if var.get() == 2 else 5
        matrix = create_matrix(key, size)
        decrypted = playfair_decrypt(msg, matrix, size)
        result_box.delete('1.0', tk.END)
        result_box.insert(tk.END, decrypted)

    def clear():
        msg_text.delete('1.0', tk.END)
        key_entry.delete(0, tk.END)
        result_box.delete('1.0', tk.END)

    # Layout
    left = tk.Frame(pf)
    left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

    tk.Label(left, text="MESSAGE:").pack()
    msg_text = scrolledtext.ScrolledText(left, height=5, width=40)
    msg_text.pack()

    frame_key = tk.Frame(left)
    frame_key.pack(pady=5)
    tk.Label(frame_key, text="KEY:").pack(side=tk.LEFT)
    key_entry = tk.Entry(frame_key, width=25)
    key_entry.pack(side=tk.LEFT)
    tk.Button(frame_key, text="READ FROM FILE", command=load_file).pack(side=tk.LEFT, padx=5)

    # Matrix buttons
    matrix_btns = tk.Frame(left)
    matrix_btns.pack(pady=10)
    for i, c in enumerate("ABCDEFGHIKLMNOPQRSTUVWXYZ"):
        tk.Button(matrix_btns, text=c, width=2).grid(row=i//5, column=i%5)

    var = tk.IntVar(value=1)
    matrix_type = tk.Frame(left)
    matrix_type.pack()
    tk.Radiobutton(matrix_type, text="5x5 Matrix", variable=var, value=1).pack(anchor=tk.W)
    tk.Radiobutton(matrix_type, text="6x6 Matrix", variable=var, value=2).pack(anchor=tk.W)
    tk.Button(left, text="INITIAL MATRIX", command=init_matrix).pack(pady=5)

    # Right side
    right = tk.Frame(pf)
    right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    tk.Label(right, text="RESULT:").pack()
    result_box = scrolledtext.ScrolledText(right, height=10)
    result_box.pack(fill=tk.BOTH, expand=True)

    btns = tk.Frame(right)
    btns.pack(pady=5)
    tk.Button(btns, text="ENCRYPT", command=encrypt).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="DECRYPT", command=decrypt).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="EXPORT FILE", command=export_file).pack(side=tk.LEFT, padx=5)
    tk.Button(btns, text="CLEAR", command=clear).pack(side=tk.LEFT, padx=5)