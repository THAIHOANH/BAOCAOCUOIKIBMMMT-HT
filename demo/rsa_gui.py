import tkinter as tk
from tkinter import messagebox
import random
from math import gcd
import base64
import time  # Thêm ở đầu file
# ====================
# RSA core functions
# ====================
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(5, int(n**0.5) + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

def generate_keys(p, q):
    n = p * q
    phi = (p - 1)*(q - 1)

    e = 65537
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)

    # Find d (modular inverse)
    def modinv(a, m):
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1

    d = modinv(e, phi)
    return (e, d, n, phi)

def rsa_encrypt(msg, e, n):
    cipher_numbers = [pow(ord(ch), e, n) for ch in msg]
    cipher_bytes = ' '.join(map(str, cipher_numbers)).encode('utf-8')
    return base64.b64encode(cipher_bytes).decode('utf-8')

def rsa_decrypt(cipher, d, n):
    try:
        decoded = base64.b64decode(cipher.encode('utf-8')).decode('utf-8')
        cipher_numbers = list(map(int, decoded.strip().split()))
        return ''.join([chr(pow(num, d, n)) for num in cipher_numbers])
    except:
        return "Invalid ciphertext"

# ====================
# RSA GUI
# ====================
def open_rsa_window():
    root = tk.Toplevel()
    root.title("RSA")
    root.geometry("800x500")

    # ==== Left Panel: Key Generation ====
    frame_left = tk.Frame(root)
    frame_left.pack(side=tk.LEFT, padx=10, pady=10)

    tk.Label(frame_left, text="CREATE KEY", font=('Arial', 10, 'bold')).pack()

    key_frame = tk.LabelFrame(frame_left, text="GENERATE KEY:")
    key_frame.pack(pady=5)

    tk.Label(key_frame, text="P").grid(row=0, column=0)
    entry_p = tk.Entry(key_frame)
    entry_p.grid(row=0, column=1)

    tk.Label(key_frame, text="Q").grid(row=1, column=0)
    entry_q = tk.Entry(key_frame)
    entry_q.grid(row=1, column=1)

    tk.Label(key_frame, text="Phi N").grid(row=2, column=0)
    entry_phi = tk.Entry(key_frame)
    entry_phi.grid(row=2, column=1)

    tk.Label(key_frame, text="1. p and q are two large prime number").grid(row=3, columnspan=2, sticky='w')
    tk.Label(key_frame, text="2. n = p × q. n is used for public & private keys").grid(row=4, columnspan=2, sticky='w')

    # Public & Private keys
    pub_frame = tk.LabelFrame(frame_left, text="PUBLIC KEY")
    pub_frame.pack(pady=5)
    tk.Label(pub_frame, text="N").grid(row=0, column=0)
    entry_n = tk.Entry(pub_frame)
    entry_n.grid(row=0, column=1)

    tk.Label(pub_frame, text="E").grid(row=1, column=0)
    entry_e = tk.Entry(pub_frame)
    entry_e.grid(row=1, column=1)

    priv_frame = tk.LabelFrame(frame_left, text="PRIVATE KEY (d,n)")
    priv_frame.pack(pady=5)
    entry_d = tk.Entry(priv_frame, width=30)
    entry_d.grid(row=0, column=0)

    # Right Panel: Encrypt & Decrypt
    frame_right = tk.Frame(root)
    frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    enc_frame = tk.LabelFrame(frame_right, text="ENCRYPT")
    enc_frame.pack(fill=tk.BOTH, expand=True)
    input_encrypt = tk.Text(enc_frame, height=4)
    input_encrypt.pack()
    output_encrypt = tk.Text(enc_frame, height=4)
    output_encrypt.pack()

    dec_frame = tk.LabelFrame(frame_right, text="DECRYPT")
    dec_frame.pack(fill=tk.BOTH, expand=True)
    input_decrypt = tk.Text(dec_frame, height=4)
    input_decrypt.pack()
    output_decrypt = tk.Text(dec_frame, height=4)
    output_decrypt.pack()

    def clear_all():
        for e in [entry_p, entry_q, entry_phi, entry_n, entry_e, entry_d, input_encrypt, output_encrypt, input_decrypt, output_decrypt]:
            e.delete(0, tk.END) if isinstance(e, tk.Entry) else e.delete('1.0', tk.END)

    def generate_key():
        try:
            # Auto-generate if blank
            if not entry_p.get() or not entry_q.get():
                sample_primes = [61, 53, 47, 59, 43, 67]
                p = random.choice(sample_primes)
                q = random.choice([x for x in sample_primes if x != p])
                entry_p.delete(0, tk.END)
                entry_p.insert(0, str(p))
                entry_q.delete(0, tk.END)
                entry_q.insert(0, str(q))
            else:
                p = int(entry_p.get())
                q = int(entry_q.get())

            if not (is_prime(p) and is_prime(q)):
                messagebox.showerror("Error", "P and Q must be prime numbers!")
                return

            e, d, n, phi = generate_keys(p, q)
            entry_phi.delete(0, tk.END)
            entry_phi.insert(0, str(phi))
            entry_n.delete(0, tk.END)
            entry_n.insert(0, str(n))
            entry_e.delete(0, tk.END)
            entry_e.insert(0, str(e))
            entry_d.delete(0, tk.END)
            entry_d.insert(0, f"{d}")
        except Exception as ex:
            messagebox.showerror("Error", f"Invalid input: {ex}")

    def do_encrypt():
        try:
            msg = input_encrypt.get("1.0", tk.END).strip()
            e = int(entry_e.get())
            n = int(entry_n.get())
            cipher = rsa_encrypt(msg, e, n)
            output_encrypt.delete('1.0', tk.END)
            output_encrypt.insert(tk.END, cipher)
        except:
            messagebox.showerror("Error", "Invalid key or message")

    def do_decrypt():
        try:
            cipher = input_decrypt.get("1.0", tk.END).strip()
            d = int(entry_d.get())
            n = int(entry_n.get())
            msg = rsa_decrypt(cipher, d, n)
            output_decrypt.delete('1.0', tk.END)
            output_decrypt.insert(tk.END, msg)
        except:
            messagebox.showerror("Error", "Invalid key or ciphertext")

    tk.Button(key_frame, text="GENERATE", command=generate_key).grid(row=0, column=2, rowspan=2, padx=5)
    tk.Button(frame_left, text="CLEAR", command=clear_all).pack(pady=5)
    tk.Button(enc_frame, text="ENCRYPT", command=do_encrypt).pack()
    tk.Button(dec_frame, text="DECRYPT", command=do_decrypt).pack()

# Gọi hàm mở GUI chính
if __name__ == "__main__":
    main_root = tk.Tk()
    main_root.withdraw()  # Ẩn cửa sổ chính
    open_rsa_window()
    main_root.mainloop()
