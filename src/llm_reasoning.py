"""
llm_reasoning.py - Layer 5 LLM Reasoning & Synthesis Engine
------------------------------------------------------------
This module leverages Google Gemini (gemini-2.5-flash / gemini-3.1-flash-lite) to inspect
top retrieved candidate resume excerpts, verify skill claims, and synthesize human-readable
match reasoning explaining why a candidate scored high or low.
Optimized to generate reasoning in a single batch prompt to minimize API calls and latency.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMReasoningEngine:
    """
    LLM Reasoning Engine generating transparent match explanations and verbatim excerpt verifications.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.strip() in ["your_gemini_api_key_here", ""]:
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception:
            self.client = None

    def synthesize_heuristic_reasoning(
        self,
        candidate_name: str,
        match_score: int,
        passed_filters: bool,
        filter_failures: List[str],
        matched_skills: Dict[str, List[str]],
        missing_skills: List[str],
        experience_years: float,
        min_exp_req: float,
        jd_title: str
    ) -> str:
        """Rule-based match explanation fallback."""
        must_have = matched_skills.get("must_have", [])
        
        if passed_filters:
            exp_status = f"exceeds the {min_exp_req}-year requirement with {experience_years} years" if experience_years >= min_exp_req else f"possesses {experience_years} years of experience"
            skills_str = ", ".join(must_have[:4]) if must_have else "the required technical stack"
            return (
                f"Candidate exceeds minimum qualifications for {jd_title} with {experience_years} years experience and {match_score}/100 match score. "
                f"Possesses mandatory skills in {skills_str}."
            )
        else:
            failures_str = "; ".join(filter_failures) if filter_failures else "did not meet mandatory requirements"
            return (
                f"Candidate scored {match_score}/100 but failed mandatory job constraints ({failures_str}). "
                f"Does not meet all non-negotiable requirements for {jd_title}."
            )

    def generate_candidate_reasoning_batch(
        self,
        candidates: List[Dict[str, Any]],
        jd_summary: Dict[str, Any]
    ) -> List[str]:
        """
        Generates 2-3 sentence transparent match rationale for ALL top candidates in 1 single API call.
        """
        jd_title = jd_summary.get("title", "Target Position")
        min_exp = jd_summary.get("min_experience_years", 0.0)

        # Build fallback array first
        fallbacks = []
        for cand in candidates:
            reasoning = self.synthesize_heuristic_reasoning(
                candidate_name=cand["candidate_name"],
                match_score=cand["match_score"],
                passed_filters=cand["passed_mandatory_filters"],
                filter_failures=cand.get("filter_failures", []),
                matched_skills=cand["matched_skills"],
                missing_skills=cand.get("missing_skills", []),
                experience_years=cand["experience_years"],
                min_exp_req=min_exp,
                jd_title=jd_title
            )
            fallbacks.append(reasoning)

        if not self.client:
            return fallbacks

        # Construct batch prompt for 1 API call
        prompt = f"""
You are an expert HR recruitment evaluator. Write a concise, professional 2-sentence match explanation for each candidate below applying for '{jd_title}'.

Target Role Requirements:
- Title: {jd_title}
- Required Minimum Experience: {min_exp} years

Candidates Data:
"""
        for idx, c in enumerate(candidates, start=1):
            prompt += f"""
Candidate #{idx}: {c['candidate_name']}
- Match Score: {c['match_score']}/100 | Passed Constraints: {c['passed_mandatory_filters']}
- Hard Filter Failures: {c.get('filter_failures', [])}
- Experience: {c['experience_years']} yrs
- Matched Must-Have Skills: {c['matched_skills'].get('must_have', [])}
- Excerpts: {c.get('relevant_excerpts', [])[:1]}
"""

        prompt += """
Return a valid JSON array of strings containing the match rationale for each candidate in order. Example format:
["Rationale for candidate 1...", "Rationale for candidate 2..."]
"""

        try:
            res = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            if hasattr(res, 'text') and res.text:
                text_content = res.text.strip()
                # Parse JSON array from response
                start_idx = text_content.find("[")
                end_idx = text_content.rfind("]") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = text_content[start_idx:end_idx]
                    parsed_reasons = json.loads(json_str)
                    if isinstance(parsed_reasons, list) and len(parsed_reasons) == len(candidates):
                        return [str(r) for r in parsed_reasons]
        except Exception as e:
            print(f"[WARN] Batch LLM reasoning call failed: {e}. Using heuristic explanations.")

        return fallbacks


if __name__ == "__main__":
    print("=== Testing LLMReasoningEngine Batch ===")
    engine = LLMReasoningEngine()
    cands = [{
        "candidate_name": "John Doe",
        "match_score": 94,
        "passed_mandatory_filters": True,
        "filter_failures": [],
        "matched_skills": {"must_have": ["Python", "FastAPI", "LangChain"]},
        "missing_skills": [],
        "experience_years": 7.0,
        "relevant_excerpts": ["Senior AI Engineer with 7+ years experience in Python."]
    }]
    reasons = engine.generate_candidate_reasoning_batch(cands, {"title": "Senior AI Systems Engineer", "min_experience_years": 5.0})
    print("\nSynthesized Rationale:\n", reasons[0])
