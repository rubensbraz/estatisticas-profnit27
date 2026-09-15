"""PDF Parsing module for PROFNIT preliminary result documents.

This module reads the PDF file containing candidate results, cleans page headers/footers,
and uses regular expressions to extract structured candidate records.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from typing import List, Optional, Union

import pypdf

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class CandidateRecord:
    """Represents a single candidate record extracted from the PDF.

    Attributes:
        name: Full name of the candidate (masked in source document).
        cpf: Masked CPF identifier (format: ***XXXXXX**).
        score: Raw score (number of correct answers, 0-20) or None if absent.
        is_present: Boolean flag indicating whether candidate was present.
    """

    name: str
    cpf: str
    score: Optional[int]
    is_present: bool


class PDFParser:
    """Parser for PROFNIT entrance exam result PDF documents."""

    def __init__(self, pdf_path: Union[str, Path]) -> None:
        """Initialize PDF parser with file path.

        Args:
            pdf_path: Path to the PDF file to be parsed.
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at path: {self.pdf_path}")

    def parse(self) -> List[CandidateRecord]:
        """Extract candidate records from PDF file.

        Returns:
            List of CandidateRecord objects extracted from the document.
        """
        logger.info("Starting PDF parsing for file: %s", self.pdf_path)
        reader = pypdf.PdfReader(str(self.pdf_path))
        records: List[CandidateRecord] = []

        # Regular expression for matching CPF and score/status at end of line
        # CPF pattern: ***XXXXXX** followed by numeric score or "AUSENTE"
        record_pattern = re.compile(r"(\*\*\*\d{6}\*\*)\s+(AUSENTE|\d+)\s*$")

        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            lines = text.split("\n")

            # Determine start of data table on page
            table_start_idx = 0
            for idx, line in enumerate(lines):
                if "NOME DO CANDIDATO" in line and "CPF" in line:
                    table_start_idx = idx + 1
                    break

            name_buffer = ""
            for line in lines[table_start_idx:]:
                line_str = line.strip()
                if not line_str:
                    continue

                # Skip header/footer artifacts
                if "Exame Nacional" in line_str or "Página" in line_str:
                    continue

                match = record_pattern.search(line_str)
                if match:
                    cpf = match.group(1)
                    status_or_score = match.group(2)
                    name_part = line_str[: match.start()].strip()

                    # Combine multiline candidate names
                    full_name = f"{name_buffer} {name_part}".strip()
                    full_name = re.sub(r"\s+", " ", full_name)

                    # Determine score and presence status
                    if status_or_score.upper() == "AUSENTE":
                        score = None
                        is_present = False
                    else:
                        score = int(status_or_score)
                        is_present = True

                    records.append(
                        CandidateRecord(
                            name=full_name,
                            cpf=cpf,
                            score=score,
                            is_present=is_present,
                        )
                    )
                    name_buffer = ""
                else:
                    # Buffer multiline name strings
                    name_buffer = f"{name_buffer} {line_str}".strip()

        logger.info("Successfully extracted %d candidate records.", len(records))
        return records
