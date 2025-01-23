import tkinter as tk
from tkinter import filedialog, messagebox
import re

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                current_node.children[char] = TrieNode()
            current_node = current_node.children[char]
        current_node.is_end_of_word = True

    def search(self, word):
        current_node = self.root
        for char in word:
            if char not in current_node.children:
                return False
            current_node = current_node.children[char]
        return current_node.is_end_of_word

def print_trie(node, level):
    if node.is_end_of_word:
        print(' ' * level + '-> [end]')
    for char, child in node.children.items():
        print(' ' * level + '->', char)
        print_trie(child, level + 1)

def build_dictionary_trie(file_path):
    dictionary_trie = Trie()
    with open(file_path, 'r') as file:
        for line in file:
            words = line.strip().split()
            for word in words:
                dictionary_trie.insert(word.lower())
    return dictionary_trie

def check_spelling_mistakes(file_path, dictionary_trie, content=None):
    mistakes = []
    line_number = 1

    if file_path is None:
        lines = content.strip().split('\n')
        for line_number, line in enumerate(lines, 1):
            words = re.findall(r'\w+|[^\w\s]|[\n]', line)
            for word in words:
                if re.match(r'\w', word) and not dictionary_trie.search(word.lower()):
                    mistakes.append((line_number, word))
    else:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                words = re.findall(r'\w+|[^\w\s]|[\n]', line)
                for word in words:
                    if re.match(r'\w', word) and not dictionary_trie.search(word.lower()):
                        mistakes.append((line_number, word))
    return mistakes

def get_hash(word):
    prime = 31
    mod = 10**9 + 9
    hash_value = 0
    for char in word:
        hash_value = (hash_value * prime + ord(char)) % mod
    return hash_value

def get_suggestions(root, word, suggestion_table):
    node = root
    suggestions = []
    current_prefix = ""

    if suggestion_table.get(get_hash(word), []) == []:

        def dfs(node, prefix):
            nonlocal suggestions
            nonlocal current_prefix
            if node.is_end_of_word:
                suggestions.append(current_prefix + prefix)
            for char, child in node.children.items():
                dfs(child, prefix + char)

        def find_suggestions(node, word):
            nonlocal current_prefix
            for char in word:
                if char not in node.children:
                    return
                current_prefix += char
                node = node.children[char]
            dfs(node, "")

        find_suggestions(root, word)
        suggestion_table[get_hash(word)] = suggestions

class SpellingCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spelling Checker")
        self.dictionary_trie = None
        self.text_file_path = None
        self.suggestion_table = {}
        self.widget_cont = False
        self.build_ui()

    def build_ui(self):
        self.root.configure(bg="#2E3440")
        self.label = tk.Label(self.root, text="Select a text file:", font=("Helvetica", 14, "bold"), bg="#2E3440", fg="#D8DEE9")
        self.label.pack(pady=10)
        self.open_button = tk.Button(self.root, text="Open File", command=self.open_file, font=("Helvetica", 12), padx=20, pady=10, bg="#81A1C1", fg="white", relief=tk.FLAT)
        self.open_button.pack(pady=10)
        self.check_button = tk.Button(self.root, text="Check Spelling", command=self.check_spelling, font=("Helvetica", 12), padx=20, pady=10, bg="#88C0D0", fg="white", relief=tk.FLAT)
        self.check_button.pack(pady=10)
        self.result_text = tk.Text(self.root, height=15, width=60, font=("Helvetica", 12), bg="#3B4252", fg="#ECEFF4", insertbackground="#ECEFF4", relief=tk.FLAT, wrap=tk.WORD)
        self.result_text.pack(pady=20)
        self.refresh_button = tk.Button(self.root, text="Refresh Dictionary", command=self.refresh_dictionary, font=("Helvetica", 12), padx=20, pady=10, bg="#BF616A", fg="white", relief=tk.FLAT)
        self.refresh_button.pack(pady=10)
        self.root.geometry("800x600")
        self.root.resizable(False, False)

    def refresh_dictionary(self):
        dictionary_file_path = r'tcw.txt'
        self.dictionary_trie = build_dictionary_trie(dictionary_file_path)
        self.result_text.delete(1.0, tk.END)
        self.text_file_path = None
        self.label.config(text="Select a text file:")

    def widget_content(self):
        if self.result_text.compare("end-1c", "==", "1.0"):
            self.widget_cont = False
        else:
            self.widget_cont = True

    def open_file(self):
        self.text_file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.text_file_path:
            self.label.config(text=f"Selected file: {self.text_file_path}")

    def check_spelling(self):
        self.widget_content()
        content = self.result_text.get("1.0", "end-1c")
        if not self.text_file_path and self.widget_cont == False:
            messagebox.showinfo("Error", "Please select a text file first.")
            return
        if not self.dictionary_trie:
            messagebox.showinfo("Error", "Dictionary trie is not built yet.")
            return
        mistakes = check_spelling_mistakes(self.text_file_path, self.dictionary_trie, content)
        if mistakes:
            self.result_text.tag_config("color_tag1", foreground="#88C0D0")
            self.result_text.tag_config("color_tag2", foreground="#BF616A")
            self.result_text.tag_config("color_tag3", foreground="#A3BE8C")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Spelling mistakes found:\n\n", "color_tag1")
            for line_number, word in mistakes:
                self.result_text.insert(tk.END, f"Line {line_number}: {word}\n", "color_tag2")
                get_suggestions(self.dictionary_trie.root, word, self.suggestion_table)
                suggestions = self.suggestion_table[get_hash(word)]
                if suggestions:
                    suggestions = suggestions[:5]
                    suggestions_text = ', '.join(suggestions)
                else:
                    suggestions_text = "None"
                self.result_text.insert(tk.END, f"Suggestions for '{word}': {suggestions_text}\n\n", "color_tag3")
        else:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "No spelling mistakes found.")

root = tk.Tk()
spelling_checker = SpellingCheckerGUI(root)
dictionary_file_path = r'tcw.txt'
spelling_checker.dictionary_trie = build_dictionary_trie(dictionary_file_path)
root.mainloop()
