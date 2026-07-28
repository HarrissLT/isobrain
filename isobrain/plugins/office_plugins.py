from pathlib import Path
from docx import Document
from openpyxl import load_workbook
from docx2pdf import convert
from isobrain.core.utils import resolve_path

class OfficePlugins:
    # ==================== WORD AUTOMATION ====================
    @staticmethod
    def change_word_font(file_path: str, font_name: str) -> str:
        """Đổi font chữ trong Word"""
        path = resolve_path(file_path)
        if not path.exists():
            return f"[bold red]Lỗi:[/bold red] File '{path}' không tồn tại!"
        
        try:
            doc = Document(path)
            for p in doc.paragraphs:
                for run in p.runs:
                    run.font.name = font_name
            doc.save(path)
            return f"[bold green]Thành công![/bold green] Đã đổi font file [yellow]{path.name}[/yellow] sang [cyan]{font_name}[/cyan]."
        except PermissionError:
            return f"[bold red]Lỗi Truy Cập:[/bold red] File [yellow]{path.name}[/yellow] đang mở trong Word. Vui lòng đóng file và thử lại!"
        except Exception as e:
            return f"[bold red]Lỗi:[/bold red] {str(e)}"

    @staticmethod
    def replace_text_word(file_path: str, old_text: str, new_text: str) -> str:
        """Tìm kiếm và thay thế văn bản hàng loạt trong file Word"""
        path = resolve_path(file_path)
        if not path.exists():
            return f"[bold red]Lỗi:[/bold red] File '{path}' không tồn tại!"

        try:
            doc = Document(path)
            replaced_count = 0
            for p in doc.paragraphs:
                if old_text in p.text:
                    p.text = p.text.replace(old_text, new_text)
                    replaced_count += 1
            doc.save(path)
            return f"[bold green]Thành công![/bold green] Đã thay thế [magenta]{replaced_count}[/magenta] đoạn văn chứa từ '[cyan]{old_text}[/cyan]' thành '[cyan]{new_text}[/cyan]'."
        except PermissionError:
            return f"[bold red]Lỗi Truy Cập:[/bold red] File [yellow]{path.name}[/yellow] đang mở. Vui lòng đóng file và thử lại!"
        except Exception as e:
            return f"[bold red]Lỗi:[/bold red] {str(e)}"

    @staticmethod
    def convert_word_to_pdf(file_path: str) -> str:
        """Chuyển đổi file Word (.docx) sang PDF hoàn toàn Offline"""
        path = resolve_path(file_path)
        if not path.exists():
            return f"[bold red]Lỗi:[/bold red] File '{path}' không tồn tại!"

        if path.suffix.lower() != ".docx":
            return f"[bold red]Lỗi:[/bold red] File phải có định dạng .docx!"

        pdf_path = path.with_suffix(".pdf")
        try:
            convert(str(path), str(pdf_path)) # Sử dụng docx2pdf
            return f"[bold green]Thành công![/bold green] Đã xuất file PDF tại: [yellow]{pdf_path}[/yellow]"
        except Exception as e:
            return f"[bold red]Lỗi chuyển PDF:[/bold red] {str(e)}"

    # ==================== EXCEL AUTOMATION ====================
    @staticmethod
    def calculate_excel_column(file_path: str, col_letter: str, calc_type: str = "sum") -> str:
        """Tính toán trên cột Excel: sum (tổng), avg (trung bình), max (lớn nhất), min (nhỏ nhất)"""
        path = resolve_path(file_path)
        if not path.exists():
            return f"[bold red]Lỗi:[/bold red] File '{path}' không tồn tại!"

        try:
            wb = load_workbook(path, data_only=True)
            sheet = wb.active
            col_letter = col_letter.upper()

            values = []
            for cell in sheet[col_letter]:
                if isinstance(cell.value, (int, float)):
                    values.append(cell.value)

            if not values:
                return f"[yellow]Không tìm thấy dữ liệu số nào ở cột {col_letter}.[/yellow]"

            calc_type = calc_type.lower()
            if "trung bình" in calc_type or "avg" in calc_type:
                res = sum(values) / len(values)
                label = "Trung bình"
            elif "lớn nhất" in calc_type or "max" in calc_type:
                res = max(values)
                label = "Giá trị lớn nhất"
            elif "nhỏ nhất" in calc_type or "min" in calc_type:
                res = min(values)
                label = "Giá trị nhỏ nhất"
            else:
                res = sum(values)
                label = "Tổng"

            return f"[bold green]Kết quả:[/bold green] {label} cột [cyan]{col_letter}[/cyan] trong [yellow]{path.name}[/yellow] = [bold magenta]{res:,.2f}[/bold magenta] (từ {len(values)} dòng)."
        except PermissionError:
            return f"[bold red]Lỗi Truy Cập:[/bold red] File [yellow]{path.name}[/yellow] đang mở trong Excel. Vui lòng đóng lại!"
        except Exception as e:
            return f"[bold red]Lỗi:[/bold red] {str(e)}"