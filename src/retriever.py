"""
retriever.py - Hybrid Retrieval Engine (Dense Vector + Sparse Keyword Search)
-----------------------------------------------------------------------------
This module implements the Layer 3 Hybrid Retrieval Engine. It computes Cosine Similarity
search in Pinecone via Gemini 768-dim embeddings, merges sparse keyword match density,
and aggregates chunk hits by candidate_id using Reciprocal Rank Fusion (RRF).
"""

import os
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

from chunker import SectionAwareChunker
from vector_store import GeminiEmbedder, PineconeVectorStore


@dataclass
class JobDescriptionParsed:
    """Dataclass holding structured parameters extracted from a Job Description."""
    raw_text: str
    title: str
    min_experience_years: float
    required_skills: List[str]
    preferred_skills: List[str]
    embedding_vector: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("embedding_vector", None)  # Exclude raw 768-dim vector from JSON dict
        return d


@dataclass
class CandidateHit:
    """Dataclass representing an aggregated candidate hit from hybrid retrieval."""
    candidate_id: str
    candidate_name: str
    resume_path: str
    experience_years: float
    skills_list: List[str]
    max_semantic_score: float
    max_keyword_score: float
    hybrid_score: float
    top_chunks: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HybridRetriever:
    """
    Hybrid Retrieval Engine combining Pinecone Cosine Similarity (Dense)
    with exact keyword skill matching (Sparse) using RRF scoring.
    """

    def __init__(
        self,
        embedder: Optional[GeminiEmbedder] = None,
        vector_store: Optional[PineconeVectorStore] = None,
        chunker: Optional[SectionAwareChunker] = None,
        alpha: float = 0.7
    ):
        self.embedder = embedder or GeminiEmbedder()
        self.vector_store = vector_store or PineconeVectorStore()
        self.chunker = chunker or SectionAwareChunker()
        self.alpha = alpha  # Weight factor: 0.7 for Semantic, 0.3 for Keyword

    def parse_job_description(self, jd_input: str) -> JobDescriptionParsed:
        """
        Parses raw JD text or file path to extract title, min experience years, required skills, and embedding vector.

        Args:
            jd_input (str): JD raw text content or file path.

        Returns:
            JobDescriptionParsed: Parsed JD object.
        """
        raw_text = jd_input.strip()
        if os.path.exists(jd_input) and os.path.isfile(jd_input):
            try:
                with open(jd_input, "r", encoding="utf-8") as f:
                    raw_text = f.read().strip()
            except Exception as e:
                print(f"[WARN] Failed to read JD file '{jd_input}': {e}")

        # Extract Title
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        title = "Job Position"
        for line in lines[:5]:
            if re.search(r"(?i)^(title|position|role)[:\s]+", line):
                title = re.sub(r"(?i)^(title|position|role)[:\s]+", "", line).strip()
                break
            elif len(line.split()) <= 6 and not any(char.isdigit() for char in line):
                title = line
                break

        # Extract Minimum Experience Years
        min_exp = 0.0
        exp_match = re.search(r"(?i)(\d+)\+?\s*years?(?:\s+of)?\s+experience", raw_text)
        if exp_match:
            min_exp = float(exp_match.group(1))
        else:
            exp_match2 = re.search(r"(?i)(?:minimum|min|at\s+least)\s+(\d+)\+?\s*years?", raw_text)
            if exp_match2:
                min_exp = float(exp_match2.group(1))

        # Extract Skills using SectionAwareChunker skills map
        all_skills = self.chunker.extract_skills(raw_text)

        # Separate required vs preferred skills if explicit headers exist
        required_skills = []
        preferred_skills = []

        req_block = re.search(r"(?i)(?:required\s+skills|must\s+have|requirements)[:\s]+(.*?)(?=\n\n|\n[A-Z\s]+:|$)", raw_text, re.DOTALL)
        pref_block = re.search(r"(?i)(?:preferred\s+skills|nice\s+to\s+have|plus)[:\s]+(.*?)(?=\n\n|\n[A-Z\s]+:|$)", raw_text, re.DOTALL)

        if req_block:
            required_skills = self.chunker.extract_skills(req_block.group(1))
        if pref_block:
            preferred_skills = self.chunker.extract_skills(pref_block.group(1))

        # Fallback if no specific section blocks found
        if not required_skills:
            required_skills = all_skills
            preferred_skills = []

        # Compute query vector (768-dim)
        embedding_vec = self.embedder.embed_text(raw_text)

        return JobDescriptionParsed(
            raw_text=raw_text,
            title=title,
            min_experience_years=min_exp,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            embedding_vector=embedding_vec
        )

    def compute_sparse_keyword_score(self, chunk_text: str, chunk_skills: List[str], required_skills: List[str]) -> float:
        """
        Computes sparse keyword match density score (0.0 to 1.0) for a chunk.

        Args:
            chunk_text (str): Chunk text content.
            chunk_skills (List[str]): List of skills associated with chunk.
            required_skills (List[str]): List of required JD skills.

        Returns:
            float: Sparse keyword match ratio.
        """
        if not required_skills:
            return 1.0

        matches = 0
        chunk_text_lower = chunk_text.lower()
        chunk_skills_lower = {s.lower() for s in chunk_skills}

        for skill in required_skills:
            skill_lower = skill.lower()
            pattern = r"\b" + re.escape(skill_lower) + r"\b"
            if skill_lower in chunk_skills_lower or re.search(pattern, chunk_text_lower):
                matches += 1

        return round(matches / len(required_skills), 4)

    def hybrid_retrieve(self, jd_input: str, top_k_chunks: int = 30) -> Dict[str, Any]:
        """
        Executes hybrid retrieval matching a JD against vector database and sparse keywords.

        Args:
            jd_input (str): Job Description text string or file path.
            top_k_chunks (int): Number of top vector chunk hits to retrieve from Pinecone.

        Returns:
            Dict[str, Any]: Retrieval summary dict with parsed JD and aggregated candidate hits.
        """
        # Step 1: Parse JD and embed vector
        parsed_jd = self.parse_job_description(jd_input)

        # Step 2: Query Pinecone Cosine Similarity (Dense Search)
        pinecone_matches = self.vector_store.query_similarity(
            query_vector=parsed_jd.embedding_vector,
            top_k=top_k_chunks
        )

        # Step 3: Compute Sparse & Hybrid Scores per chunk, aggregate by candidate_id
        candidate_map: Dict[str, Dict[str, Any]] = {}

        for match in pinecone_matches:
            chunk_id = match.get("id")
            meta = match.get("metadata", {})
            semantic_score = match.get("score", 0.0)

            cand_id = meta.get("candidate_id", "unknown")
            cand_name = meta.get("candidate_name", "Unknown Candidate")
            resume_path = meta.get("resume_path", "")
            exp_years = float(meta.get("experience_years", 0.0))
            chunk_skills = meta.get("skills", [])
            chunk_text = meta.get("chunk_text", "")
            sec_type = meta.get("section_type", "General")

            # Calculate sparse keyword score
            keyword_score = self.compute_sparse_keyword_score(chunk_text, chunk_skills, parsed_jd.required_skills)

            # Compute RRF hybrid score: alpha * semantic + (1 - alpha) * keyword
            hybrid_score = round(self.alpha * semantic_score + (1.0 - self.alpha) * keyword_score, 4)

            chunk_info = {
                "chunk_id": chunk_id,
                "section_type": sec_type,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "hybrid_score": hybrid_score,
                "chunk_text": chunk_text
            }

            if cand_id not in candidate_map:
                candidate_map[cand_id] = {
                    "candidate_id": cand_id,
                    "candidate_name": cand_name,
                    "resume_path": resume_path,
                    "experience_years": exp_years,
                    "skills_set": set(chunk_skills),
                    "max_semantic_score": semantic_score,
                    "max_keyword_score": keyword_score,
                    "hybrid_score": hybrid_score,
                    "chunks": [chunk_info]
                }
            else:
                cand = candidate_map[cand_id]
                cand["skills_set"].update(chunk_skills)
                cand["max_semantic_score"] = max(cand["max_semantic_score"], semantic_score)
                cand["max_keyword_score"] = max(cand["max_keyword_score"], keyword_score)
                # Aggregate candidate hybrid score via max-pooling across sections
                cand["hybrid_score"] = max(cand["hybrid_score"], hybrid_score)
                cand["chunks"].append(chunk_info)

        # Convert candidate map to sorted list of CandidateHit objects
        candidate_hits: List[CandidateHit] = []
        for cand_id, info in candidate_map.items():
            # Sort candidate chunks by highest hybrid score
            sorted_chunks = sorted(info["chunks"], key=lambda x: x["hybrid_score"], reverse=True)
            
            candidate_hits.append(CandidateHit(
                candidate_id=info["candidate_id"],
                candidate_name=info["candidate_name"],
                resume_path=info["resume_path"],
                experience_years=info["experience_years"],
                skills_list=sorted(list(info["skills_set"])),
                max_semantic_score=round(info["max_semantic_score"], 4),
                max_keyword_score=round(info["max_keyword_score"], 4),
                hybrid_score=round(info["hybrid_score"], 4),
                top_chunks=sorted_chunks[:3]  # Keep top 3 most relevant chunks per candidate
            ))

        # Sort candidate hits by highest overall hybrid score
        candidate_hits.sort(key=lambda x: x.hybrid_score, reverse=True)

        return {
            "status": "success",
            "job_description": parsed_jd.to_dict(),
            "total_chunks_retrieved": len(pinecone_matches),
            "unique_candidates_found": len(candidate_hits),
            "candidate_hits": [c.to_dict() for c in candidate_hits]
        }


if __name__ == "__main__":
    print("=== Testing HybridRetriever Engine ===")
    sample_jd = """
    Job Title: Senior AI & LLM Systems Engineer
    Required Experience: Minimum 5+ years of experience.
    Required Skills: Python, LangChain, Vector Databases, FastAPI, PyTorch.
    Preferred Skills: Docker, Kubernetes, AWS, Pinecone.

    Responsibilities:
    Architect and deploy production LLM applications using RAG retrieval, vector search, and tool calling.
    """
    
    retriever = HybridRetriever()
    result = retriever.hybrid_retrieve(sample_jd, top_k_chunks=20)
    
    print(f"\nParsed Job Title: {result['job_description']['title']}")
    print(f"Required Experience: {result['job_description']['min_experience_years']} yrs")
    print(f"Required Skills: {result['job_description']['required_skills']}")
    print(f"Candidates Retrieved: {result['unique_candidates_found']}\n")
    
    for rank, cand in enumerate(result['candidate_hits'][:5], start=1):
        print(f"#{rank} {cand['candidate_name']} (Hybrid Score: {cand['hybrid_score']}) | Exp: {cand['experience_years']} yrs")
        print(f"   Semantic: {cand['max_semantic_score']} | Keyword: {cand['max_keyword_score']}")
        print(f"   Top Skills: {cand['skills_list'][:6]}\n" + "-"*50)
