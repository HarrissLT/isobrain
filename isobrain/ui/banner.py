from rich.console import Console
from rich.panel import Panel
from rich.table import Table

def display_welcome_banner(console: Console):
    ascii_art = """[bold cyan]
  ██████╗ ███████╗ ██████╗ ██████╗ ██████╗  █████╗ ██╗███╗   ██╗
  ██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║
  ██║  ██║███████╗██║   ██║██████╔╝██████╔╝███████║██║██╔██╗ ██║
  ██║  ██║╚════██║██║   ██║██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║
  ██████╔╝███████║╚██████╔╝██████╔╝██║  ██║██║  ██║██║██║ ╚████║
  ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
    [/bold cyan]"""
    
    console.print(ascii_art)
    
    table = Table(title="[bold yellow]IsoBrain v0.1.0 - Local Offline AI Agent[/bold yellow]", show_header=True, header_style="bold magenta")
    table.add_column("Nhóm Lệnh", style="cyan", width=18)
    table.add_column("Cú Pháp / Câu Lệnh Mẫu", style="white")
    
    table.add_row("Word Automation", "Đổi font file baocao.docx sang Arial")
    table.add_row("Excel Automation", "Tính tổng cột D file luong.xlsx")
    table.add_row("Hệ Thống", "Gõ 'exit' hoặc 'quit' để thoát")
    
    panel = Panel(table, border_style="blue", title="[bold green]Tác giả: Harriss[/bold green]", subtitle="[italic gray]100% Private - No API - Super Fast[/italic gray]")
    console.print(panel)