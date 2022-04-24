from typing import Callable, List, Tuple


CONFIG_ITEMS = {
    "autoadd": (False, bool),
    "brief_unknown_words": (True, bool),
    "brief_case_sensitive": (True, bool),
    "brief_cap_phrases": (True, bool),
    "override": (False, bool),
    "exclude_chars": ("()'\",.", str),
    "to_dict": ("", str),
    "brief_gen": ("", str), 
    "min_length": (4, int),
    "min_strokes": (4, int),
    "search_depth": (6, int),
    "row_height": (30, int),
    "page_len": (10, int)
}


class AutobriefConfig:
    def __init__(self, values: dict = None) -> None:
        if values is None:
            values = dict()

        for key, (default, _) in CONFIG_ITEMS.items():
            if key in values:
                setattr(self, key, values[key])
            else:
                setattr(self, key, default)

    def copy(self) -> "AutobriefConfig":
        value_dict = {k: getattr(self, k) for k in CONFIG_ITEMS.keys()}
        return AutobriefConfig(value_dict)

    def load_brief_gen(self) -> None:
        if hasattr(self, "brief_gen") and self.brief_gen:
            try:
                with open(self.brief_gen, encoding="utf-8") as fp:
                    source = fp.read()
                
                globs = {}
                exec(source, globs)
                
                get_briefs = globs.get("get_briefs")
                if not isinstance(get_briefs, Callable):
                    self._get_briefs = None
                
                self._get_briefs = get_briefs
            
            except (FileNotFoundError, OSError) as _:
                self._get_briefs = None
    
    def get_briefs(self, text: str) -> List[Tuple[str, ...]]:
        if hasattr(self, "_get_briefs") and self._get_briefs is not None:
            return self._get_briefs(text)
        
        return []

    def no_briefer(self) -> bool:
        return not (hasattr(self, "_get_briefs") and self._get_briefs is not None)
