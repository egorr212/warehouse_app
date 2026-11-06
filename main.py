import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
import styles

DB = "warehouse.db"

def run_q(q, p=(), fetch=False, commit=False):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(q, p)
    res = cur.fetchall() if fetch else (cur.fetchone() if not commit else None)
    if commit: conn.commit()
    conn.close()
    return res

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS managers (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS cells (id INTEGER PRIMARY KEY AUTOINCREMENT, cell_code TEXT UNIQUE, max_size TEXT, is_occupied INTEGER DEFAULT 0)')
    cur.execute('CREATE TABLE IF NOT EXISTS packages (id INTEGER PRIMARY KEY AUTOINCREMENT, track_number TEXT UNIQUE, client_phone TEXT, size TEXT, cell_id INTEGER, arrival_date TEXT)')
    cur.execute("SELECT COUNT(*) FROM managers")
    if cur.fetchone() == 0:
        cur.execute("INSERT INTO managers (username, password) VALUES ('admin', 'admin123')")
    cur.execute("SELECT COUNT(*) FROM cells")
    if cur.fetchone() == 0:
        data = [("A-1", "Маленькая", 0), ("A-2", "Маленькая", 0), ("B-1", "Средняя", 0), ("B-2", "Средняя", 0), ("C-1", "Крупная", 0)]
        cur.executemany("INSERT INTO cells (cell_code, max_size, is_occupied) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()

class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WMS Контроль ПВЗ")
        self.root.geometry("850x550")
        styles.apply_theme(self.root)
        self.main_container = ttk.Frame(self.root, padding=15)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.show_login()

    def show_login(self):
        for w in self.main_container.winfo_children(): w.destroy()
        f = ttk.LabelFrame(self.main_container, text=" Авторизация ", padding=20)
        f.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=220)
        ttk.Label(f, text="Логин:").pack(anchor=tk.W)
        self.l_ent = tk.Entry(f, bg="#3f3f50", fg="#ffffff", bd=0)
        self.l_ent.pack(fill=tk.X, pady=5, ipady=4)
        self.l_ent.insert(0, "admin")
        ttk.Label(f, text="Пароль:").pack(anchor=tk.W)
        self.p_ent = tk.Entry(f, show="*", bg="#3f3f50", fg="#ffffff", bd=0)
        self.p_ent.pack(fill=tk.X, pady=5, ipady=4)
        self.p_ent.insert(0, "admin123")
        ttk.Button(f, text="ВОЙТИ В СИСТЕМУ", command=self.login).pack(fill=tk.X, pady=10)

    def login(self):
        r = run_q("SELECT id FROM managers WHERE username=? AND password=?", (self.l_ent.get().strip(), self.p_ent.get().strip()))
        if r: self.show_main()
        else: messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_main(self):
        for w in self.main_container.winfo_children(): w.destroy()
        nb = ttk.Notebook(self.main_container)
        nb.pack(fill=tk.BOTH, expand=True)
        t1, t2 = ttk.Frame(nb, padding=10), ttk.Frame(nb, padding=10)
        nb.add(t1, text="📦 Приемка груза")
        nb.add(t2, text="📊 Мониторинг склада")
        
        f1 = ttk.LabelFrame(t1, text=" Регистрация ", padding=10)
        f1.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Label(f1, text="Трек-номер:").pack(anchor=tk.W)
        self.t_ent = tk.Entry(f1, bg="#2a2a35", fg="#ffffff", bd=1, relief=tk.SOLID)
        self.t_ent.pack(fill=tk.X, pady=5, ipady=3)
        ttk.Label(f1, text="Телефон:").pack(anchor=tk.W)
        self.ph_ent = tk.Entry(f1, bg="#2a2a35", fg="#ffffff", bd=1, relief=tk.SOLID)
        self.ph_ent.pack(fill=tk.X, pady=5, ipady=3)
        self.ph_ent.insert(0, "+7")
        self.sz_cb = ttk.Combobox(f1, values=["Маленькая", "Средняя", "Крупная"], state="readonly")
        self.sz_cb.set("Маленькая")
        self.sz_cb.pack(fill=tk.X, pady=5)
        self.sz_cb.bind("<<ComboboxSelected>>", lambda e: self.load_c())
        ttk.Button(f1, text="🔎 НАЙТИ ПОЛКУ", command=self.load_c).pack(fill=tk.X, pady=5)
        ttk.Button(f1, text="📥 РАЗМЕСТИТЬ", command=self.save_p).pack(fill=tk.X, pady=2)
        
        f2 = ttk.LabelFrame(t1, text=" Свободные ячейки ", padding=10)
        f2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.c_tr = ttk.Treeview(f2, columns=("id", "code", "sz"), show="headings")
        for c, h in [("id", "ID"), ("code", "Код ячейки"), ("sz", "Тип полки")]:
            self.c_tr.heading(c, text=h); self.c_tr.column(c, anchor=tk.CENTER)
        self.c_tr.column("id", width=40)
        self.c_tr.pack(fill=tk.BOTH, expand=True)
        
        f3 = ttk.Frame(t2)
        f3.pack(fill=tk.X, pady=5)
        
        self.lbl_analytics = ttk.Label(f3, text="Загрузка склада: 0%", font=("Segoe UI", 10, "bold"), foreground="#00adb5")
        self.lbl_analytics.pack(side=tk.LEFT, padx=5)
        
        self.p_bar = ttk.Progressbar(f3, orient="horizontal", length=200, mode="determinate")
        self.p_bar.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(f3, text="✅ ВЫДАТЬ ЗАКАЗ КЛИЕНТУ", command=self.del_p).pack(side=tk.RIGHT)
        
        self.p_tr = ttk.Treeview(t2, columns=("id", "tr", "ph", "sz", "cl", "dt"), show="headings")
        for c, h in [("id", "ID"), ("tr", "Трек"), ("ph", "Телефон"), ("sz", "Размер"), ("cl", "Ячейка"), ("dt", "Дата")]:
            self.p_tr.heading(c, text=h); self.p_tr.column(c, anchor=tk.CENTER, width=120)
        self.p_tr.column("id", width=40)
        self.p_tr.pack(fill=tk.BOTH, expand=True)
        
        self.load_c(); self.load_p()

    def update_analytics(self):
        total_cells = run_q("SELECT COUNT(*) FROM cells")[0]
        occupied_cells = run_q("SELECT COUNT(*) FROM cells WHERE is_occupied = 1")[0]
        if total_cells > 0:
            percent = (occupied_cells / total_cells) * 100
            self.lbl_analytics.config(text=f"Загрузка склада: {percent:.0f}% ({occupied_cells} из {total_cells})")
            self.p_bar["value"] = percent
        else:
            self.p_bar["value"] = 0

    def load_c(self):
        self.c_tr.delete(*self.c_tr.get_children())
        for r in run_q("SELECT id, cell_code, max_size FROM cells WHERE is_occupied = 0 AND max_size = ?", (self.sz_cb.get(),), fetch=True):
            self.c_tr.insert("", tk.END, iid=str(r[0]), values=r)

    def save_p(self):
        sel = self.c_tr.selection()
        if not self.t_ent.get() or not sel:
            messagebox.showwarning("Ошибка", "Заполните данные и выберите ячейку!")
            return
        c_id = int(sel[0])
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO packages (track_number, client_phone, size, cell_id, arrival_date) VALUES (?, ?, ?, ?, ?)', (self.t_ent.get().strip(), self.ph_ent.get().strip(), self.sz_cb.get(), c_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
            cur.execute("UPDATE cells SET is_occupied = 1 WHERE id = ?", (c_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Посылка принята!")
            self.t_ent.delete(0, tk.END); self.load_c(); self.load_p()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такой трек уже существует!")
        finally:
            conn.close()

    def load_p(self):
        self.p_tr.delete(*self.p_tr.get_children())
        for r in run_q('SELECT p.id, p.track_number, p.client_phone, p.size, c.cell_code, p.arrival_date FROM packages p JOIN cells c ON p.cell_id = c.id', fetch=True):
            self.p_tr.insert("", tk.END, iid=str(r[0]), values=r)
        self.update_analytics()

    def del_p(self):
        sel = self.p_tr.selection()
        if not sel:
            messagebox.showwarning("Ошибка", "Выберите посылку!")
            return
        p_id = int(sel[0])
        p_data = self.p_tr.item(sel)['values']
        cell_code = str(p_data[4])
        if messagebox.askyesno("Выдача", f"Выдать заказ №{p_data[1]} клиенту? Полка {cell_code} освободится."):
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("UPDATE cells SET is_occupied = 0 WHERE cell_code = ?", (cell_code,))
            cur.execute("DELETE FROM packages WHERE id = ?", (p_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Заказ выдан!"); self.load_p(); self.load_c()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()