import os
from pathlib import Path

def resolve_path(raw_path: str) -> Path:
    """
    Làm sạch và chuyển đổi mọi chuỗi đường dẫn thành Path hợp lệ.
    Hỗ trợ đường dẫn tuyệt đối (D:\...), đường dẫn có ngoặc kép "...", và ký tự home (~).
    """
    if not raw_path:
        return Path.cwd()
        
    # Xóa khoảng trắng thừa và dấu ngoặc kép ở 2 đầu
    cleaned = raw_path.strip().strip('"').strip("'")
    
    # Mở rộng đường dẫn home (~) nếu có
    expanded = os.path.expanduser(cleaned)
    
    # Chuyển thành Path object tuyệt đối
    path_obj = Path(expanded)
    if not path_obj.is_absolute():
        path_obj = (Path.cwd() / path_obj).resolve()
        
    return path_obj