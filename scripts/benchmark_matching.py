"""
benchmark_matching.py - Comprehensive Benchmark & Evaluation Script across 10 JDs and 50 Resumes

Runs profile matching across all 10 diverse Job Descriptions in `./job_descriptions/`
against the pool of 50 candidate resumes indexed in Pinecone.
Generates performance metrics, candidate match rankings, hard constraint pass/fail statistics,
and exports a structured benchmark evaluation report into `scratch/benchmark_results.json`.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from matcher import ProfileMatcher
from logger import SessionLogger

JDS_DIR = Path("job_descriptions")
SCRATCH_DIR = Path("scratch")


def run_benchmark(top_k: int = 5, output_file: str = "scratch/benchmark_results.json") -> Dict[str, Any]:
    print("=" * 75)
    print("      RAG Profile Matcher - Multi-JD System Performance Benchmark")
    print("=" * 75)

    if not JDS_DIR.exists():
        print(f"[ERROR] Job descriptions directory '{JDS_DIR}' does not exist.")
        sys.exit(1)

    jd_files = sorted(list(JDS_DIR.glob("*.txt")))
    print(f"[INFO] Found {len(jd_files)} Job Description files in '{JDS_DIR}'.")
    print(f"[INFO] Running evaluation against 50 indexed candidates in Pinecone...\n")

    matcher = ProfileMatcher()
    benchmark_results: List[Dict[str, Any]] = []

    start_total_time = time.time()

    for idx, jd_path in enumerate(jd_files, 1):
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        jd_name = jd_path.name
        print(f"[{idx}/{len(jd_files)}] Evaluating JD: {jd_name}...")
        
        t0 = time.time()
        match_report = matcher.match_candidates(jd_text, top_k_candidates=top_k)
        elapsed = round(time.time() - t0, 2)

        jd_summary = match_report["job_description_summary"]
        top_matches = match_report["top_matches"]

        # Collect top candidate names & scores
        top_cands_summary = [
            {
                "rank": m["rank"],
                "candidate_name": m["candidate_name"],
                "resume_path": m["resume_path"],
                "match_score": m["match_score"],
                "passed_mandatory_filters": m["passed_mandatory_filters"],
                "matched_must_have": m["matched_skills"]["must_have"],
                "missing_skills": m["missing_skills"]
            }
            for m in top_matches
        ]

        result_item = {
            "jd_filename": jd_name,
            "jd_title": jd_summary["title"],
            "min_experience_years": jd_summary["min_experience_years"],
            "required_skills": jd_summary["required_skills"],
            "total_candidates_evaluated": match_report["total_candidates_evaluated"],
            "candidates_passed_filters": match_report["candidates_passed_filters"],
            "candidates_failed_filters": match_report["candidates_failed_filters"],
            "execution_time_seconds": elapsed,
            "top_candidate_name": top_cands_summary[0]["candidate_name"] if top_cands_summary else None,
            "top_candidate_score": top_cands_summary[0]["match_score"] if top_cands_summary else 0,
            "top_matches": top_cands_summary
        }

        benchmark_results.append(result_item)
        print(f"      -> Title: '{jd_summary['title']}' | Top Match: {result_item['top_candidate_name']} ({result_item['top_candidate_score']}/100) | Filter Passed: {result_item['candidates_passed_filters']}/{result_item['total_candidates_evaluated']} in {elapsed}s")

    total_elapsed = round(time.time() - start_total_time, 2)

    summary_report = {
        "total_jds_evaluated": len(jd_files),
        "total_candidates_pool": 50,
        "total_benchmark_time_seconds": total_elapsed,
        "average_jd_eval_time_seconds": round(total_elapsed / len(jd_files), 2),
        "evaluations": benchmark_results
    }

    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    print("\n" + "=" * 75)
    print("                     BENCHMARK SUMMARY RESULTS")
    print("=" * 75)
    print(f"Total JDs Tested:            {len(jd_files)}")
    print(f"Candidate Pool Size:         50 candidates")
    print(f"Total Processing Time:       {total_elapsed} seconds")
    print(f"Avg Time Per JD Match:       {summary_report['average_jd_eval_time_seconds']} seconds")
    print(f"Benchmark Report Saved To:   {output_file}")
    print("=" * 75)

    return summary_report


if __name__ == "__main__":
    run_benchmark()
