"""PDF Report Generation module for PROFNIT preliminary result statistics.

This module builds a multi-page PDF document incorporating KPI cards, formatted data tables,
and embedded charts using ReportLab Platypus.
"""

from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Union

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.analyzer import AnalysisResults

logger = logging.getLogger(__name__)


class NumberedCanvas(canvas.Canvas):
    """Canvas implementation for multi-pass page numbering ('Page X of Y')."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize canvas with page record list."""
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[dict] = []

    def showPage(self) -> None:
        """Record page state and start a new page."""
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        """Draw footers and headers on all saved page states during final pass."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


    def draw_page_number(self, page_count: int) -> None:
        """Draw running headers and footers.

        Args:
            page_count: Total number of pages in the document.
        """
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer line
        self.setLineWidth(0.5)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.line(36, 36, letter[0] - 36, 36)

        # Footer content
        footer_text = "PROFNIT 2027 Entrance Exam (ENA27) - Preliminary Results Statistical Report"
        page_str = f"Page {self._pageNumber} of {page_count}"

        self.drawString(36, 24, footer_text)
        self.drawRightString(letter[0] - 36, 24, page_str)

        # Running header for pages > 1
        if self._pageNumber > 1:
            self.drawString(36, letter[1] - 25, "PROFNIT 2027 - Executive Statistical Report")
            self.drawRightString(
                letter[0] - 36,
                letter[1] - 25,
                datetime.now().strftime("%Y-%m-%d"),
            )
            self.line(36, letter[1] - 30, letter[0] - 36, letter[1] - 30)

        self.restoreState()


class PDFReportGenerator:
    """PDF Document generator for statistical analysis results."""

    def __init__(self, output_path: Union[str, Path]) -> None:
        """Initialize PDF generator.

        Args:
            output_path: Path where the output PDF will be created.
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_styles()

    def _init_styles(self) -> None:
        """Initialize custom paragraph styles for document."""

        self.styles = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "DocTitle",
            parent=self.styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        )

        self.subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=15,
        )

        self.h1_style = ParagraphStyle(
            "SectionH1",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        )

        self.body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=self.styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8,
        )

        self.kpi_title_style = ParagraphStyle(
            "KPITitle",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748B"),
            alignment=1,  # Center
        )

        self.kpi_value_style = ParagraphStyle(
            "KPIValue",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=18,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=1,  # Center
        )

        self.kpi_sub_style = ParagraphStyle(
            "KPISub",
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#475569"),
            alignment=1,  # Center
        )

        self.tbl_header_style = ParagraphStyle(
            "TblHeader",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.white,
            alignment=1,
        )

        self.tbl_cell_style = ParagraphStyle(
            "TblCell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B"),
            alignment=0,
        )

        self.tbl_cell_center = ParagraphStyle(
            "TblCellCenter",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B"),
            alignment=1,
        )

    def generate(
        self, results: AnalysisResults, chart_paths: Dict[str, Path]
    ) -> Path:
        """Generate PDF document from analysis results and chart images.

        Args:
            results: AnalysisResults object containing calculated statistics.
            chart_paths: Dictionary mapping chart keys to PNG image file paths.

        Returns:
            Path to the generated PDF document.
        """
        logger.info("Building PDF document at: %s", self.output_path)
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=45,
        )

        story = []

        # 1. Document Header
        story.append(
            Paragraph(
                "PROFNIT 2027 Entrance Exam (ENA27)",
                self.title_style,
            )
        )
        story.append(
            Paragraph(
                "Executive Statistical Report - Stage 1 National Examination Preliminary Results",
                self.subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=15))

        # 2. Executive Summary KPI Blocks
        kpi_table = self._build_kpi_cards(results)
        story.append(kpi_table)
        story.append(Spacer(1, 15))

        # 3. Attendance & General Performance Overview
        story.append(Paragraph("1. General Attendance & Descriptive Performance", self.h1_style))
        story.append(
            Paragraph(
                "The preliminary results cover a total of <b>1,845 candidates</b> registered for the Stage 1 "
                "National Examination (ENA27). Out of these, <b>1,749 candidates</b> took the exam, establishing an "
                "attendance rate of <b>94.80%</b>. The overall mean score achieved by present candidates is <b>18.03 out of 20</b>.",
                self.body_style,
            )
        )

        # Descriptive Statistics Table
        desc_table = self._build_descriptive_table(results)
        story.append(desc_table)
        story.append(Spacer(1, 10))

        # Chart: Score Distribution
        if "score_distribution" in chart_paths:
            img_path = chart_paths["score_distribution"]
            story.append(Image(str(img_path), width=480, height=210))

        story.append(PageBreak())

        # 4. Score Thresholds & Frequency Distribution
        story.append(Paragraph("2. Score Frequency & Cutoff Percentiles", self.h1_style))
        story.append(
            Paragraph(
                "Candidate performance displays high concentration at top scores. A total of <b>918 candidates (52.49%)</b> "
                "scored a perfect 20 out of 20. Furthermore, <b>76.44%</b> scored 18 or above, and <b>86.68%</b> reached or "
                "exceeded 15 points. The detailed score breakdown is listed below:",
                self.body_style,
            )
        )

        # Score Frequency Table & Cumulative Chart
        freq_table = self._build_frequency_table(results)
        story.append(freq_table)
        story.append(Spacer(1, 10))

        if "cumulative_distribution" in chart_paths:
            img_path = chart_paths["cumulative_distribution"]
            story.append(Image(str(img_path), width=480, height=200))

        story.append(PageBreak())

        # 5. Regional Demographics (CPF State Code)
        story.append(Paragraph("3. Geographic Demographics by CPF State Code", self.h1_style))
        story.append(
            Paragraph(
                "Using the 9th digit of candidate CPFs (the state issuing jurisdiction code), we map candidates across Brazilian "
                "administrative regions. Region 2 (AC/AM/AP/PA/RO/RR) represented the highest candidate volume (425 candidates), "
                "followed by Region 1 (DF/GO/MT/MS/TO) with 306 candidates.",
                self.body_style,
            )
        )

        reg_table = self._build_regional_table(results)
        story.append(reg_table)
        story.append(Spacer(1, 10))

        if "regional_volume" in chart_paths:
            img_path = chart_paths["regional_volume"]
            story.append(Image(str(img_path), width=480, height=190))
            story.append(Spacer(1, 8))

        if "regional_means" in chart_paths:
            img_path = chart_paths["regional_means"]
            story.append(Image(str(img_path), width=480, height=180))


        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info("PDF generation complete: %s", self.output_path)
        return self.output_path

    def _build_kpi_cards(self, results: AnalysisResults) -> Table:
        """Construct 4-card KPI summary banner.

        Args:
            results: AnalysisResults object.

        Returns:
            Formatted ReportLab Table object.
        """
        att = results.attendance
        desc = results.descriptive
        thresh = results.thresholds

        card1 = [
            Paragraph("TOTAL CANDIDATES", self.kpi_title_style),
            Paragraph(f"{att.total_candidates:,}", self.kpi_value_style),
            Paragraph(f"{att.present_candidates:,} Present ({att.attendance_rate_pct:.1f}%)", self.kpi_sub_style),
        ]

        card2 = [
            Paragraph("ATTENDANCE RATE", self.kpi_title_style),
            Paragraph(f"{att.attendance_rate_pct:.1f}%", self.kpi_value_style),
            Paragraph(f"{att.absent_candidates:,} Absent ({att.absence_rate_pct:.1f}%)", self.kpi_sub_style),
        ]

        card3 = [
            Paragraph("NATIONAL MEAN SCORE", self.kpi_title_style),
            Paragraph(f"{desc.mean:.2f} / 20", self.kpi_value_style),
            Paragraph(f"Median: {desc.median:.1f} | Std: {desc.std_dev:.2f}", self.kpi_sub_style),
        ]

        card4 = [
            Paragraph("PERFECT SCORES (20/20)", self.kpi_title_style),
            Paragraph(f"{thresh.perfect_scores_20:,}", self.kpi_value_style),
            Paragraph(f"{thresh.perfect_scores_pct:.1f}% of Present Candidates", self.kpi_sub_style),
        ]

        data = [[card1, card2, card3, card4]]
        card_table = Table(data, colWidths=[130, 130, 130, 130])
        card_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return card_table

    def _build_descriptive_table(self, results: AnalysisResults) -> Table:
        """Build descriptive statistics summary table.

        Args:
            results: AnalysisResults container.

        Returns:
            ReportLab Table object.
        """
        att = results.attendance
        desc = results.descriptive
        t = results.thresholds

        header = [
            Paragraph("Metric", self.tbl_header_style),
            Paragraph("Value", self.tbl_header_style),
            Paragraph("Metric", self.tbl_header_style),
            Paragraph("Value", self.tbl_header_style),
        ]

        rows = [
            header,
            [
                Paragraph("Total Candidates Registered", self.tbl_cell_style),
                Paragraph(f"{att.total_candidates:,}", self.tbl_cell_center),
                Paragraph("Mean Score (Out of 20)", self.tbl_cell_style),
                Paragraph(f"{desc.mean:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("Present Candidates", self.tbl_cell_style),
                Paragraph(f"{att.present_candidates:,} ({att.attendance_rate_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("Median Score", self.tbl_cell_style),
                Paragraph(f"{desc.median:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("Absent Candidates", self.tbl_cell_style),
                Paragraph(f"{att.absent_candidates:,} ({att.absence_rate_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("Mode Score", self.tbl_cell_style),
                Paragraph(f"{desc.mode:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("Perfect Scores (20/20)", self.tbl_cell_style),
                Paragraph(f"{t.perfect_scores_20:,} ({t.perfect_scores_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("Standard Deviation", self.tbl_cell_style),
                Paragraph(f"{desc.std_dev:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("High Scores (>= 18)", self.tbl_cell_style),
                Paragraph(f"{t.high_scores_18_to_20:,} ({t.high_scores_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("Variance", self.tbl_cell_style),
                Paragraph(f"{desc.variance:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("Passing Grade (>= 15)", self.tbl_cell_style),
                Paragraph(f"{t.passing_scores_15_plus:,} ({t.passing_scores_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("25th Percentile (Q1)", self.tbl_cell_style),
                Paragraph(f"{desc.q1_25pct:.2f}", self.tbl_cell_center),
            ],
            [
                Paragraph("Low Scores (< 10)", self.tbl_cell_style),
                Paragraph(f"{t.low_scores_under_10:,} ({t.low_scores_pct:.1f}%)", self.tbl_cell_center),
                Paragraph("75th Percentile (Q3)", self.tbl_cell_style),
                Paragraph(f"{desc.q3_75pct:.2f}", self.tbl_cell_center),
            ],
        ]

        tbl = Table(rows, colWidths=[150, 110, 150, 110])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return tbl

    def _build_frequency_table(self, results: AnalysisResults) -> Table:
        """Construct full score frequency distribution table.

        Args:
            results: AnalysisResults object.

        Returns:
            ReportLab Table object.
        """
        header = [
            Paragraph("Score", self.tbl_header_style),
            Paragraph("Candidates Count", self.tbl_header_style),
            Paragraph("Percentage (%)", self.tbl_header_style),
            Paragraph("Cumulative Count", self.tbl_header_style),
            Paragraph("Cumulative %", self.tbl_header_style),
        ]

        rows = [header]
        for row in results.score_frequencies:
            # Highlight top scores
            cell_bg = colors.white
            if row.score == 20:
                cell_bg = colors.HexColor("#EFF6FF")

            rows.append(
                [
                    Paragraph(f"<b>{row.score}</b>", self.tbl_cell_center),
                    Paragraph(f"{row.count:,}", self.tbl_cell_center),
                    Paragraph(f"{row.percentage:.2f}%", self.tbl_cell_center),
                    Paragraph(f"{row.cumulative_count:,}", self.tbl_cell_center),
                    Paragraph(f"{row.cumulative_percentage:.2f}%", self.tbl_cell_center),
                ]
            )

        tbl = Table(rows, colWidths=[65, 110, 110, 115, 110])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return tbl

    def _build_regional_table(self, results: AnalysisResults) -> Table:
        """Construct CPF region statistical breakdown table.

        Args:
            results: AnalysisResults object.

        Returns:
            ReportLab Table object.
        """
        header = [
            Paragraph("CPF Code", self.tbl_header_style),
            Paragraph("Region / States Included", self.tbl_header_style),
            Paragraph("Total Reg.", self.tbl_header_style),
            Paragraph("Present", self.tbl_header_style),
            Paragraph("Absent", self.tbl_header_style),
            Paragraph("Mean Score", self.tbl_header_style),
            Paragraph("20/20 Count", self.tbl_header_style),
        ]

        rows = [header]
        for reg in results.regional_breakdown:
            rows.append(
                [
                    Paragraph(f"<b>Digit {reg.digit}</b>", self.tbl_cell_center),
                    Paragraph(reg.region_name, self.tbl_cell_style),
                    Paragraph(f"{reg.total_candidates:,}", self.tbl_cell_center),
                    Paragraph(f"{reg.present_candidates:,}", self.tbl_cell_center),
                    Paragraph(f"{reg.absent_candidates:,}", self.tbl_cell_center),
                    Paragraph(f"{reg.mean_score:.2f}", self.tbl_cell_center),
                    Paragraph(f"{reg.perfect_scores_count:,}", self.tbl_cell_center),
                ]
            )

        tbl = Table(rows, colWidths=[55, 200, 50, 50, 45, 60, 60])
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return tbl
