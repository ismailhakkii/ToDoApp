import tkinter as tk
from tkinter import messagebox
import datetime
import os

# Görev listesi
tasks = []

# Görevleri dosyaya kaydetme
def gorevleriKaydet():
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")
    print("Görevler başarıyla kaydedildi.")

# Görevleri dosyadan yükleme
def gorevleriYukle():
    if os.path.exists("tasks.txt"):
        with open("tasks.txt", "r") as file:
            for line in file:
                tasks.append(line.strip())
        print("Görevler başarıyla yüklendi.")
    else:
        print("Görev dosyası bulunamadı, yeni bir liste oluşturulacak.")

# Görev ekleme fonksiyonu
def gorevEkle():
    task = entry_gorev.get()
    if task:
        tasks.append(task)
        listbox_gorevler.insert(tk.END, task)
        entry_gorev.delete(0, tk.END)
        gorevleriKaydet()
        print(f"'{task}' görevi başarıyla eklendi!")
    else:
        messagebox.showwarning("Uyarı", "Lütfen bir görev girin.")

# Görev silme fonksiyonu
def gorevSil():
    selected_index = listbox_gorevler.curselection()
    if selected_index:
        task = listbox_gorevler.get(selected_index)
        confirm = messagebox.askyesno("Onay", f"'{task}' görevini silmek istediğinize emin misiniz?")
        if confirm:
            listbox_gorevler.delete(selected_index)
            tasks.pop(selected_index[0])
            gorevleriKaydet()
            print(f"'{task}' görevi silindi.")
    else:
        messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz görevi seçin.")

# Ana pencereyi oluşturma
root = tk.Tk()
root.title("Todo Uygulaması")
root.geometry("400x400")

# Hoşgeldin mesajı ve tarih gösterimi
def gostergeler():
    x = datetime.datetime.now()
    label_tarih.config(text=f"Şu anki tarih ve saat: {x}")

# Tarih butonu
button_tarih = tk.Button(root, text="Şu Anki Tarihi Göster", command=gostergeler)
button_tarih.pack(pady=10)

label_tarih = tk.Label(root, text="")
label_tarih.pack()

# Görev ekleme kısmı
frame_gorev = tk.Frame(root)
frame_gorev.pack(pady=10)

entry_gorev = tk.Entry(frame_gorev, width=30)
entry_gorev.pack(side=tk.LEFT, padx=5)

button_ekle = tk.Button(frame_gorev, text="Görev Ekle", command=gorevEkle)
button_ekle.pack(side=tk.LEFT)

# Görev listeleme kısmı
frame_liste = tk.Frame(root)
frame_liste.pack(pady=10)

scrollbar = tk.Scrollbar(frame_liste)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_gorevler = tk.Listbox(frame_liste, width=50, yscrollcommand=scrollbar.set)
listbox_gorevler.pack()

scrollbar.config(command=listbox_gorevler.yview)

# Görev silme butonu
button_sil = tk.Button(root, text="Seçili Görevi Sil", command=gorevSil)
button_sil.pack(pady=10)

# Uygulamayı kapatırken görevleri kaydetme
def kapanis():
    gorevleriKaydet()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", kapanis)

# Uygulama başlangıcı
gorevleriYukle()
for task in tasks:
    listbox_gorevler.insert(tk.END, task)

root.mainloop()
