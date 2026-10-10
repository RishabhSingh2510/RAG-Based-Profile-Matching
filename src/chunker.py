"""
chunker.py - Section-Aware Structural Resume Chunking Engine
-------------------------------------------------------------
This module parses multi-format resumes (.pdf, .docx, .txt) extracted via fs_tools.py
into section-aware chunks (Professional Summary, Technical Skills, Work Experience,
Education, Projects) preserving semantic boundaries and metadata.
"""

import re
import os
import hashlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional

from fs_tools import FileSystemTools


@dataclass
class ResumeChunk:
    """Dataclass representing a structured resume section chunk."""
    chunk_id: str             # Unique chunk identifier (e.g. 'cand_alice_johnson_exp_01')
    candidate_id: str         # Candidate identifier (e.g. 'cand_alice_johnson')
    candidate_name: str       # Candidate full name (e.g. 'Alice Johnson')
    resume_path: str          # Relative/Absolute path to resume file
    section_type: str         # Section category ('Professional Summary', 'Technical Skills', 'Work Experience', 'Education', 'Projects')
    experience_years: float   # Calculated/Extracted total experience years
    skills_list: List[str]    # Extracted technical skills list
    text: str                 # Complete chunk text formatted with prepended provenance metadata

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SectionAwareChunker:
    """
    Section-Aware Structural Resume Chunker Engine.
    Splits resumes into logical semantic sections rather than naive character lengths.
    """

    SECTION_PATTERNS = {
        "Professional Summary": r"(?i)^(professional\s+summary|summary|about\s+me|profile|executive\s+summary|objective)[\s:]*$",
        "Technical Skills": r"(?i)^(technical\s+skills|skills|core\s+competencies|technical\s+expertise|technologies|tools)[\s:]*$",
        "Work Experience": r"(?i)^(work\s+experience|professional\s+experience|experience|employment\s+history|career\s+history)[\s:]*$",
        "Education": r"(?i)^(education(\s+&\s+certifications)?|academic\s+background|certifications|degrees|education\s+and\s+training)[\s:]*$",
        "Projects": r"(?i)^(projects|key\s+projects|selected\s+projects|personal\s+projects)[\s:]*$"
    }

    # Known common technical skills for metadata extraction fallback with canonical casing
    SKILL_CASING_MAP = {
        "python": "Python", "java": "Java", "c++": "C++", "c#": "C#", "r": "R", "sql": "SQL", "julia": "Julia",
        "javascript": "JavaScript", "typescript": "TypeScript", "go": "Go", "rust": "Rust", "php": "PHP",
        "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "Scikit-Learn", "keras": "Keras",
        "spacy": "SpaCy", "huggingface": "HuggingFace", "transformers": "Transformers", "xgboost": "XGBoost",
        "pandas": "Pandas", "numpy": "NumPy", "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
        "react": "React", "node.js": "Node.js", "next.js": "Next.js", "docker": "Docker", "kubernetes": "Kubernetes",
        "aws": "AWS", "azure": "Azure", "gcp": "GCP", "langchain": "LangChain", "llama-index": "LlamaIndex",
        "chromadb": "ChromaDB", "pinecone": "Pinecone", "qdrant": "Qdrant", "weaviate": "Weaviate",
        "faiss": "FAISS", "rag": "RAG", "llm": "LLM", "bert": "BERT", "spark": "Spark", "hadoop": "Hadoop",
        "snowflake": "Snowflake", "airflow": "Airflow", "kafka": "Kafka", "tableau": "Tableau",
        "power bi": "Power BI", "postgresql": "PostgreSQL", "mongodb": "MongoDB", "redis": "Redis",
        "linux": "Linux", "bash": "Bash", "git": "Git", "ci/cd": "CI/CD", "terraform": "Terraform",
        "ansible": "Ansible", "jenkins": "Jenkins", "graphql": "GraphQL", "rest api": "REST API", "opencv": "OpenCV"
    }

    def __init__(self, fs_engine: Optional[FileSystemTools] = None, max_chunk_chars: int = 1800, overlap_chars: int = 200):
        self.fs_tools = fs_engine or FileSystemTools()
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars


    def extract_candidate_name(self, text: str, filepath: str) -> str:
        """Extracts candidate name from document top lines or filename."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            first_line = lines[0]
            # Check if first line contains name before separator like '-' or '|'
            name_part = re.split(r"[-|=:]", first_line)[0].strip()
            # If name part is reasonable length (2 to 4 words, no numbers)
            if 2 <= len(name_part.split()) <= 5 and not any(char.isdigit() for char in name_part):
                return name_part

        # Fallback to filename cleanup: e.g. "resume_john_doe.pdf" -> "John Doe"
        base_name = Path(filepath).stem
        cleaned = re.sub(r"(?i)^(resume_|cv_)", "", base_name)
        cleaned = cleaned.replace("_", " ").replace("-", " ")
        return cleaned.title()

    def generate_candidate_id(self, candidate_name: str, filepath: str) -> str:
        """Generates a consistent slug-based candidate ID."""
        slug = re.sub(r"[^\w\s]", "", candidate_name.lower()).replace(" ", "_")
        if not slug:
            slug = Path(filepath).stem.lower()
        return f"cand_{slug}"

    def extract_experience_years(self, text: str) -> float:
        """Calculates total experience years from explicit text statements or date ranges."""
        # Check for explicit experience statements (e.g. "5+ years", "7 years experience")
        exp_match = re.search(r"(?i)(\d+)\+?\s*years?(?:\s+of)?\s+experience", text)
        if exp_match:
            return float(exp_match.group(1))

        exp_match2 = re.search(r"(?i)experience[:\s]+(\d+)\+?\s*years?", text)
        if exp_match2:
            return float(exp_match2.group(1))

        # Check date ranges (e.g. 2018 - 2024 or 2019 - Present)
        current_year = 2026
        date_matches = re.findall(r"\b(20\d{2}|19\d{2})\s*[-–—\s\to]+\s*(20\d{2}|19\d{2}|[Pp]resent|[Cc]urrent)\b", text)
        
        total_years = 0.0
        for start_str, end_str in date_matches:
            try:
                start_yr = int(start_str)
                if end_str.lower() in ["present", "current"]:
                    end_yr = current_year
                else:
                    end_yr = int(end_str)
                diff = end_yr - start_yr
                if 0 < diff <= 40:
                    total_years += diff
            except ValueError:
                continue

        return round(total_years, 1) if total_years > 0 else 0.0

    def extract_skills(self, text: str) -> List[str]:
        """Extracts technical skills list from document text."""
        found_skills = set()
        text_lower = text.lower()

        # Match known common skills using canonical casing lookup
        for skill_key, canonical_name in self.SKILL_CASING_MAP.items():
            pattern = r"\b" + re.escape(skill_key) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.add(canonical_name)

        return sorted(list(found_skills))


    def parse_sections(self, text: str) -> List[Dict[str, str]]:
        """Parses document text into structural section blocks."""
        lines = text.splitlines()
        sections: List[Dict[str, str]] = []
        
        current_section = "Professional Summary"
        current_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_lines.append(line)
                continue

            # Check if line matches a section header
            matched_section = None
            # Strip trailing punctuation like ':' or '='
            clean_header = re.sub(r"[:=]+\s*$", "", stripped)
            
            for section_name, pattern in self.SECTION_PATTERNS.items():
                if re.match(pattern, clean_header):
                    matched_section = section_name
                    break

            if matched_section:
                # Save previous section if it has non-empty lines
                content_block = "\n".join(current_lines).strip()
                if content_block:
                    sections.append({
                        "section_type": current_section,
                        "text": content_block
                    })
                current_section = matched_section
                current_lines = []
            else:
                current_lines.append(line)

        # Append final section
        final_block = "\n".join(current_lines).strip()
        if final_block:
            sections.append({
                "section_type": current_section,
                "text": final_block
            })

        return sections

    def _split_large_section(self, text: str, max_chars: int, overlap_chars: int) -> List[str]:
        """Sub-chunks large sections using double-newlines/bullets with sliding window overlap."""
        if len(text) <= max_chars:
            return [text]

        sub_chunks = []
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) + 2 <= max_chars:
                current_chunk = (current_chunk + "\n\n" + p).strip()
            else:
                if current_chunk:
                    sub_chunks.append(current_chunk)
                # Apply sliding window overlap
                overlap = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                current_chunk = (overlap + "\n\n" + p).strip()

        if current_chunk:
            sub_chunks.append(current_chunk)

        return sub_chunks if sub_chunks else [text]

    def chunk_document(self, filepath: str) -> List[ResumeChunk]:
        """
        Parses a resume file and generates section-aware chunks with prepended metadata.

        Args:
            filepath (str): Target resume file path.

        Returns:
            List[ResumeChunk]: List of structured ResumeChunk objects.
        """
        read_res = self.fs_tools.read_file(filepath)
        if read_res.get("status") == "error":
            print(f"[WARN] Could not read file for chunking: '{filepath}' ({read_res.get('error')})")
            return []

        text = read_res.get("content", "")
        if not text.strip():
            return []

        candidate_name = self.extract_candidate_name(text, filepath)
        candidate_id = self.generate_candidate_id(candidate_name, filepath)
        exp_years = self.extract_experience_years(text)
        overall_skills = self.extract_skills(text)

        parsed_sections = self.parse_sections(text)
        chunks: List[ResumeChunk] = []

        chunk_counter = 1
        for sec in parsed_sections:
            sec_type = sec["section_type"]
            sec_text = sec["text"]

            # Sub-chunk if section text exceeds max length
            sub_texts = self._split_large_section(sec_text, self.max_chunk_chars, self.overlap_chars)

            for sub_idx, sub_text in enumerate(sub_texts, start=1):
                chunk_id = f"{candidate_id}_{sec_type.lower().replace(' ', '_')}_{chunk_counter:02d}"
                chunk_counter += 1

                # Extract section-specific skills
                sec_skills = self.extract_skills(sub_text)
                combined_skills = sorted(list(set(sec_skills + overall_skills)))

                # Prepend contextual provenance header
                formatted_text = (
                    f"[Candidate: {candidate_name} | Section: {sec_type} | Exp: {exp_years} yrs]\n"
                    f"{sub_text}"
                )

                chunks.append(ResumeChunk(
                    chunk_id=chunk_id,
                    candidate_id=candidate_id,
                    candidate_name=candidate_name,
                    resume_path=str(filepath),
                    section_type=sec_type,
                    experience_years=exp_years,
                    skills_list=combined_skills,
                    text=formatted_text
                ))

        return chunks

    def chunk_directory(self, directory: str) -> List[ResumeChunk]:
        """
        Chunks all resume files in a target directory (.pdf, .docx, .txt).

        Args:
            directory (str): Directory containing resume files.

        Returns:
            List[ResumeChunk]: Aggregate list of chunks across all resumes.
        """
        file_metas = self.fs_tools.list_files(directory)
        all_chunks = []

        for meta in file_metas:
            filename = meta.get("filename")
            if not filename or meta.get("status") == "error":
                continue
            ext = Path(filename).suffix.lower()
            if ext in [".pdf", ".docx", ".txt"]:
                filepath = os.path.join(directory, filename)
                res_chunks = self.chunk_document(filepath)
                all_chunks.extend(res_chunks)

        return all_chunks


if __name__ == "__main__":
    print("=== Testing SectionAwareChunker Engine ===")
    chunker = SectionAwareChunker()
    sample_file = "resumes/resume_alice_johnson.txt"
    
    if os.path.exists(sample_file):
        chunks = chunker.chunk_document(sample_file)
        print(f"Generated {len(chunks)} chunks for '{sample_file}':\n")
        for chunk in chunks:
            print(f"[{chunk.chunk_id}] {chunk.section_type} (Exp: {chunk.experience_years} yrs)")
            print(f"Skills: {chunk.skills_list[:5]}")
            print(f"Text Snippet: {chunk.text[:150]}...\n" + "-"*50)
    else:
        print(f"Sample file '{sample_file}' not found.")
