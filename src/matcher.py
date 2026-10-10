"""
matcher.py - Layer 4 Top-K Hard Filtering & 0-100 Relevance Scoring Engine
---------------------------------------------------------------------------
This module evaluates retrieved Top-K candidates against strict non-negotiable constraints
(Minimum Experience Years, Mandatory Tech Stack) and computes normalized 0-100 match scores.
"""

import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Tuple, Optional

from retriever import HybridRetriever, CandidateHit, JobDescriptionParsed


@dataclass
class EvaluatedCandidate:
    """Dataclass representing a fully evaluated and scored candidate profile."""
    rank: int
    candidate_id: str
    candidate_name: str
    resume_path: str
    match_score: int                     # 0 to 100 quantitative match score
    passed_mandatory_filters: bool
    filter_failures: List[str]           # Failure reasons if passed_mandatory_filters is False
    matched_skills: Dict[str, List[str]] # {"must_have": [...], "preferred": [...]}
    missing_skills: List[str]            # Missing mandatory / preferred skills
    experience_years: float
    relevant_excerpts: List[str]         # Verbatim section excerpts from resume

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProfileMatcher:
    """
    Top-K Hard Constraint Filter Evaluator & 0-100 Quantitative Match Scoring Engine.
    """

    def __init__(self, retriever: Optional[HybridRetriever] = None):
        self.retriever = retriever or HybridRetriever()

    def evaluate_hard_filters(
        self,
        candidate_exp: float,
        candidate_skills: List[str],
        min_experience_req: float,
        mandatory_skills: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Evaluates candidate attributes against strict non-negotiable job constraints.

        Returns:
            Tuple[bool, List[str]]: (passed_filters, list_of_failure_reasons)
        """
        failures = []

        # 1. Experience Years Filter
        if min_experience_req > 0 and candidate_exp < min_experience_req:
            failures.append(
                f"Failed: Insufficient Experience ({candidate_exp} yrs < {min_experience_req} yrs required)"
            )

        # 2. Mandatory / Must-Have Skill Filter
        cand_skills_lower = {s.lower() for s in candidate_skills}
        for skill in mandatory_skills:
            if skill.lower() not in cand_skills_lower:
                failures.append(f"Failed: Missing mandatory skill '{skill}'")

        passed = len(failures) == 0
        return passed, failures

    def compute_match_score(
        self,
        semantic_score: float,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        candidate_exp: float,
        min_exp_req: float
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Computes 0-100 quantitative match score based on 4-part weighted formula:
        Score = (40% * Semantic) + (35% * Skills) + (15% * Experience) + (10% * Education/Domain)
        """
        cand_skills_lower = {s.lower() for s in candidate_skills}

        # Part 1: Semantic Vector Similarity (40% Weight)
        # Cosine similarity in Pinecone is typically between 0.4 and 0.85 for resumes
        # Scale & normalize semantic score to 0-100
        norm_semantic = max(0.0, min(1.0, (semantic_score - 0.3) / 0.55))
        semantic_component = norm_semantic * 100.0 * 0.40

        # Part 2: Required & Preferred Skills Coverage (35% Weight)
        matched_must_have = [s for s in required_skills if s.lower() in cand_skills_lower]
        missing_must_have = [s for s in required_skills if s.lower() not in cand_skills_lower]
        
        matched_preferred = [s for s in preferred_skills if s.lower() in cand_skills_lower]
        missing_preferred = [s for s in preferred_skills if s.lower() not in cand_skills_lower]

        req_ratio = len(matched_must_have) / len(required_skills) if required_skills else 1.0
        pref_ratio = len(matched_preferred) / len(preferred_skills) if preferred_skills else 1.0

        skills_ratio = 0.80 * req_ratio + 0.20 * pref_ratio
        skills_component = skills_ratio * 100.0 * 0.35

        # Part 3: Experience Relevance (15% Weight)
        if min_exp_req > 0:
            exp_ratio = min(1.2, candidate_exp / min_exp_req)
        else:
            exp_ratio = 1.0
        exp_component = min(1.0, exp_ratio) * 100.0 * 0.15

        # Part 4: Education & Domain Fit Baseline (10% Weight)
        education_component = 85.0 * 0.10

        # Aggregate total score (0 to 100)
        total_score = round(semantic_component + skills_component + exp_component + education_component)
        clamped_score = max(0, min(100, total_score))

        skill_breakdown = {
            "matched_skills": {
                "must_have": matched_must_have,
                "preferred": matched_preferred
            },
            "missing_skills": missing_must_have + missing_preferred
        }

        return clamped_score, skill_breakdown

    def match_candidates(self, jd_input: str, top_k_candidates: int = 10) -> Dict[str, Any]:
        """
        Main matching engine: executes hybrid retrieval, applies hard constraint filters,
        calculates 0-100 match scores, and ranks candidates.

        Args:
            jd_input (str): Job Description text string or file path.
            top_k_candidates (int): Number of top candidates to return.

        Returns:
            Dict[str, Any]: Complete matching report dict.
        """
        # Step 1: Execute Hybrid Retrieval
        retrieval_res = self.retriever.hybrid_retrieve(jd_input, top_k_chunks=35)
        parsed_jd = retrieval_res["job_description"]
        candidate_hits = retrieval_res["candidate_hits"]

        req_skills = parsed_jd["required_skills"]
        pref_skills = parsed_jd["preferred_skills"]
        min_exp = float(parsed_jd["min_experience_years"])

        evaluated_list: List[EvaluatedCandidate] = []

        # Step 2: Evaluate Hard Filters & Compute 0-100 Scores
        for cand_hit in candidate_hits:
            cand_id = cand_hit["candidate_id"]
            cand_name = cand_hit["candidate_name"]
            resume_path = cand_hit["resume_path"]
            cand_exp = float(cand_hit["experience_years"])
            cand_skills = cand_hit["skills_list"]
            semantic_score = float(cand_hit["max_semantic_score"])

            # Hard Constraint Filter Verification
            passed_filters, failures = self.evaluate_hard_filters(
                candidate_exp=cand_exp,
                candidate_skills=cand_skills,
                min_experience_req=min_exp,
                mandatory_skills=req_skills
            )

            # Compute 0-100 quantitative score
            match_score, skill_details = self.compute_match_score(
                semantic_score=semantic_score,
                candidate_skills=cand_skills,
                required_skills=req_skills,
                preferred_skills=pref_skills,
                candidate_exp=cand_exp,
                min_exp_req=min_exp
            )

            # Extract relevant resume excerpts from top chunks
            excerpts = []
            for chunk in cand_hit.get("top_chunks", [])[:2]:
                text = chunk.get("chunk_text", "").strip()
                # Clean prepended header if present
                clean_text = re.sub(r"^\[Candidate:.*?\]\n", "", text).strip()
                if clean_text:
                    excerpts.append(clean_text[:250] + "..." if len(clean_text) > 250 else clean_text)

            evaluated_list.append(EvaluatedCandidate(
                rank=0,  # Will be set after sorting
                candidate_id=cand_id,
                candidate_name=cand_name,
                resume_path=resume_path,
                match_score=match_score,
                passed_mandatory_filters=passed_filters,
                filter_failures=failures,
                matched_skills=skill_details["matched_skills"],
                missing_skills=skill_details["missing_skills"],
                experience_years=cand_exp,
                relevant_excerpts=excerpts
            ))

        # Step 3: Sort & Rank Candidates
        # Partition into passed filters vs failed filters
        passed_candidates = [c for c in evaluated_list if c.passed_mandatory_filters]
        failed_candidates = [c for c in evaluated_list if not c.passed_mandatory_filters]

        # Sort both groups by match score descending
        passed_candidates.sort(key=lambda x: x.match_score, reverse=True)
        failed_candidates.sort(key=lambda x: x.match_score, reverse=True)

        final_ranked = passed_candidates + failed_candidates
        for rank_idx, candidate in enumerate(final_ranked, start=1):
            candidate.rank = rank_idx

        # Slice to requested top_k_candidates
        top_matches = final_ranked[:top_k_candidates]

        return {
            "job_description_summary": {
                "title": parsed_jd["title"],
                "min_experience_years": min_exp,
                "required_skills": req_skills,
                "preferred_skills": pref_skills
            },
            "total_candidates_evaluated": len(final_ranked),
            "candidates_passed_filters": len(passed_candidates),
            "candidates_failed_filters": len(failed_candidates),
            "top_matches": [c.to_dict() for c in top_matches]
        }


if __name__ == "__main__":
    print("=== Testing ProfileMatcher Engine ===")
    sample_jd = """
    Job Title: Senior AI & LLM Systems Engineer
    Required Experience: Minimum 5+ years of experience.
    Required Skills: Python, LangChain, FastAPI, Vector Databases.
    Preferred Skills: Docker, Kubernetes, AWS, Pinecone.
    """

    matcher = ProfileMatcher()
    results = matcher.match_candidates(sample_jd, top_k_candidates=10)

    print(f"\nTarget Position: {results['job_description_summary']['title']}")
    print(f"Total Evaluated: {results['total_candidates_evaluated']} | Passed Filters: {results['candidates_passed_filters']} | Failed: {results['candidates_failed_filters']}\n")

    for cand in results['top_matches']:
        status = "PASSED" if cand['passed_mandatory_filters'] else "FAILED"
        print(f"Rank #{cand['rank']}: {cand['candidate_name']} (Score: {cand['match_score']}/100) [{status}]")
        print(f"  Exp: {cand['experience_years']} yrs | Matched Must-Have: {cand['matched_skills']['must_have']}")
        if cand['filter_failures']:
            print(f"  Filter Failures: {cand['filter_failures']}")
        print(f"  Excerpts: {cand['relevant_excerpts'][:1]}\n" + "-"*55)
