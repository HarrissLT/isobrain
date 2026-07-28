import ast
from pathlib import Path
from isobrain.core.utils import resolve_path

class CodePlugins:
    @staticmethod
    def generate_readme_from_code(folder_path: str) -> str:
        """Quét toàn bộ file Python trong thư mục và tự động sinh file README.md mô tả các hàm/lớp"""
        folder = resolve_path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return f"[bold red]Lỗi:[/bold red] Thư mục '{folder}' không tồn tại!"

        py_files = list(folder.glob("*.py"))
        if not py_files:
            return f"[yellow]Không tìm thấy file Python (.py) nào trong '{folder}'.[/yellow]"

        doc_lines = [
            f"# 📖 Tài Liệu Mã Nguồn: `{folder.name}`\n",
            f"*Tự động khởi tạo bởi **IsoBrain** vào {Path.cwd()}*\n",
            "---",
            "## 🗂️ Danh Sách Module & Hàm\n"
        ]

        for py_file in py_files:
            if py_file.name.startswith("__"):
                continue
                
            doc_lines.append(f"### 📄 File: `{py_file.name}`\n")
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=py_file.name)

                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

                if classes:
                    doc_lines.append("**Classes:**")
                    for cls in classes:
                        docstring = ast.get_docstring(cls) or "Không có docstring"
                        doc_lines.append(f"- `class {cls.name}`: *{docstring.strip()}*")
                    doc_lines.append("")

                if functions:
                    doc_lines.append("**Functions:**")
                    for fn in functions:
                        args = [a.arg for a in fn.args.args]
                        docstring = ast.get_docstring(fn) or "Không có docstring"
                        doc_lines.append(f"- `{fn.name}({', '.join(args)})`: *{docstring.strip()}*")
                    doc_lines.append("")

            except Exception as e:
                doc_lines.append(f"*[Lỗi đọc file: {str(e)}]*\n")

        readme_file = folder / "README_AUTO.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write("\n".join(doc_lines))

        return f"[bold green]Thành công![/bold green] Đã quét [magenta]{len(py_files)}[/magenta] file Python và xuất tài liệu tại: [yellow]{readme_file}[/yellow]"