import inspect
from rich.console import Console
from prompt_toolkit import PromptSession

from isobrain.core.intent_engine import IntentEngine
from isobrain.plugins.office_plugins import OfficePlugins
from isobrain.plugins.file_plugin import FilePlugins
from isobrain.plugins.system_plugin import SystemPlugins
from isobrain.plugins.code_plugin import CodePlugins
from isobrain.plugins.viz_plugin import VizPlugins
from isobrain.ui.banner import display_welcome_banner
from isobrain.ui.completer import IsoBrainCompleter, SmartAutoSuggest

console = Console()

def execute_handler(handler, entities: dict):
    """
    Dispatcher an toàn: Tự động kiểm tra tham số của hàm handler
    và lọc bỏ các tham số dư thừa do Fuzzy Matcher trích xuất rác.
    """
    sig = inspect.signature(handler)
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    
    if has_kwargs:
        return handler(**entities)
    
    valid_keys = set(sig.parameters.keys())
    filtered_entities = {k: v for k, v in entities.items() if k in valid_keys}
    
    return handler(**filtered_entities)

def build_engine() -> IntentEngine:
    engine = IntentEngine()
    
    # ==================== 1. TỰ ĐỘNG HÓA FILE & THƯ MỤC ====================
    # Tạo File mới (.docx, .xlsx, .txt)
    engine.register(
        intent_name="FILE_CREATE",
        pattern=r"""tạo\s+file\s+(?:có\s+tên\s+và\s+định\s+dạng\s+là\s+)?["']?\s*(?P<file_name>[\w\.-]+\.(?:docx|xlsx|pdf|txt))\s*["']?\s+trong\s+(?:thư\s+mục\s+)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tạo file", "tạo văn bản", "tạo bảng tính", "tạo tài liệu"],
        handler=lambda file_name, folder_path: FilePlugins.create_file(file_name, folder_path)
    )

    # Đổi tên hàng loạt trong thư mục
    engine.register(
        intent_name="FILE_BATCH_RENAME",
        pattern=r"""đổi\s+tên\s+hàng\s+loạt\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+?|["'].+?["'])\s+từ\s+["']?(?P<old_str>[^\s"']+)["']?\s+thành\s+["']?(?P<new_str>[^\s"']+)["']?""",
        keywords=["đổi tên hàng loạt", "sửa tên hàng loạt", "đổi tên"],
        handler=lambda folder_path, old_str, new_str: FilePlugins.batch_rename(folder_path, old_str, new_str)
    )

    # Liệt kê danh sách file theo định dạng
    engine.register(
        intent_name="FILE_LIST_BY_EXT",
        pattern=r"""liệt\s+kê\s+file\s+(?P<extension>\.\w+|\w+)\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["liệt kê file", "danh sách file"],
        handler=lambda extension, folder_path: FilePlugins.list_files_by_ext(folder_path, extension)
    )

    # ==================== 2. TỰ ĐỘNG HÓA WORD & OFFICE ====================
    # Đổi Font Chữ Word
    engine.register(
        intent_name="WORD_CHANGE_FONT",
        pattern=r"""(đổi|sửa|thay)\s+font\s+file\s+.*?["']?(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)["']?\s+(?:sang|thành)\s+(?P<font_name>[\w\s]+)""",
        keywords=["đổi font", "thay phông", "sửa font word", "đổi phông"],
        handler=lambda file_path, font_name: OfficePlugins.change_word_font(file_path, font_name.strip())
    )
    
    # Tìm kiếm & Thay thế văn bản trong Word
    engine.register(
        intent_name="WORD_REPLACE_TEXT",
        pattern=r"""thay\s+thế\s+(?:từ\s+)?["']?(?P<old_text>[^\s"']+)["']?\s+thành\s+["']?(?P<new_text>[^\s"']+)["']?\s+trong\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["thay thế từ", "đổi từ", "replace text"],
        handler=lambda old_text, new_text, file_path: OfficePlugins.replace_text_word(file_path, old_text, new_text)
    )

    # Chuyển đổi Word sang PDF
    engine.register(
        intent_name="WORD_TO_PDF",
        pattern=r"""(chuyển|xuất|convert)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)\s+sang\s+pdf""",
        keywords=["sang pdf", "chuyển pdf", "word sang pdf"],
        handler=lambda file_path: OfficePlugins.convert_word_to_pdf(file_path)
    )

    # ==================== 3. TỰ ĐỘNG HÓA EXCEL ====================
    # Tính toán Cột Excel (Tổng / Trung Bình / Max / Min)
    engine.register(
        intent_name="EXCEL_CALCULATE_COL",
        pattern=r"""(tính|cộng)\s+(?P<calc_type>tổng|trung bình|lớn nhất|nhỏ nhất)?\s*cột\s+(?P<col_letter>[a-zA-Z]+)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tính tổng cột", "trung bình cột", "lớn nhất cột", "nhỏ nhất cột"],
        handler=lambda file_path, col_letter, calc_type="sum": OfficePlugins.calculate_excel_column(file_path, col_letter, calc_type or "sum")
    )

    # ==================== 4. ĐIỀU KHUYỂN HỆ THỐNG & WORKSPACE ====================
    # Mở Workspace làm việc theo bối cảnh
    engine.register(
        intent_name="SYS_WORKSPACE",
        pattern=r"""(bắt\s+đầu|kích\s+hoạt|mở)\s+(?:ca\s+|không\s+gian\s+)?(?P<workspace_name>lập\s+trình|code|học\s+tập|văn\s+phòng)""",
        keywords=["bắt đầu ca", "mở không gian", "ca học", "ca làm việc"],
        handler=lambda workspace_name: SystemPlugins.launch_workspace(workspace_name)
    )

    # Gom & Nén File Điều Kiện (Smart Zip)
    engine.register(
        intent_name="SYS_SMART_ZIP",
        pattern=r"""gom\s+file\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)\s+trong\s+(?P<days>\d+)\s+ngày\s+nén\s+thành\s+zip""",
        keywords=["gom file", "nén zip", "nén file tuần này"],
        handler=lambda folder_path, days=7: SystemPlugins.zip_files_by_condition(folder_path, int(days) if days else 7)
    )

    # Chuẩn hóa văn bản trong Clipboard
    engine.register(
        intent_name="SYS_CLIPBOARD",
        pattern=r"""(làm\s+sạch|chuẩn\s+hóa)\s+(?:khay\s+nhớ\s+tạm|clipboard)""",
        keywords=["làm sạch clipboard", "chuẩn hóa clipboard"],
        handler=lambda: SystemPlugins.process_clipboard()
    )

    # ==================== 5. CODE DOCS & AUTO-VIZ ====================
    # Phân tích mã nguồn và tự sinh file README.md
    engine.register(
        intent_name="CODE_GEN_README",
        pattern=r"""(tạo|viết)\s+(?:tài\s+liệu|readme)\s+cho\s+(?:thư\s+mục\s+)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tạo readme", "viết tài liệu", "tài liệu code"],
        handler=lambda folder_path: CodePlugins.generate_readme_from_code(folder_path)
    )

    # Vẽ biểu đồ Excel chèn trực tiếp vào Word (Auto-Viz)
    engine.register(
        intent_name="VIZ_AUTO_CHART",
        pattern=r"""vẽ\s+biểu\s+đồ\s+cột\s+(?P<col_val>[a-zA-Z]+)\s+theo\s+cột\s+(?P<col_label>[a-zA-Z]+)\s+file\s+(?P<excel_file>[a-zA-Z]:\\[^"'\n]+|\S+)\s+chèn\s+vào\s+(?P<word_file>[a-zA-Z]:\\[^"'\n]+|\S+)""",
        keywords=["vẽ biểu đồ", "vẽ chart", "chèn biểu đồ"],
        handler=lambda excel_file, word_file, col_label, col_val: VizPlugins.create_chart_to_word(excel_file, word_file, col_label, col_val)
    )
    
    return engine

def main():
    console.clear()
    display_welcome_banner(console)
    engine = build_engine()
    
    # Thiết lập Gợi ý thông minh (Auto-complete & Ghost text)
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
                    result = execute_handler(match.handler, match.entities)
                else:
                    result = execute_handler(match.handler, {})
                console.print(result)
            else:
                console.print("[red]Lệnh chưa rõ hoặc chưa hỗ trợ. Thử gõ: 'bắt đầu ca lập trình' hoặc 'tạo file khbg.docx trong D:\\'[/red]")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()