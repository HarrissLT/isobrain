import os
import time
import zipfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from isobrain.core.utils import resolve_path

class SystemPlugins:
    # ==================== TÍNH NĂNG 7: WORKSPACE AUTOMATION ====================
    @staticmethod
    def launch_workspace(workspace_name: str) -> str:
        """Thiết lập môi trường làm việc theo bối cảnh"""
        ws = workspace_name.strip().lower()
        opened = []
        
        if "lập trình" in ws or "code" in ws or "python" in ws:
            # Mở VS Code
            subprocess.Popen(["code"])
            opened.append("VS Code")
            # Mở trang tài liệu Python trên trình duyệt
            os.system("start https://docs.python.org/3/")
            opened.append("Python Docs (Browser)")
            return f"[bold green]Đã kích hoạt không gian '[cyan]Học Lập Trình[/cyan]'![/bold green]\nĐã mở: {', '.join(opened)}"
            
        elif "học tập" in ws or "study" in ws or "văn phòng" in ws:
            subprocess.Popen(["notepad"])
            opened.append("Notepad")
            return f"[bold green]Đã kích hoạt không gian '[cyan]Học Tập / Văn Phòng[/cyan]'![/bold green]\nĐã mở: {', '.join(opened)}"
            
        return f"[yellow]Chưa định nghĩa không gian làm việc '[cyan]{workspace_name}[/cyan]'. Bạn có thể thêm cấu hình trong system_plugin.py![/yellow]"

    # ==================== TÍNH NĂNG 9: SMART CONDITIONAL ZIP ====================
    @staticmethod
    def zip_files_by_condition(folder_path: str, days: int = 7, file_type: str = "docx") -> str:
        """Gom và nén các file được sửa đổi trong N ngày qua thành file ZIP trên Desktop"""
        source_folder = resolve_path(folder_path)
        if not source_folder.exists() or not source_folder.is_dir():
            return f"[bold red]Lỗi:[/bold red] Thư mục '{source_folder}' không tồn tại!"

        desktop_path = Path.home() / "Desktop"
        zip_filename = f"BaoCao_GomNhom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        target_zip = desktop_path / zip_filename

        cutoff_time = datetime.now() - timedelta(days=int(days))
        ext = f".{file_type.strip().strip('.')}"

        zipped_files = []
        with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_folder):
                for file in files:
                    if file.endswith(ext):
                        file_full_path = Path(root) / file
                        # Kiểm tra ngày chỉnh sửa (mtime)
                        mtime = datetime.fromtimestamp(file_full_path.stat().st_mtime)
                        if mtime >= cutoff_time:
                            arcname = file_full_path.relative_to(source_folder)
                            zipf.write(file_full_path, arcname)
                            zipped_files.append(file)

        if not zipped_files:
            if target_zip.exists():
                target_zip.unlink() # Xóa file zip rỗng
            return f"[yellow]Không có file {ext} nào được chỉnh sửa trong {days} ngày qua tại '{source_folder}'.[/yellow]"

        return f"[bold green]Thành công![/bold green] Đã nén [magenta]{len(zipped_files)}[/magenta] file {ext} vào: [yellow]{target_zip}[/yellow]"

    # ==================== TÍNH NĂNG 3: SMART CLIPBOARD ====================
    @staticmethod
    def process_clipboard() -> str:
        """Đọc và làm sạch văn bản trong Khay nhớ tạm (Clipboard)"""
        try:
            import pyperclip
            text = pyperclip.paste()
            if not text or not text.strip():
                return "[yellow]Khay nhớ tạm (Clipboard) đang trống![/yellow]"

            # Xử lý làm sạch: Xóa khoảng trắng thừa, sửa lỗi xuống dòng
            cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            pyperclip.copy(cleaned_text)

            preview = cleaned_text[:60] + "..." if len(cleaned_text) > 60 else cleaned_text
            return f"[bold green]Đã chuẩn hóa văn bản trong Clipboard![/bold green]\n[italic gray]Nội dung:[/italic gray] \"{preview}\""
        except ImportError:
            return "[red]Vui lòng cài đặt pyperclip bằng lệnh: pip install pyperclip[/red]"
        except Exception as e:
            return f"[bold red]Lỗi Clipboard:[/bold red] {str(e)}"