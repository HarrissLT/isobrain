import os
from pathlib import Path
from docx import Document
from openpyxl import Workbook
from isobrain.core.utils import resolve_path

class FilePlugins:
    @staticmethod
    def create_file(file_name: str, folder_path: str) -> str:
        """Tạo file mới (.docx, .xlsx, .txt) tự động tạo thư mục nếu chưa có"""
        folder = resolve_path(folder_path)
        
        # Làm sạch tên file
        clean_file_name = file_name.strip().strip('"').strip("'")
        
        # Tự tạo thư mục nếu chưa tồn tại
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            
        full_path = folder / clean_file_name
        
        try:
            ext = full_path.suffix.lower()
            if ext == ".docx":
                doc = Document()
                doc.add_heading(f"Tài liệu: {clean_file_name}", level=1)
                doc.save(full_path)
            elif ext == ".xlsx":
                wb = Workbook()
                wb.save(full_path)
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("")
                    
            return f"[bold green]Thành công![/bold green] Đã tạo file [cyan]{clean_file_name}[/cyan] tại [yellow]{full_path}[/yellow]."
        except Exception as e:
            return f"[bold red]Lỗi tạo file:[/bold red] {str(e)}"

    @staticmethod
    def batch_rename(folder_path: str, old_str: str, new_str: str) -> str:
        """Đổi tên hàng loạt file trong thư mục"""
        folder = resolve_path(folder_path)
        
        # Nếu truyền vào đường dẫn file trực tiếp, lấy thư mục cha
        if folder.is_file():
            folder = folder.parent
            
        if not folder.exists() or not folder.is_dir():
            return f"[bold red]Lỗi:[/bold red] Thư mục '{folder}' không tồn tại!"

        renamed_count = 0
        try:
            for item in folder.iterdir():
                if item.is_file() and old_str.lower() in item.name.lower():
                    # Đổi tên giữ nguyên đuôi file
                    new_name = item.name.replace(old_str, new_str)
                    new_path = item.parent / new_name
                    item.rename(new_path)
                    renamed_count += 1

            if renamed_count == 0:
                return f"[yellow]Không tìm thấy file nào chứa chuỗi '{old_str}' trong thư mục '{folder}'.[/yellow]"

            return f"[bold green]Thành công![/bold green] Đã đổi tên [magenta]{renamed_count}[/magenta] file trong [yellow]{folder}[/yellow]."
        except Exception as e:
            return f"[bold red]Lỗi đổi tên file:[/bold red] {str(e)}"

    @staticmethod
    def list_files_by_ext(folder_path: str, extension: str) -> str:
        """Liệt kê danh sách file theo định dạng"""
        folder = resolve_path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return f"[bold red]Lỗi:[/bold red] Thư mục '{folder}' không tồn tại!"

        ext = extension.strip().lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        files = [f.name for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ext]
        if not files:
            return f"[yellow]Không tìm thấy file nào có đuôi '{ext}' trong '{folder}'.[/yellow]"

        file_list_str = "\n".join([f"  • [cyan]{name}[/cyan]" for name in files])
        return f"[bold green]Tìm thấy {len(files)} file {ext} trong [yellow]{folder}[/yellow]:[/bold green]\n{file_list_str}"