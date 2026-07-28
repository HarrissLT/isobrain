import re
from typing import List, Tuple, Callable, Dict, Any
from rapidfuzz import fuzz
from isobrain.core.models import IntentMatch

class IntentEngine:
    def __init__(self):
        self.rules: List[Tuple[str, str, List[str], Callable]] = []

    def register(self, intent_name: str, pattern: str, keywords: List[str], handler: Callable):
        self.rules.append((intent_name, pattern, keywords, handler))

    def _extract_fallback_entities(self, text: str) -> Dict[str, Any]:
        """Tự động rút trích tham số thông minh khi rơi vào Layer 2 Fuzzy Matching"""
        entities = {}
        text_lower = text.lower()
        
        # 1. Trích xuất đường dẫn Windows
        path_match = re.search(r"""([a-zA-Z]:\\[^"'\n]+?)(?=\s+từ|\s+thành|\s+sang|\s+trong|$)""", text)
        if not path_match:
            path_match = re.search(r"""["'](?P<path>[a-zA-Z]:\\[^"']+)["']""", text)
        if path_match:
            extracted_path = path_match.group(1).strip('"\' ')
            entities["folder_path"] = extracted_path
            entities["file_path"] = extracted_path

        # 2. Trích xuất mode (nhẹ nhất vs nặng nhất)
        if "nhẹ" in text_lower or "nhỏ" in text_lower:
            entities["mode"] = "smallest"
        elif "nặng" in text_lower or "lớn" in text_lower:
            entities["mode"] = "largest"

        # 3. Trích xuất con số Top N (ví dụ: 5 file)
        top_n_match = re.search(r'(\d+)\s*file', text_lower)
        if top_n_match:
            entities["top_n"] = top_n_match.group(1)

        # 4. Trích xuất từ ngữ sau 'từ', 'thành', 'sang'
        from_match = re.search(r"""từ\s+["']?(?P<old_str>[^\s"']+)""", text, re.IGNORECASE)
        if from_match:
            entities["old_str"] = from_match.group("old_str")

        to_match = re.search(r"""(?:thành|sang)\s+["']?(?P<target>[^"'\n]+)""", text, re.IGNORECASE)
        if to_match:
            target_val = to_match.group("target").strip()
            entities["new_str"] = target_val
            entities["font_name"] = target_val

        # 5. Trích xuất tên file
        file_name_match = re.search(r"""[\w\.-]+\.(docx|xlsx|pdf|txt)""", text, re.IGNORECASE)
        if file_name_match:
            entities["file_name"] = file_name_match.group(0)

        return entities

    def parse(self, text: str) -> IntentMatch:
        text_clean = text.strip()
        
        # 1. LAYER 1: Regex Matching
        for intent_name, pattern, _, handler in self.rules:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                entities = {k: v.strip('"\' ') if isinstance(v, str) else v for k, v in match.groupdict().items() if v is not None}
                return IntentMatch(
                    intent_name=intent_name,
                    confidence=1.0,
                    entities=entities,
                    handler=handler
                )
        
        # 2. LAYER 2: Fuzzy Matching + Smart Entity Extraction
        best_intent = None
        best_score = 0.0
        best_handler = None
        
        for intent_name, _, keywords, handler in self.rules:
            for kw in keywords:
                score = fuzz.partial_ratio(kw.lower(), text_clean.lower())
                if score > best_score and score >= 60.0:
                    best_score = score
                    best_intent = intent_name
                    best_handler = handler

        if best_intent:
            fallback_entities = self._extract_fallback_entities(text_clean)
            return IntentMatch(
                intent_name=best_intent,
                confidence=best_score / 100.0,
                entities=fallback_entities,
                handler=best_handler
            )

        return IntentMatch(intent_name="UNKNOWN", confidence=0.0)