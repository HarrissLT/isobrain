import inspect
from rich.console import Console
from prompt_toolkit import PromptSession

from isobrain.core.intent_engine import IntentEngine
from isobrain.plugins.office_plugins import OfficePlugins
from isobrain.plugins.file_plugin import FilePlugins
from isobrain.ui.banner import display_welcome_banner
from isobrain.ui.completer import IsoBrainCompleter, SmartAutoSuggest

console = Console()

def execute_handler(handler, entities: dict):
    """
    Dispatcher an toàn: Tự động lọc bỏ các tham số dư thừa 
    không nằm trong định nghĩa của hàm handler.
    """
    sig = inspect.signature(handler)
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    
    if has_kwargs:
        return handler(**entities)
    
    # Lọc chỉ giữ lại những tham số mà handler thực sự yêu cầu
    valid_keys = set(sig.parameters.keys())
    filtered_entities = {k: v for k, v in entities.items() if k in valid_keys}
    
    return handler(**filtered_entities)

def build_engine() -> IntentEngine:
    engine = IntentEngine()
    
    # 1. File: Tạo File mới
    engine.register(
        intent_name="FILE_CREATE",
        pattern=r"""tạo\s+file\s+(?:có\s+tên\s+và\s+định\s+dạng\s+là\s+)?["']?\s*(?P<file_name>[\w\.-]+\.(?:docx|xlsx|pdf|txt))\s*["']?\s+trong\s+(?:thư\s+mục\s+)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tạo file", "tạo văn bản", "tạo bảng tính", "tạo tài liệu"],
        handler=lambda file_name, folder_path: FilePlugins.create_file(file_name, folder_path)
    )

    # 2. File: Đổi tên hàng loạt
    engine.register(
        intent_name="FILE_BATCH_RENAME",
        pattern=r"""đổi\s+tên\s+hàng\s+loạt\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+?|["'].+?["'])\s+từ\s+["']?(?P<old_str>[^\s"']+)["']?\s+thành\s+["']?(?P<new_str>[^\s"']+)["']?""",
        keywords=["đổi tên hàng loạt", "sửa tên hàng loạt", "đổi tên"],
        handler=lambda folder_path, old_str, new_str: FilePlugins.batch_rename(folder_path, old_str, new_str)
    )

    # 3. Word: Đổi Font Chữ (Chấp nhận cả 'sang' và 'thành')
    engine.register(
        intent_name="WORD_CHANGE_FONT",
        pattern=r"""(đổi|sửa|thay)\s+font\s+file\s+.*?["']?(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)["']?\s+(?:sang|thành)\s+(?P<font_name>[\w\s]+)""",
        keywords=["đổi font", "thay phông", "sửa font word", "đổi phông"],
        handler=lambda file_path, font_name: OfficePlugins.change_word_font(file_path, font_name.strip())
    )
    
    # 4. Word: Tìm kiếm & Thay thế văn bản
    engine.register(
        intent_name="WORD_REPLACE_TEXT",
        pattern=r"""thay\s+thế\s+(?:từ\s+)?["']?(?P<old_text>[^\s"']+)["']?\s+thành\s+["']?(?P<new_text>[^\s"']+)["']?\s+trong\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["thay thế từ", "đổi từ", "replace text"],
        handler=lambda old_text, new_text, file_path: OfficePlugins.replace_text_word(file_path, old_text, new_text)
    )

    # 5. Word: Chuyển đổi Word sang PDF
    engine.register(
        intent_name="WORD_TO_PDF",
        pattern=r"""(chuyển|xuất|convert)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)\s+sang\s+pdf""",
        keywords=["sang pdf", "chuyển pdf", "word sang pdf"],
        handler=lambda file_path: OfficePlugins.convert_word_to_pdf(file_path)
    )
    
    # 6. Excel: Tính Toán Cột (Tổng / Trung Bình / Max / Min)
    engine.register(
        intent_name="EXCEL_CALCULATE_COL",
        pattern=r"""(tính|cộng)\s+(?P<calc_type>tổng|trung bình|lớn nhất|nhỏ nhất)?\s*cột\s+(?P<col_letter>[a-zA-Z]+)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tính tổng cột", "trung bình cột", "lớn nhất cột", "nhỏ nhất cột"],
        handler=lambda file_path, col_letter, calc_type="sum": OfficePlugins.calculate_excel_column(file_path, col_letter, calc_type or "sum")
    )

    # 7. File: Liệt kê danh sách file theo đuôi
    engine.register(
        intent_name="FILE_LIST_BY_EXT",
        pattern=r"""liệt\s+kê\s+file\s+(?P<extension>\.\w+|\w+)\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["liệt kê file", "danh sách file"],
        handler=lambda extension, folder_path: FilePlugins.list_files_by_ext(folder_path, extension)
    )
    
    return engine

def main():
    console.clear()
    display_welcome_banner(console)
    engine = build_engine()
    
    completer = IsoBrainCompleter()
    auto_suggest = SmartAutoSuggest()
    
    session = PromptSession(
        completer=completer,
        auto_suggest=auto_suggest,
        complete_while_typing=True
    )
    
    while True:
        try:
            user_input = session.prompt("IsoBrain ❯ ")
            if not user_input.strip():
                continue
                
            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[bold cyan]Cảm ơn bạn đã sử dụng IsoBrain. Tạm biệt![/bold cyan]")
                break
                
            match = engine.parse(user_input)
            
            if match.intent_name != "UNKNOWN" and match.handler:
                if match.entities:
                    # Gọi hàm qua Dispatcher lọc tham số an toàn
                    result = execute_handler(match.handler, match.entities)
                else:
                    result = "[yellow]IsoBrain hiểu ý định nhưng chưa trích xuất đủ tham số (đường dẫn/tên file). Bạn thử gõ rõ đường dẫn hơn nhé![/yellow]"
                console.print(result)
            else:
                console.print("[red]Lệnh chưa rõ hoặc chưa hỗ trợ. Bạn thử gõ lại câu ngắn gọn hơn nhé![/red]")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()