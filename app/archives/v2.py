import tkinter as tk
import requests
import hashlib

def check_password():
    password = entry.get()
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1password[:5]
    suffix = sha1password[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)

    if suffix in res.text:
        result_label.config(text="Password has been breached!", fg="red")
    else:
        result_label.config(text="Password is safe!", fg="green")

# GUI setup
root = tk.Tk()
root.title("Password Breach Checker")

tk.Label(root, text="Enter your password:").pack(pady=5)
entry = tk.Entry(root, show="*")
entry.pack(pady=5)

tk.Button(root, text="Check Password", command=check_password).pack(pady=5)
result_label = tk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()
