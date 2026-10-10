"""
test_suite.py - Consolidated End-to-End & Unit Test Suite for Profile Matcher System
-------------------------------------------------------------------------------------
Consolidates all system unit, integration, RAG accuracy, and tool tests into a single
runnable test file covering:
1. Environment & Pinecone initialization setup
2. SectionAwareChunker multi-format resume parsing
3. GeminiEmbedder 768-dim embeddings & Pinecone payload formatting
4. HybridRetriever sparse keyword density & vector retrieval
5. ProfileMatcher hard filter constraint evaluation & 0-100 quantitative scoring
6. ProfileMatcher CLI application & JSON schema compliance
7. Multi-domain RAG retrieval accuracy benchmark
8. File system tools & LLM assistant dispatcher functionality
"""

import os
import json
import unittest
import pytest
from pathlib import Path

from init_pinecone import get_pinecone_client, initialize_pinecone_index
from chunker import SectionAwareChunker, ResumeChunk
from vector_store import GeminiEmbedder, PineconeVectorStore
from retriever import HybridRetriever, JobDescriptionParsed, CandidateHit
from matcher import ProfileMatcher, EvaluatedCandidate
from profile_matcher import run_profile_matcher
import fs_tools
import llm_file_assistant


# =============================================================================
# 1. Environment & Setup Verification
# =============================================================================

def test_requirements_file_exists():
    assert os.path.exists("requirements.txt")
    with open("requirements.txt", "r") as f:
        content = f.read()
        assert "pinecone" in content
        assert "google-genai" in content


def test_env_example_exists():
    assert os.path.exists(".env.example")
    with open(".env.example", "r") as f:
        content = f.read()
        assert "PINECONE_API_KEY" in content
        assert "PINECONE_INDEX_NAME" in content


def test_pinecone_placeholder_detection():
    client, spec = get_pinecone_client()
    if os.getenv("PINECONE_API_KEY") in ["your_pinecone_api_key_here", "", None]:
        assert client is None


# =============================================================================
# 2. Section-Aware Chunker Tests
# =============================================================================

@pytest.fixture
def chunker():
    return SectionAwareChunker()


def test_single_txt_resume_chunking(chunker):
    filepath = "resumes/resume_alice_johnson.txt"
    assert os.path.exists(filepath), f"File not found: {filepath}"

    chunks = chunker.chunk_document(filepath)
    assert len(chunks) > 0, "No chunks generated for sample TXT resume"

    for chunk in chunks:
        assert isinstance(chunk, ResumeChunk)
        assert chunk.candidate_name == "Alice Johnson"
        assert chunk.candidate_id == "cand_alice_johnson"
        assert chunk.experience_years == 5.0
        assert chunk.resume_path == filepath
        assert len(chunk.skills_list) > 0
        assert "[Candidate: Alice Johnson" in chunk.text


def test_single_pdf_resume_chunking(chunker):
    filepath = "resumes/resume_john_doe.pdf"
    assert os.path.exists(filepath), f"File not found: {filepath}"

    chunks = chunker.chunk_document(filepath)
    assert len(chunks) > 0, "No chunks generated for sample PDF resume"

    first_chunk = chunks[0]
    assert "John Doe" in first_chunk.candidate_name
    assert first_chunk.candidate_id.startswith("cand_")
    assert first_chunk.experience_years > 0.0
    assert len(first_chunk.skills_list) > 0


def test_single_docx_resume_chunking(chunker):
    filepath = "resumes/resume_jane_smith.docx"
    assert os.path.exists(filepath), f"File not found: {filepath}"

    chunks = chunker.chunk_document(filepath)
    assert len(chunks) > 0, "No chunks generated for sample DOCX resume"

    first_chunk = chunks[0]
    assert "Jane Smith" in first_chunk.candidate_name
    assert first_chunk.candidate_id.startswith("cand_")
    assert len(first_chunk.skills_list) > 0


def test_all_resumes_chunking(chunker):
    resumes_dir = "resumes"
    assert os.path.exists(resumes_dir), f"Directory not found: {resumes_dir}"

    all_chunks = chunker.chunk_directory(resumes_dir)
    assert len(all_chunks) > 0, "No chunks generated for resumes directory"

    unique_candidates = {c.candidate_id for c in all_chunks}
    assert len(unique_candidates) >= 50, f"Expected at least 50 unique candidates, found {len(unique_candidates)}"

    section_types = {c.section_type for c in all_chunks}
    assert "Work Experience" in section_types or "Professional Summary" in section_types


def test_experience_years_extraction(chunker):
    text1 = "Senior Software Engineer with 7+ years of experience in Python."
    assert chunker.extract_experience_years(text1) == 7.0

    text2 = "Experience: 10 years building cloud architectures."
    assert chunker.extract_experience_years(text2) == 10.0

    text3 = "Senior Developer (2018 - 2024)"
    assert chunker.extract_experience_years(text3) == 6.0


def test_skill_extraction(chunker):
    text = "Proficient in Python, PyTorch, SQL, Docker, Kubernetes, AWS, and FastAPI."
    skills = chunker.extract_skills(text)
    assert "Python" in skills
    assert "PyTorch" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "AWS" in skills
    assert "FastAPI" in skills


# =============================================================================
# 3. Vector Embedder & Vector Store Tests
# =============================================================================

def test_embedder_dimension():
    embedder = GeminiEmbedder()
    vec = embedder.embed_text("Senior AI Engineer with Python and Pinecone experience.")
    assert isinstance(vec, list)
    assert len(vec) == 768, f"Expected 768-dim vector, got {len(vec)}"
    assert all(isinstance(val, float) for val in vec)


def test_embedder_batch():
    embedder = GeminiEmbedder()
    texts = [
        "Data Scientist with PyTorch experience.",
        "DevOps Engineer with Kubernetes and AWS experience."
    ]
    vectors = embedder.embed_batch(texts, batch_size=2)
    assert len(vectors) == 2
    assert len(vectors[0]) == 768
    assert len(vectors[1]) == 768


def test_vector_store_payload_structure():
    store = PineconeVectorStore()
    embedder = GeminiEmbedder()
    
    sample_chunk = ResumeChunk(
        chunk_id="cand_test_01_exp_01",
        candidate_id="cand_test_01",
        candidate_name="Test Candidate",
        resume_path="resumes/resume_john_doe.pdf",
        section_type="Work Experience",
        experience_years=5.0,
        skills_list=["Python", "FastAPI", "Pinecone"],
        text="[Candidate: Test Candidate | Section: Work Experience | Exp: 5.0 yrs]\nSenior Software Engineer"
    )

    res = store.upsert_chunks([sample_chunk], embedder)
    assert "status" in res
    assert "upserted_count" in res


# =============================================================================
# 4. Hybrid Retriever Tests
# =============================================================================

@pytest.fixture
def retriever():
    return HybridRetriever()


def test_parse_job_description(retriever):
    sample_jd = """
    Job Title: Senior Cloud DevOps Engineer
    Required Experience: Minimum 5+ years of experience.
    Required Skills: Python, Docker, Kubernetes, AWS, Terraform.
    Preferred Skills: CI/CD, Jenkins, Linux.
    """

    parsed = retriever.parse_job_description(sample_jd)
    assert isinstance(parsed, JobDescriptionParsed)
    assert parsed.min_experience_years == 5.0
    assert len(parsed.required_skills) > 0
    assert "Docker" in parsed.required_skills or "Kubernetes" in parsed.required_skills
    assert len(parsed.embedding_vector) == 768


def test_sparse_keyword_score_computation(retriever):
    chunk_text = "Experienced with Python, Docker, Kubernetes, and AWS cloud deployments."
    chunk_skills = ["Python", "Docker", "Kubernetes", "AWS"]
    required_skills = ["Python", "Docker", "Kubernetes", "AWS", "Terraform"]

    score = retriever.compute_sparse_keyword_score(chunk_text, chunk_skills, required_skills)
    assert score == 0.8  # 4 matches out of 5 required = 0.8


def test_hybrid_retrieve_pipeline(retriever):
    sample_jd = """
    Job Title: Senior Data Scientist
    Required Experience: 3+ years experience.
    Required Skills: Python, PyTorch, SQL, Pandas.
    """

    res = retriever.hybrid_retrieve(sample_jd, top_k_chunks=15)
    assert res.get("status") == "success"
    assert "job_description" in res
    assert "candidate_hits" in res

    hits = res.get("candidate_hits", [])
    assert len(hits) > 0

    top_hit = hits[0]
    assert "candidate_id" in top_hit
    assert "hybrid_score" in top_hit
    assert "max_semantic_score" in top_hit
    assert "max_keyword_score" in top_hit
    assert top_hit["hybrid_score"] > 0.0


# =============================================================================
# 5. Profile Matcher Hard Filtering & Scoring Tests
# =============================================================================

@pytest.fixture
def matcher():
    return ProfileMatcher()


def test_hard_filter_pass(matcher):
    cand_exp = 7.0
    cand_skills = ["Python", "FastAPI", "LangChain", "Pinecone", "AWS"]
    min_exp_req = 5.0
    mandatory_skills = ["Python", "FastAPI", "LangChain"]

    passed, failures = matcher.evaluate_hard_filters(
        candidate_exp=cand_exp,
        candidate_skills=cand_skills,
        min_experience_req=min_exp_req,
        mandatory_skills=mandatory_skills
    )

    assert passed is True
    assert len(failures) == 0


def test_hard_filter_insufficient_exp(matcher):
    cand_exp = 3.0
    cand_skills = ["Python", "FastAPI", "LangChain"]
    min_exp_req = 5.0
    mandatory_skills = ["Python", "FastAPI"]

    passed, failures = matcher.evaluate_hard_filters(
        candidate_exp=cand_exp,
        candidate_skills=cand_skills,
        min_experience_req=min_exp_req,
        mandatory_skills=mandatory_skills
    )

    assert passed is False
    assert any("Insufficient Experience" in f for f in failures)


def test_hard_filter_missing_skill(matcher):
    cand_exp = 6.0
    cand_skills = ["Python", "FastAPI"]
    min_exp_req = 5.0
    mandatory_skills = ["Python", "FastAPI", "Kubernetes"]

    passed, failures = matcher.evaluate_hard_filters(
        candidate_exp=cand_exp,
        candidate_skills=cand_skills,
        min_experience_req=min_exp_req,
        mandatory_skills=mandatory_skills
    )

    assert passed is False
    assert any("Missing mandatory skill 'Kubernetes'" in f for f in failures)


def test_compute_match_score_range(matcher):
    score, details = matcher.compute_match_score(
        semantic_score=0.75,
        candidate_skills=["Python", "FastAPI", "LangChain", "Docker", "AWS"],
        required_skills=["Python", "FastAPI", "LangChain"],
        preferred_skills=["Docker", "AWS"],
        candidate_exp=7.0,
        min_exp_req=5.0
    )

    assert 0 <= score <= 100
    assert "matched_skills" in details
    assert len(details["matched_skills"]["must_have"]) == 3


def test_full_candidate_matching_pipeline(matcher):
    sample_jd = """
    Job Title: Senior AI & LLM Systems Engineer
    Required Experience: Minimum 5+ years of experience.
    Required Skills: Python, LangChain, FastAPI.
    Preferred Skills: Docker, AWS.
    """

    results = matcher.match_candidates(sample_jd, top_k_candidates=10)

    assert "job_description_summary" in results
    assert "total_candidates_evaluated" in results
    assert "top_matches" in results
    assert len(results["top_matches"]) > 0

    top_match = results["top_matches"][0]
    assert "rank" in top_match
    assert "match_score" in top_match
    assert "passed_mandatory_filters" in top_match
    assert "matched_skills" in top_match
    assert "relevant_excerpts" in top_match


# =============================================================================
# 6. Profile Matcher CLI & Output JSON Schema Tests
# =============================================================================

def test_run_profile_matcher_execution():
    sample_jd = """
    Job Title: Senior AI & LLM Systems Engineer
    Required Experience: Minimum 5+ years of experience.
    Required Skills: Python, LangChain, FastAPI.
    Preferred Skills: Docker, AWS, Pinecone.
    """
    
    output_file = "scratch/test_results.json"
    if os.path.exists(output_file):
        os.remove(output_file)

    report = run_profile_matcher(
        jd_input=sample_jd,
        top_k=5,
        output_json_path=output_file
    )

    assert isinstance(report, dict)
    assert "job_description_summary" in report
    assert "total_candidates_evaluated" in report
    assert "top_matches" in report
    assert len(report["top_matches"]) == 5

    top_match = report["top_matches"][0]
    assert "rank" in top_match
    assert "candidate_name" in top_match
    assert "resume_path" in top_match
    assert "match_score" in top_match
    assert "passed_mandatory_filters" in top_match
    assert "matched_skills" in top_match
    assert "missing_skills" in top_match
    assert "relevant_excerpts" in top_match
    assert "match_reasoning" in top_match
    assert len(top_match["match_reasoning"]) > 0

    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        loaded_json = json.load(f)
        assert loaded_json["total_candidates_evaluated"] == report["total_candidates_evaluated"]


# =============================================================================
# 7. Multi-Domain RAG Pipeline Accuracy Tests
# =============================================================================

TEST_JDS = [
    {
        "domain": "AI / LLM Engineering",
        "jd": """
        Job Title: Senior AI & LLM Engineer
        Required Experience: Minimum 5+ years of experience.
        Required Skills: Python, LangChain, FastAPI.
        Preferred Skills: Docker, Pinecone.
        """
    },
    {
        "domain": "Cloud & DevOps Architecture",
        "jd": """
        Job Title: Lead Cloud & DevOps Architect
        Required Experience: Minimum 7+ years of experience.
        Required Skills: Terraform, Kubernetes, Docker, AWS.
        Preferred Skills: Ansible, Python, Go.
        """
    },
    {
        "domain": "Data Engineering",
        "jd": """
        Job Title: Senior Data Engineer
        Required Experience: Minimum 4+ years of experience.
        Required Skills: Python, SQL, Spark, Snowflake.
        Preferred Skills: Airflow, Kafka.
        """
    },
    {
        "domain": "Cybersecurity",
        "jd": """
        Job Title: Cybersecurity & SOC Specialist
        Required Experience: Minimum 4+ years of experience.
        Required Skills: Python, Wireshark, Splunk, CISSP.
        Preferred Skills: Linux, Metasploit.
        """
    }
]


@pytest.mark.parametrize("jd_item", TEST_JDS)
def test_rag_pipeline_across_domains(jd_item):
    domain_name = jd_item["domain"]
    jd_text = jd_item["jd"]
    out_file = f"scratch/test_pipeline_{domain_name.replace(' ', '_').lower()}.json"

    report = run_profile_matcher(
        jd_input=jd_text,
        top_k=5,
        output_json_path=out_file
    )

    assert isinstance(report, dict)
    assert "job_description_summary" in report
    assert "total_candidates_evaluated" in report
    assert report["total_candidates_evaluated"] > 0
    assert "top_matches" in report
    assert len(report["top_matches"]) == 5

    for cand in report["top_matches"]:
        assert "rank" in cand
        assert "candidate_name" in cand
        assert "resume_path" in cand
        assert "match_score" in cand
        assert 0 <= cand["match_score"] <= 100
        assert "passed_mandatory_filters" in cand
        assert isinstance(cand["passed_mandatory_filters"], bool)
        assert "matched_skills" in cand
        assert "must_have" in cand["matched_skills"]
        assert "missing_skills" in cand
        assert "relevant_excerpts" in cand
        assert "match_reasoning" in cand
        assert len(cand["match_reasoning"]) > 0

    assert os.path.exists(out_file)


# =============================================================================
# 8. File System Tools & LLM Assistant Dispatcher Tests
# =============================================================================

class TestAssistantTools(unittest.TestCase):

    def setUp(self):
        self.resumes_dir = Path("resumes")
        self.tools = fs_tools.FileSystemTools()

    def test_01_list_resumes(self):
        files = self.tools.list_files(str(self.resumes_dir))
        self.assertIsInstance(files, list)
        self.assertGreaterEqual(len(files), 6)

    def test_02_read_pdf_resume(self):
        pdf_path = self.resumes_dir / "resume_john_doe.pdf"
        result = self.tools.read_file(str(pdf_path))
        self.assertEqual(result.get("status"), "success")
        self.assertIn("John Doe", result.get("content", ""))

    def test_03_read_docx_resume(self):
        docx_path = self.resumes_dir / "resume_jane_smith.docx"
        result = self.tools.read_file(str(docx_path))
        self.assertEqual(result.get("status"), "success")
        self.assertIn("Jane Smith", result.get("content", ""))

    def test_04_read_txt_resume(self):
        txt_path = self.resumes_dir / "resume_alice_johnson.txt"
        result = self.tools.read_file(str(txt_path))
        self.assertEqual(result.get("status"), "success")
        self.assertIn("Alice Johnson", result.get("content", ""))

    def test_05_search_keyword(self):
        pdf_path = self.resumes_dir / "resume_john_doe.pdf"
        result = self.tools.search_in_file(str(pdf_path), "Python")
        self.assertEqual(result.get("status"), "success")
        self.assertGreaterEqual(result.get("match_count", 0), 1)

    def test_06_tool_dispatcher(self):
        assistant = llm_file_assistant.LLMFileAssistant()
        res = assistant.execute_tool_call(
            "search_in_file",
            {"filepath": str(self.resumes_dir / "resume_john_doe.pdf"), "keyword": "Python"}
        )
        self.assertEqual(res.get("status"), "success")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
