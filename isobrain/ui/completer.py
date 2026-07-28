from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.document import Document

class SmartAutoSuggest(AutoSuggest):
    """
    Hiển thị gợi ý mờ (Ghost Text) thông minh theo ngữ cảnh từ đang gõ.
    Khi người dùng gõ "Hãy tính tổng file...", chữ mờ sẽ gợi ý đường dẫn mẫu.
    """
    def get_suggestion(self, buffer, document: Document):
        text = document.text.lower()
        
        # Gợi ý ngữ cảnh động khi gõ câu lệnh
        if text.startswith("hãy tính tổng file") or text.startswith("tính tổng cột"):
            if "file" in text and not ('"' in text or "'" in text):
                return Suggestion(' "D:\\du_an\\luong.xlsx" cột D')
        elif text.startswith("chuyển file") or text.startswith("sang pdf"):
            if "file" in text and not (".docx" in text):
                return Suggestion(' "D:\\du_an\\baocao.docx" sang PDF')
        elif text.startswith("đổi tên hàng loạt"):
            return Suggestion(' trong "D:\\thumuc" từ "cu" thành "moi"')
            
        return None

class IsoBrainCompleter(Completer):
    """Bộ gợi ý tự động hoàn thiện danh sách lệnh và định dạng file khi nhấn TAB"""
    def __init__(self):
        self.commands = [
            "Tính tổng cột D file",
            "Tính trung bình cột D file",
            "Đổi font file",
            "Thay thế từ",
            "Chuyển file",
            "Đổi tên hàng loạt trong",
            "Liệt kê danh sách file",
            "exit",
            "quit"
        ]
        self.extensions = [".docx", ".xlsx", ".pdf", ".txt"]
        self.fonts = ["Arial", "Times New Roman", "Calibri", "Roboto", "Segoe UI"]

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor()

        # 1. Gợi ý từ khóa câu lệnh
        for cmd in self.commands:
            if cmd.lower().startswith(text_before_cursor.lower()):
                yield Completion(cmd, start_position=-len(text_before_cursor))

        # 2. Gợi ý Font chữ nếu gõ từ 'sang'
        if "sang " in text_before_cursor.lower():
            for font in self.fonts:
                if font.lower().startswith(word_before_cursor.lower()):
                    yield Completion(font, start_position=-len(word_before_cursor))