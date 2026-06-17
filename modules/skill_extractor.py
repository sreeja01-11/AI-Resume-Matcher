import json
import re
import os
from typing import Dict, List, Set, Any

class SkillExtractor:
    def __init__(self, skills_json_path: str):
        self.skills_json_path = skills_json_path
        self.skill_to_category: Dict[str, str] = {}
        self.alias_map: Dict[str, str] = {}
        self.canonical_skills: List[str] = []
        self._load_and_prepare_skills()

    def _load_and_prepare_skills(self) -> None:
        if not os.path.exists(self.skills_json_path):
            raise FileNotFoundError(f"Skills database not found: {self.skills_json_path}")
        try:
            with open(self.skills_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            categories = data.get("skills", {})
            for category, skill_list in categories.items():
                for skill in skill_list:
                    normalized = skill.lower().strip()
                    self.skill_to_category[normalized] = category
            self.alias_map = {k.lower(): v.lower() for k, v in data.get("aliases", {}).items()}
            self.canonical_skills = sorted(
                self.skill_to_category.keys(),
                key=len,
                reverse=True
            )
            self.skill_pattern = self._build_regex_pattern(self.canonical_skills)
            if self.alias_map:
                self.alias_pattern = self._build_regex_pattern(
                    list(self.alias_map.keys())
                )
            else:
                self.alias_pattern = None
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse skills JSON: {e}")

    def _build_regex_pattern(self, items: List[str]) -> re.Pattern:
        pattern_string = r"(?<![a-zA-Z0-9])(" + "|".join(re.escape(i) for i in items) + r")(?![a-zA-Z0-9])"
        return re.compile(pattern_string, re.IGNORECASE)

    def _normalize_text(self, text: str) -> str:
        if not self.alias_pattern:
            return text.lower()
        def replace_match(match):
            term = match.group(0).lower()
            return self.alias_map.get(term, term)
        return self.alias_pattern.sub(
            replace_match,
            text.lower()
        )

    def extract_skills(self, text: str) -> Dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            return {"skills": [], "count": 0, "categories": {}}
        normalized_text = self._normalize_text(text)
        found_skills: Set[str] = set()
        for match in self.skill_pattern.finditer(normalized_text):
            found_skills.add(match.group(0).lower())
        sorted_found = sorted(list(found_skills))
        skill_cat_map = {skill: self.skill_to_category[skill] for skill in sorted_found}
        return {
            "skills": sorted_found,
            "count": len(sorted_found),
            "categories": skill_cat_map
        }

    def group_by_category(self, extraction_result: Dict[str, Any]) -> Dict[str, List[str]]:
        grouped: Dict[str, List[str]] = {}
        for skill, category in extraction_result.get("categories", {}).items():
            grouped.setdefault(category, []).append(skill)
        return grouped