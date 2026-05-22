class SimpleSearch:
    def __init__(self):
        self.chunks = [
            {"id": "1", "text": "Для поступления нужны паспорт, аттестат, СНИЛС."},
            {"id": "2", "text": "Платное обучение от 100 000 руб."},
        ]
    def search(self, query):
        return self.chunks  # пока возвращает все

if __name__ == "__main__":
    s = SimpleSearch()
    print(s.search("документы"))