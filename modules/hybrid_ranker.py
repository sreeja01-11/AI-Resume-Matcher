from typing import List, Dict, Set, Any
from modules import matcher 

def calculate_keyword_score(resume_skills: Set[str], job_skills: Set[str]) -> float:
    if not job_skills:
        return 0.0
    res_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    matched = res_set.intersection(job_set)
    return round(len(matched) / len(job_set), 4)

def get_skill_gap_analysis(resume_skills: Set[str], job_skills: Set[str]) -> Dict[str, List[str]]:
    res_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    matched = sorted(list(res_set.intersection(job_set)))
    missing = sorted(list(job_set.difference(res_set)))
    return {"matched_skills": matched,"missing_skills": missing}

def calculate_final_score(semantic_score: float, keyword_score: float) -> float:
    final = (0.7 * semantic_score) + (0.3 * keyword_score)
    return round(final, 4)

def rank_jobs_hybrid(resume_text: str, resume_skills: List[str], jobs: List[Dict]) -> List[Dict]:
    ranked_list = []
    resume_skills_set = set(s.lower() for s in resume_skills)
    for job in jobs:
        job_desc = job.get('description', '')
        sem_score = matcher.calculate_similarity(resume_text, job_desc)
        job_skills = set(s.lower() for s in job.get('skills', []))
        key_score = calculate_keyword_score(resume_skills_set, job_skills)
        gap = get_skill_gap_analysis(resume_skills_set, job_skills)
        final_score = calculate_final_score(sem_score, key_score)
        job_result = job.copy()
        job_result.update({
            "semantic_score": sem_score,
            "keyword_score": key_score,
            "final_score": final_score,
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"]
        })
        ranked_list.append(job_result)
    return sorted(ranked_list, key=lambda x: x['final_score'], reverse=True)