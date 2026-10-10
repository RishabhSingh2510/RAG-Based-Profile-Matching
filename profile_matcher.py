"""
profile_matcher.py - Main RAG Resume Profile Matching Application & CLI Interface
-----------------------------------------------------------------------------------
Main system entry point connecting multi-format parsing, section-aware chunking,
Pinecone vector similarity, top-K hard constraint filtering, 0-100 quantitative scoring,
and Gemini LLM match reasoning into a structured JSON output interface.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from matcher import ProfileMatcher
from llm_reasoning import LLMReasoningEngine
from logger import SessionLogger



def run_profile_matcher(
    jd_input: str,
    top_k: int = 10,
    output_json_path: Optional[str] = None,
    log_dir: str = "logs"
) -> Dict[str, Any]:
    """
    Main orchestration function running full RAG candidate matching pipeline.

    Args:
        jd_input (str): Job Description raw text string or file path.
        top_k (int): Number of top candidate matches to return.
        output_json_path (Optional[str]): Output JSON file path to write results.
        log_dir (str): Session log directory path.

    Returns:
        Dict[str, Any]: Final JSON match report conforming to target schema.
    """
    logger = SessionLogger(log_dir=log_dir)
    logger.log("SYSTEM START", f"Running RAG Profile Matcher (Top K = {top_k})")

    # Step 1: Execute Profile Matching & Hard Filtering Engine
    matcher = ProfileMatcher()
    match_results = matcher.match_candidates(jd_input, top_k_candidates=top_k)

    jd_summary = match_results["job_description_summary"]
    top_matches = match_results["top_matches"]

    logger.log("JD PARSED", f"Title: '{jd_summary['title']}' | Min Exp: {jd_summary['min_experience_years']} yrs | Required Skills: {jd_summary['required_skills']}")

    # Step 2: Synthesize LLM Reasoning via Gemini in 1 Single Batch Prompt
    reasoning_engine = LLMReasoningEngine()
    logger.log("REASONING START", f"Generating LLM match reasoning for top {len(top_matches)} candidate matches in 1 batch call...")

    rationales = reasoning_engine.generate_candidate_reasoning_batch(top_matches, jd_summary)

    formatted_matches = []
    for cand, reasoning in zip(top_matches, rationales):
        formatted_matches.append({
            "rank": cand["rank"],
            "candidate_name": cand["candidate_name"],
            "resume_path": cand["resume_path"],
            "match_score": cand["match_score"],
            "passed_mandatory_filters": cand["passed_mandatory_filters"],
            "matched_skills": cand["matched_skills"],
            "missing_skills": cand["missing_skills"],
            "relevant_excerpts": cand["relevant_excerpts"],
            "match_reasoning": reasoning
        })

    # Step 3: Construct Target JSON Schema Output
    final_output = {
        "job_description_summary": jd_summary,
        "total_candidates_evaluated": match_results["total_candidates_evaluated"],
        "candidates_passed_filters": match_results["candidates_passed_filters"],
        "candidates_failed_filters": match_results["candidates_failed_filters"],
        "top_matches": formatted_matches
    }

    logger.log("PIPELINE COMPLETE", f"Successfully evaluated {final_output['total_candidates_evaluated']} candidates.")

    # Step 4: Write JSON output if path provided
    if output_json_path:
        try:
            out_dir = os.path.dirname(output_json_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=2)
            logger.log("JSON EXPORT", f"Match report written to '{output_json_path}'")
            print(f"\n[SUCCESS] Matching report exported to '{output_json_path}'")
        except Exception as e:
            logger.log("ERROR", f"Failed to write JSON output: {e}")
            print(f"[ERROR] Failed to write JSON output file: {e}")

    return final_output


def print_cli_report(report: Dict[str, Any]):
    """Prints clean terminal summary table."""
    jd = report["job_description_summary"]
    print("\n" + "=" * 70)
    print("        RAG RESUME PROFILE MATCHING SYSTEM - FINAL REPORT")
    print("=" * 70)
    print(f"Target Position: {jd['title']}")
    print(f"Min Experience:  {jd['min_experience_years']} years")
    print(f"Required Skills: {', '.join(jd['required_skills']) if jd['required_skills'] else 'None'}")
    print(f"Total Evaluated: {report['total_candidates_evaluated']} | Passed Filters: {report['candidates_passed_filters']} | Failed: {report['candidates_failed_filters']}")
    print("=" * 70 + "\n")

    for cand in report["top_matches"]:
        status_tag = "PASSED" if cand["passed_mandatory_filters"] else "FAILED"
        print(f"Rank #{cand['rank']}: {cand['candidate_name']}  (Match Score: {cand['match_score']}/100) [{status_tag}]")
        print(f"   Resume: {cand['resume_path']}")
        print(f"   Matched Must-Have: {cand['matched_skills']['must_have']}")
        if cand['missing_skills']:
            print(f"   Missing Skills:    {cand['missing_skills']}")
        print(f"   LLM Rationale:     {cand['match_reasoning']}\n" + "-" * 70)


def main():
    parser = argparse.ArgumentParser(description="RAG-Based Resume Profile Matching System")
    parser.add_argument("--jd", type=str, help="Job Description raw text string")
    parser.add_argument("--jd_file", type=str, help="Path to Job Description text file")
    parser.add_argument("--top_k", type=int, default=10, help="Number of top candidates to return (default: 10)")
    parser.add_argument("--output", type=str, help="Output JSON file path (e.g. 'results.json')")

    args = parser.parse_args()

    jd_input = None
    if args.jd_file:
        jd_input = args.jd_file
    elif args.jd:
        jd_input = args.jd
    else:
        # Default sample JD if no arguments provided
        jd_input = """
        Job Title: Senior AI & LLM Systems Engineer
        Required Experience: Minimum 5+ years of experience.
        Required Skills: Python, LangChain, FastAPI, Vector Databases.
        Preferred Skills: Docker, Kubernetes, AWS, Pinecone.

        Responsibilities:
        Architect and deploy production LLM applications using RAG retrieval, vector search, and tool calling.
        """
        print("[INFO] No JD input specified. Running default Senior AI Systems Engineer JD evaluation...")

    report = run_profile_matcher(jd_input, top_k=args.top_k, output_json_path=args.output)
    print_cli_report(report)


if __name__ == "__main__":
    main()
