from tkinter import ttk

def apply_theme(root):
    root.configure(bg="#1e1e24")
    s = ttk.Style()
    s.theme_use("clam")
    s.configure(".", background="#1e1e24", foreground="#ffffff", font=("Segoe UI", 10))
    s.configure("TLabelframe", background="#2a2a35", bordercolor="#3f3f50", borderwidth=1)
    s.configure("TLabelframe.Label", background="#2a2a35", foreground="#00adb5", font=("Segoe UI", 11, "bold"))
    s.configure("TButton", background="#00adb5", foreground="#ffffff", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=6)
    s.map("TButton", background=[("active", "#008085")])
    s.configure("TNotebook", background="#1e1e24", borderwidth=0)
    s.configure("TNotebook.Tab", background="#2a2a35", foreground="#aaaaaa", padding=(15, 6))
    s.map("TNotebook.Tab", background=[("selected", "#00adb5")], foreground=[("selected", "#ffffff")])
    s.configure("Treeview", background="#2a2a35", fieldbackground="#2a2a35", foreground="#ffffff", rowheight=24)
    s.configure("Treeview.Heading", background="#3f3f50", foreground="#00adb5", font=("Segoe UI", 10, "bold"))
    s.map("Treeview", background=[("selected", "#00adb5")])
