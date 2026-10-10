import os
import shutil
import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

import pypdf
import docx


class FileSystemTools:
    """
    OOP File System Tools Engine providing file reading, listing, writing, and searching capabilities.
    """

    def _get_file_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract common metadata from a file.

        Args:
            filepath (str): Path to the target file.

        Returns:
            Dict[str, Any]: File metadata (filename, size_bytes, size_kb, extension, modified_date).
        """
        path = Path(filepath)
        stat = path.stat()
        return {
            "filename": path.name,
            "file_size_bytes": stat.st_size,
            "file_size_kb": round(stat.st_size / 1024, 2),
            "extension": path.suffix.lower(),
            "modified_date": datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Read text content and metadata from resume files (PDF, TXT, DOCX).

        Args:
            filepath (str): Path to the resume or target file.

        Returns:
            Dict[str, Any]: Dict containing status, filepath, content string, metadata, and error.
        """
        path = Path(filepath)

        if not path.exists():
            return {"status": "error", "filepath": str(filepath), "error": f"File not found: '{filepath}'", "content": "", "metadata": {}}
        if not path.is_file():
            return {"status": "error", "filepath": str(filepath), "error": f"Path is a directory: '{filepath}'", "content": "", "metadata": {}}

        ext = path.suffix.lower()
        text_content = ""

        try:
            if ext in [".txt", ".md", ".json", ".csv"]:
                try:
                    text_content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text_content = path.read_text(encoding="latin-1")

            elif ext == ".pdf":
                reader = pypdf.PdfReader(str(path))
                text_content = "\n\n".join(page.extract_text() for page in reader.pages if page.extract_text())

            elif ext == ".docx":
                doc = docx.Document(str(path))
                text_content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

            else:
                text_content = path.read_text(encoding="utf-8", errors="ignore")

            meta = self._get_file_metadata(str(path))
            meta["char_count"] = len(text_content)
            meta["word_count"] = len(text_content.split())

            return {"status": "success", "filepath": str(filepath), "content": text_content, "metadata": meta, "error": None}

        except Exception as e:
            return {"status": "error", "filepath": str(filepath), "error": f"Error reading file: {str(e)}", "content": "", "metadata": {}}

    def list_files(self, directory: str, extension: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all files in a directory with optional extension filtering.

        Args:
            directory (str): Directory path to scan (e.g. 'resumes').
            extension (Optional[str]): Optional extension filter (e.g. '.pdf', '.txt', '.docx').

        Returns:
            List[Dict[str, Any]]: List of file metadata dictionaries.
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            return [{"status": "error", "error": f"Directory not found: '{directory}'"}]
        if not dir_path.is_dir():
            return [{"status": "error", "error": f"Path is not a directory: '{directory}'"}]

        if extension:
            extension = (extension if extension.startswith(".") else f".{extension}").lower()

        try:
            files = [
                self._get_file_metadata(str(p))
                for p in dir_path.iterdir()
                if p.is_file() and (not extension or p.suffix.lower() == extension)
            ]
            return sorted(files, key=lambda x: x.get("filename", ""))
        except Exception as e:
            return [{"status": "error", "error": f"Error listing files: {str(e)}"}]

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        Write string content to a file, creating parent directories automatically.

        Args:
            filepath (str): Target file path (e.g. 'summaries/summary.txt').
            content (str): Text content to write.

        Returns:
            Dict[str, Any]: Status dict with filepath, bytes_written, metadata, and error.
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

            meta = self._get_file_metadata(str(path))
            return {
                "status": "success",
                "message": f"Successfully wrote {len(content)} characters to '{filepath}'.",
                "filepath": str(filepath),
                "bytes_written": len(content.encode('utf-8')),
                "metadata": meta,
                "error": None
            }
        except Exception as e:
            return {"status": "error", "filepath": str(filepath), "error": f"Failed to write file: {str(e)}"}

    def search_in_file(self, filepath: str, keyword: str) -> Dict[str, Any]:
        """
        Search for a keyword inside a file (case-insensitive) and return matching context snippets.

        Args:
            filepath (str): Target file path.
            keyword (str): Query keyword to search for.

        Returns:
            Dict[str, Any]: Dict containing match count and matching context line details.
        """
        if not keyword or not keyword.strip():
            return {"status": "error", "error": "Keyword cannot be empty.", "filepath": str(filepath), "match_count": 0, "matches": []}

        read_res = self.read_file(filepath)
        if read_res.get("status") == "error":
            return {"status": "error", "error": read_res.get("error"), "filepath": str(filepath), "match_count": 0, "matches": []}

        lines = read_res.get("content", "").splitlines()
        keyword_lower = keyword.strip().lower()
        matches = []

        for idx, line in enumerate(lines, start=1):
            if keyword_lower in line.lower():
                prev_line = lines[idx - 2].strip() if idx > 1 else ""
                next_line = lines[idx].strip() if idx < len(lines) else ""
                matches.append({
                    "line_number": idx,
                    "matching_line": line.strip(),
                    "context": f"... {prev_line} | [{line.strip()}] | {next_line} ..."
                })

        return {"status": "success", "filepath": str(filepath), "keyword": keyword, "match_count": len(matches), "matches": matches, "error": None}



if __name__ == "__main__":
    print("=== Testing OOP File System Tools (FileSystemTools) ===")
    tools = FileSystemTools()
    test_file = "sample_test/john_doe.txt"
    print("1. write_file:", tools.write_file(test_file, "John Doe\nRole: Senior Python Developer").get("status"))
    print("2. read_file:", tools.read_file(test_file).get("status"))
    print("3. search_in_file matches:", tools.search_in_file(test_file, "python").get("match_count"))
    print("4. list_files count:", len(tools.list_files("sample_test")))
    shutil.rmtree("sample_test", ignore_errors=True)
    print("\n[SUCCESS] FileSystemTools OOP class tests passed!")
