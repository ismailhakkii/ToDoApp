import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import datetime
import json
import os

# Veri dosyası adı

def resource_path(relative_path):
    """PyInstaller ile paketlendiğinde veri dosyalarının yolunu alır."""
    try:
        # PyInstaller ile paketlenmişse
        base_path = sys._MEIPASS
    except Exception:
        # Normalde çalışıyorsa
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
DATA_FILE = resource_path("tasks.json")

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo Uygulaması")
        self.root.geometry("700x500")
        self.tasks = []

        self.create_widgets()
        self.load_tasks()
        self.update_progress()
        self.check_reminders()

    def create_widgets(self):
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#f0f0f0", foreground="black", rowheight=25, fieldbackground="#f0f0f0")
        style.map('Treeview', background=[('selected', '#347083')])

        # Üst çerçeve (Hoşgeldin mesajı ve tarih)
        frame_top = ttk.Frame(self.root)
        frame_top.pack(pady=10, padx=10, fill='x')

        self.label_welcome = ttk.Label(frame_top, text="Hoşgeldiniz! Görevlerinizi yönetin.", font=("Helvetica", 14))
        self.label_welcome.pack(side=tk.LEFT)

        self.label_datetime = ttk.Label(frame_top, text="", font=("Helvetica", 12))
        self.label_datetime.pack(side=tk.RIGHT)
        self.update_datetime()

        # Görev ekleme bölümü
        frame_add = ttk.Frame(self.root)
        frame_add.pack(pady=10, padx=10, fill='x')

        self.entry_task = ttk.Entry(frame_add, width=50)
        self.entry_task.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_task.bind("<Return>", lambda event: self.add_task())

        btn_add = ttk.Button(frame_add, text="Görev Ekle", command=self.add_task)
        btn_add.pack(side=tk.LEFT)

        # Görev filtreleme
        frame_filter = ttk.Frame(self.root)
        frame_filter.pack(pady=5, padx=10, fill='x')

        self.filter_var = tk.StringVar()
        self.filter_var.set("Tüm Görevler")

        filters = ["Tüm Görevler", "Tamamlanmış", "Tamamlanmamış"]
        for f in filters:
            rb = ttk.Radiobutton(frame_filter, text=f, variable=self.filter_var, value=f, command=self.filter_tasks)
            rb.pack(side=tk.LEFT, padx=5)

        # Görev listesi (Treeview)
        columns = ("Task", "Deadline", "Priority", "Completed")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=150)
        self.tree.pack(pady=10, padx=10, fill='both', expand=True)

        self.tree.bind("<Double-1>", self.toggle_completion)

        # Alt çerçeve (Butonlar ve İlerleme Çubuğu)
        frame_bottom = ttk.Frame(self.root)
        frame_bottom.pack(pady=10, padx=10, fill='x')

        btn_delete = ttk.Button(frame_bottom, text="Seçili Görevi Sil", command=self.delete_task)
        btn_delete.pack(side=tk.LEFT, padx=5)

        btn_edit = ttk.Button(frame_bottom, text="Seçili Görevi Düzenle", command=self.edit_task)
        btn_edit.pack(side=tk.LEFT, padx=5)

        btn_sort = ttk.Button(frame_bottom, text="Önceliğe Göre Sırala", command=self.sort_tasks)
        btn_sort.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(frame_bottom, orient='horizontal', length=300, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5)

        self.label_progress = ttk.Label(frame_bottom, text="İlerleme:")
        self.label_progress.pack(side=tk.RIGHT, padx=(0, 5))

        # Zamanlayıcı için sürekli tarih güncelleme
        self.update_clock()

    def update_datetime(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.label_datetime.config(text=f"Şu Anki Tarih ve Saat: {now}")

    def update_clock(self):
        self.update_datetime()
        self.root.after(1000, self.update_clock)

    def add_task(self):
        task = self.entry_task.get().strip()
        if not task:
            messagebox.showwarning("Uyarı", "Lütfen bir görev girin.")
            return

        deadline = simpledialog.askstring("Son Tarih", "Bu görev için bir son tarih girin (YYYY-MM-DD):")
        if not deadline or not self.validate_date(deadline):
            messagebox.showwarning("Uyarı", "Geçerli bir tarih girin (YYYY-MM-DD).")
            return

        priority = simpledialog.askstring("Öncelik Seviyesi", "Görev önceliğini girin (Yüksek, Orta, Düşük):")
        if not priority or priority.capitalize() not in ["Yüksek", "Orta", "Düşük"]:
            messagebox.showwarning("Uyarı", "Geçerli bir öncelik seviyesi girin (Yüksek, Orta, Düşük).")
            return

        new_task = {
            "task": task,
            "completed": False,
            "deadline": deadline,
            "priority": priority.capitalize()
        }
        self.tasks.append(new_task)
        self.save_tasks()
        self.refresh_treeview()
        self.update_progress()
        self.entry_task.delete(0, tk.END)
        messagebox.showinfo("Başarılı", f"'{task}' görevi başarıyla eklendi!")

    def toggle_completion(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = selected_item[0]
            index = self.tree.index(item)
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.save_tasks()
            self.refresh_treeview()
            self.update_progress()

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz görevi seçin.")
            return
        item = selected_item[0]
        index = self.tree.index(item)
        task_name = self.tasks[index]["task"]
        confirm = messagebox.askyesno("Onay", f"'{task_name}' görevini silmek istediğinize emin misiniz?")
        if confirm:
            self.tasks.pop(index)
            self.save_tasks()
            self.refresh_treeview()
            self.update_progress()
            messagebox.showinfo("Silindi", f"'{task_name}' görevi silindi.")

    def edit_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek istediğiniz görevi seçin.")
            return
        item = selected_item[0]
        index = self.tree.index(item)
        current_task = self.tasks[index]

        new_task = simpledialog.askstring("Görevi Düzenle", "Yeni görev adını girin:",
                                          initialvalue=current_task["task"])
        if not new_task:
            messagebox.showwarning("Uyarı", "Görev adı boş olamaz.")
            return

        new_deadline = simpledialog.askstring("Son Tarih", "Yeni son tarihi girin (YYYY-MM-DD):",
                                              initialvalue=current_task["deadline"])
        if not new_deadline or not self.validate_date(new_deadline):
            messagebox.showwarning("Uyarı", "Geçerli bir tarih girin (YYYY-MM-DD).")
            return

        new_priority = simpledialog.askstring("Öncelik Seviyesi", "Görev önceliğini girin (Yüksek, Orta, Düşük):",
                                              initialvalue=current_task["priority"])
        if not new_priority or new_priority.capitalize() not in ["Yüksek", "Orta", "Düşük"]:
            messagebox.showwarning("Uyarı", "Geçerli bir öncelik seviyesi girin (Yüksek, Orta, Düşük).")
            return

        self.tasks[index] = {
            "task": new_task,
            "completed": current_task["completed"],
            "deadline": new_deadline,
            "priority": new_priority.capitalize()
        }
        self.save_tasks()
        self.refresh_treeview()
        messagebox.showinfo("Güncellendi", f"'{current_task['task']}' görevi '{new_task}' olarak güncellendi!")

    def sort_tasks(self):
        priority_order = {"Yüksek": 1, "Orta": 2, "Düşük": 3}
        self.tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))
        self.save_tasks()
        self.refresh_treeview()
        messagebox.showinfo("Sıralandı", "Görevler önem değerine göre sıralandı.")

    def filter_tasks(self):
        self.refresh_treeview()

    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        filter_option = self.filter_var.get()
        for task in self.tasks:
            if filter_option == "Tamamlanmış" and not task["completed"]:
                continue
            elif filter_option == "Tamamlanmamış" and task["completed"]:
                continue
            self.tree.insert("", tk.END, values=(
                task["task"],
                task["deadline"],
                task["priority"],
                "Evet" if task["completed"] else "Hayır"
            ))

    def update_progress(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        if total > 0:
            progress_value = (completed / total) * 100
        else:
            progress_value = 0
        self.progress['value'] = progress_value

    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def save_tasks(self):
        try:
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Hata", f"Veriler kaydedilemedi: {e}")

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding='utf-8') as f:
                    self.tasks = json.load(f)
                self.refresh_treeview()
            except Exception as e:
                messagebox.showerror("Hata", f"Veriler yüklenemedi: {e}")
        else:
            self.tasks = []

    def check_reminders(self):
        today = datetime.datetime.now().date()
        reminders = [task for task in self.tasks if
                     not task["completed"] and datetime.datetime.strptime(task["deadline"], '%Y-%m-%d').date() == today]
        for task in reminders:
            messagebox.showinfo("Hatırlatma", f"Bugün '{task['task']}' görevini tamamlamalısın!")
        self.root.after(60000, self.check_reminders)  # Her dakika kontrol et


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
