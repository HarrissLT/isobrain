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
    try:
        sig = inspect.signature(handler)
        has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        
        if has_kwargs:
            return handler(**entities)
        
        valid_keys = set(sig.parameters.keys())
        filtered_entities = {k: v for k, v in entities.items() if k in valid_keys}
        
        required_params = {
            name for name, param in sig.parameters.items()
            if param.default == inspect.Parameter.empty and param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY)
        }
        
        missing_params = required_params - set(filtered_entities.keys())
        if missing_params:
            return f"[yellow]IsoBrain nhận diện được ý định của bạn nhưng chưa trích xuất đủ thông tin bắt buộc: {', '.join(missing_params)}. Bạn hãy thử gõ câu rõ ràng hơn nhé![/yellow]"
            
        return handler(**filtered_entities)
    except Exception as e:
        return f"[bold red]Lỗi thực thi lệnh:[/bold red] {str(e)}"

def build_engine() -> IntentEngine:
    engine = IntentEngine()
    
    # 1. Word: Tạo Bảng biểu Chuyên Nghiệp (MỚI NÂNG CẤP)
    engine.register(
        intent_name="WORD_CREATE_TABLE",
        pattern=r"""tạo\s+bảng\s+.*?(?:file\s+["']?(?P<file_name>[\w\.-]+\.docx)?["']?)?\s*(?:ở|trong)?\s*(?:thư\s+mục\s*:?\s*)?["']?(?P<folder_path>[a-zA-Z]:\\[^"'\n:]+?)["']?\s*:?\s*(?P<headers_str>cột\s*\d+.*|.*)""",
        keywords=["tạo bảng", "tạo bảng biểu", "tạo bảng với", "tạo table"],
        handler=lambda file_name="document.docx", folder_path="", headers_str="": OfficePlugins.create_word_table(file_name, folder_path, headers_str)
    )

    # 2. File: Quét Top N File theo Kích Thước
    engine.register(
        intent_name="FILE_SIZE_ANALYTICS",
        pattern=r"""liệt\s+kê\s+(?:danh\s+sách\s+)?(?P<top_n>\d+)?\s*file\s+(?P<mode>nặng|lớn|nhẹ|nhỏ)\s+nhất\s+trong\s+(?:thư\s+mục\s*:?\s*)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]*|["'].+?["']|\S+)""",
        keywords=["file nặng nhất", "file nhẹ nhất", "file lớn nhất", "file nhỏ nhất"],
        handler=lambda folder_path, mode="largest", top_n=5: FilePlugins.get_files_by_size(
            folder_path, 
            int(top_n) if top_n else 5, 
            mode or "largest"
        )
    )

    # 3. File: Tạo HÀNG LOẠT File cùng lúc
    engine.register(
        intent_name="FILE_CREATE_BATCH",
        pattern=r"""tạo\s+(?:\d+\s+)?file\s*(?P<default_ext>word|excel|docx|xlsx|txt)?\s*.*?(?:với\s+tên\s+là\s*:\s*|gồm\s*:?\s*)?(?P<raw_names>[\w\s;,-]+?)\s+trong\s+(?:thư\s+mục\s*:?\s*)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]*|["'].+?["']|\S+)""",
        keywords=["tạo 3 file", "tạo nhiều file", "tạo các file", "lần lượt với tên là"],
        handler=lambda raw_names, folder_path, default_ext="docx": FilePlugins.create_batch_files(
            raw_names, 
            folder_path, 
            default_ext or "docx"
        )
    )

    # 4. File: Tạo 1 File đơn lẻ
    engine.register(
        intent_name="FILE_CREATE",
        pattern=r"""tạo\s+file\s+(?:có\s+tên\s+và\s+định\s+dạng\s+là\s+)?["']?\s*(?P<file_name>[\w\.-]+\.(?:docx|xlsx|pdf|txt))\s*["']?\s+trong\s+(?:thư\s+mục\s+)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tạo file", "tạo văn bản", "tạo bảng tính"],
        handler=lambda file_name, folder_path: FilePlugins.create_file(file_name, folder_path)
    )

    # 5. Word: Đổi Font Chữ
    engine.register(
        intent_name="WORD_CHANGE_FONT",
        pattern=r"""(đổi|sửa|thay)\s+font\s+file\s+.*?["']?(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)["']?\s+(?:sang|thành)\s+(?P<font_name>[\w\s]+)""",
        keywords=["đổi font", "thay phông", "sửa font word"],
        handler=lambda file_path, font_name: OfficePlugins.change_word_font(file_path, font_name.strip())
    )

    # 6. Word: Chuyển Word sang PDF
    engine.register(
        intent_name="WORD_TO_PDF",
        pattern=r"""(chuyển|xuất|convert)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)\s+sang\s+pdf""",
        keywords=["sang pdf", "chuyển pdf", "word sang pdf"],
        handler=lambda file_path: OfficePlugins.convert_word_to_pdf(file_path)
    )

    # 7. Excel: Tính Toán Cột
    engine.register(
        intent_name="EXCEL_CALCULATE_COL",
        pattern=r"""(tính|cộng)\s+(?P<calc_type>tổng|trung bình|lớn nhất|nhỏ nhất)?\s*cột\s+(?P<col_letter>[a-zA-Z]+)\s+file\s+(?P<file_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tính tổng cột", "trung bình cột", "lớn nhất cột"],
        handler=lambda file_path, col_letter, calc_type="sum": OfficePlugins.calculate_excel_column(file_path, col_letter, calc_type or "sum")
    )

    # 8. System: Workspace & Zip
    engine.register(
        intent_name="SYS_WORKSPACE",
        pattern=r"""(bắt\s+đầu|kích\s+hoạt|mở)\s+(?:ca\s+|không\s+gian\s+)?(?P<workspace_name>lập\s+trình|code|học\s+tập|văn\s+phòng)""",
        keywords=["bắt đầu ca", "mở không gian"],
        handler=lambda workspace_name: SystemPlugins.launch_workspace(workspace_name)
    )

    engine.register(
        intent_name="SYS_SMART_ZIP",
        pattern=r"""gom\s+file\s+trong\s+(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)\s+trong\s+(?P<days>\d+)\s+ngày\s+nén\s+thành\s+zip""",
        keywords=["gom file", "nén zip"],
        handler=lambda folder_path, days=7: SystemPlugins.zip_files_by_condition(folder_path, int(days) if days else 7)
    )

    engine.register(
        intent_name="CODE_GEN_README",
        pattern=r"""(tạo|viết)\s+(?:tài\s+liệu|readme)\s+cho\s+(?:thư\s+mục\s+)?(?P<folder_path>[a-zA-Z]:\\[^"'\n]+|["'].+?["']|\S+)""",
        keywords=["tạo readme", "viết tài liệu"],
        handler=lambda folder_path: CodePlugins.generate_readme_from_code(folder_path)
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
                    result = execute_handler(match.handler, match.entities)
                else:
                    result = execute_handler(match.handler, {})
                console.print(result)
            else:
                console.print("[red]Lệnh chưa rõ hoặc chưa hỗ trợ. Bạn thử gõ lại nhé![/red]")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()