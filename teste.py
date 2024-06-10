import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import requests

api_key = "SUA_API_AQUI"

def carregar_livros():
    url = "https://www.abibliadigital.com.br/api/books"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:  
        return response.json()
    else:
        print(f"Error loading books. Status code: {response.status_code}")
        return [] 


def carregar_capitulos(book_abbrev):
    url = f"https://www.abibliadigital.com.br/api/books/{book_abbrev}"  
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        book_data = response.json()
        return book_data.get("chapters", 0) 
    else:
        print(f"Error loading chapters for {book_abbrev}. Status code: {response.status_code}")
        return 0  


def carregar_versiculos(book_id, chapter):
    url = f"https://www.abibliadigital.com.br/api/verses/nvi/{book_id}/{chapter}"
    headers = {"Authorization": f"Bearer {api_key}"}  
    response = requests.get(url, headers=headers)
    return response.json()

class BibliaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bíblia")
        self.geometry("800x600")
        
        self.sidebar_visible = True
     
        self.sidebar = tk.Frame(self, width=200, bg="lightgray")
        self.sidebar.pack_propagate(False)
        self.sidebar.pack(side="left", fill="y")
        
      
        self.tree = ttk.Treeview(self.sidebar)
        self.tree.pack(fill="both", expand=True)
      
        self.insert_tree_items()
        
      
        self.text_area = ScrolledText(self, wrap=tk.WORD)
        self.text_area.pack(side="right", fill="both", expand=True)
        

        self.toggle_button = tk.Button(self, text="<<", command=self.toggle_sidebar)
        self.toggle_button.pack(side="left", fill="y")
      
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
    def insert_tree_items(self):
        livros = carregar_livros()

        import threading  # Importar threading para usar threads

        
    def insert_tree_items(self):
        livros = carregar_livros()

        livros_ordenados = sorted(livros, key=lambda livro: livro.get("order", 0))  

        import threading  # Importar threading para usar threads

        def load_chapters_in_thread(livro):
            book_abbrev = livro["abbrev"]["pt"]
            book_id = self.tree.insert("", "end", text=livro["name"], values=(book_abbrev,))
            num_chapters = livro["chapters"]  # Obter o número de capítulos diretamente dos dados do livro
            for capitulo in range(1, num_chapters + 1):
                self.tree.insert(book_id, "end", text=f"Capítulo {capitulo}", values=(book_abbrev, capitulo))

        for livro in livros_ordenados:  # Usar a lista ordenada
            threading.Thread(target=load_chapters_in_thread, args=(livro,)).start()


                    
    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.toggle_button.config(text=">>")
        else:
            self.sidebar.pack(side="left", fill="y")
            self.toggle_button.config(text="<<")
        self.sidebar_visible = not self.sidebar_visible
    
    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        item_text = self.tree.item(selected_item, "text")
        book_id = self.tree.item(selected_item, "values")[0]
        
        if "Capítulo" in item_text:
            chapter = self.tree.item(selected_item, "values")[1]
            self.display_chapter(book_id, chapter)
            
    def display_chapter(self, book_id, chapter):
        self.text_area.delete(1.0, tk.END)
        versiculos = carregar_versiculos(book_id, chapter)
        for versiculo in versiculos["verses"]:
            self.text_area.insert(tk.END, f"{versiculo['number']} {versiculo['text']}\n")

if __name__ == "__main__":
    app = BibliaApp()
    app.mainloop()
