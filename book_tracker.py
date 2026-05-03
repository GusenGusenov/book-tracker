import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        
        # Данные о книгах
        self.books = []
        self.filename = "books.json"
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных при запуске
        self.load_books()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление книги", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Название книги
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Автор
        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Количество страниц
        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.pages_entry = ttk.Entry(input_frame, width=30)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=2)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить книгу", command=self.add_book).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Фильтр по жанру
        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w")
        self.filter_genre = ttk.Combobox(filter_frame, width=27)
        self.filter_genre.grid(row=0, column=1, padx=5, pady=2)
        self.filter_genre.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Фильтр по страницам
        ttk.Label(filter_frame, text="Страниц больше:").grid(row=1, column=0, sticky="w")
        self.filter_pages = ttk.Entry(filter_frame, width=30)
        self.filter_pages.grid(row=1, column=1, padx=5, pady=2)
        self.filter_pages.bind('<KeyRelease>', self.apply_filters)
        
        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Фрейм для таблицы
        table_frame = ttk.Frame(self.root)
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        # Создание таблицы
        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Определение заголовков
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Полосы прокрутки
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_books).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_books).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_book).pack(side="left", padx=5)
        
        # Настройка расширения таблицы
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def validate_input(self):
        # Проверка на пустые поля
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()
        
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return None
        
        # Проверка количества страниц
        try:
            pages = int(pages)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return None
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return None
        
        return {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
    
    def add_book(self):
        book = self.validate_input()
        if book:
            self.books.append(book)
            self.update_table()
            self.clear_entries()
            self.update_genre_filter()
    
    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
    
    def update_table(self, filtered_books=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление книг в таблицу
        books_to_display = filtered_books if filtered_books is not None else self.books
        for book in books_to_display:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))
    
    def apply_filters(self, event=None):
        filtered_books = self.books.copy()
        
        # Фильтр по жанру
        selected_genre = self.filter_genre.get()
        if selected_genre and selected_genre != "Все жанры":
            filtered_books = [book for book in filtered_books if book["genre"].lower() == selected_genre.lower()]
        
        # Фильтр по страницам
        pages_filter = self.filter_pages.get().strip()
        if pages_filter:
            try:
                min_pages = int(pages_filter)
                filtered_books = [book for book in filtered_books if book["pages"] > min_pages]
            except ValueError:
                # Игнорируем невалидный ввод в фильтре
                pass
        
        self.update_table(filtered_books)
    
    def reset_filters(self):
        self.filter_genre.set("")
        self.filter_pages.delete(0, tk.END)
        self.update_table()
    
    def update_genre_filter(self):
        # Обновление списка жанров для фильтра
        genres = list(set(book["genre"] for book in self.books))
        genres.sort()
        genres.insert(0, "Все жанры")
        self.filter_genre['values'] = genres
    
    def delete_book(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return
        
        # Получение данных выбранной книги
        values = self.tree.item(selected_item[0])['values']
        
        # Поиск и удаление книги из списка
        for book in self.books[:]:
            if (book["title"] == values[0] and 
                book["author"] == values[1] and 
                book["genre"] == values[2] and 
                book["pages"] == values[3]):
                self.books.remove(book)
                break
        
        self.update_table()
        self.update_genre_filter()
    
    def save_books(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def load_books(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
                self.update_table()
                self.update_genre_filter()
                messagebox.showinfo("Успех", f"Данные загружены из файла {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            self.books = []

def main():
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()