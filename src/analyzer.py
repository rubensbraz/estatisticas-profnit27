"""Statistical Analysis module for PROFNIT entrance exam data.

This module processes parsed candidate data, enriches it with regional insights
derived from CPF patterns, and computes comprehensive statistical metrics.
"""

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.parser import CandidateRecord

logger = logging.getLogger(__name__)

# Mapping of CPF 9th digit to Brazilian State / Region groupings
CPF_REGION_MAP: Dict[int, str] = {
    0: "Rio Grande do Sul (RS)",
    1: "Distrito Federal, Goiás, Mato Grosso, Mato Grosso do Sul, Tocantins (DF/GO/MT/MS/TO)",
    2: "Acre, Amazonas, Amapá, Pará, Rondônia, Roraima (AC/AM/AP/PA/RO/RR)",
    3: "Ceará, Maranhão, Piauí (CE/MA/PI)",
    4: "Alagoas, Paraíba, Pernambuco, Rio Grande do Norte (AL/PB/PE/RN)",
    5: "Bahia, Sergipe (BA/SE)",
    6: "Minas Gerais (MG)",
    7: "Espírito Santo, Rio de Janeiro (ES/RJ)",
    8: "São Paulo (SP)",
    9: "Paraná, Santa Catarina (PR/SC)",
}


CPF_REGION_SHORT_MAP: Dict[int, str] = {
    0: "RS",
    1: "DF/GO/MT/MS/TO",
    2: "AC/AM/AP/PA/RO/RR",
    3: "CE/MA/PI",
    4: "AL/PB/PE/RN",
    5: "BA/SE",
    6: "MG",
    7: "ES/RJ",
    8: "SP",
    9: "PR/SC",
}


@dataclass
class AttendanceStats:
    """Summary of candidate attendance statistics."""

    total_candidates: int
    present_candidates: int
    absent_candidates: int
    attendance_rate_pct: float
    absence_rate_pct: float


@dataclass
class DescriptiveStats:
    """Summary of score descriptive statistics for present candidates."""

    count: int
    mean: float
    median: float
    mode: float
    std_dev: float
    variance: float
    min_score: int
    max_score: int
    q1_25pct: float
    q3_75pct: float
    iqr: float


@dataclass
class ThresholdStats:
    """Summary of candidates meeting specific score thresholds."""

    perfect_scores_20: int
    perfect_scores_pct: float
    high_scores_18_to_20: int
    high_scores_pct: float
    passing_scores_15_plus: int
    passing_scores_pct: float
    low_scores_under_10: int
    low_scores_pct: float


@dataclass
class ScoreFrequencyRow:
    """Frequency data for a specific score value."""

    score: int
    count: int
    percentage: float
    cumulative_count: int
    cumulative_percentage: float


@dataclass
class RegionalStatsRow:
    """Regional statistical breakdown derived from CPF digits."""

    digit: int
    region_name: str
    short_code: str
    total_candidates: int
    present_candidates: int
    absent_candidates: int
    mean_score: float
    median_score: float
    perfect_scores_count: int


@dataclass
class AnalysisResults:
    """Container holding complete statistical analysis results."""

    attendance: AttendanceStats
    descriptive: DescriptiveStats
    thresholds: ThresholdStats
    score_frequencies: List[ScoreFrequencyRow]
    regional_breakdown: List[RegionalStatsRow]
    df: pd.DataFrame


class StatisticalAnalyzer:
    """Analyzer for computing candidate performance and regional statistics."""

    def __init__(self, records: List[CandidateRecord]) -> None:
        """Initialize analyzer with candidate records.

        Args:
            records: List of CandidateRecord objects from PDF parser.
        """
        self.records = records
        self.df = self._build_dataframe(records)

    def _build_dataframe(self, records: List[CandidateRecord]) -> pd.DataFrame:
        """Convert candidate records to Pandas DataFrame and enrich with region info.

        Args:
            records: List of CandidateRecord objects.

        Returns:
            Enriched Pandas DataFrame.
        """
        data = []
        for r in records:
            digit_9 = -1
            if len(r.cpf) >= 9 and r.cpf[8].isdigit():
                digit_9 = int(r.cpf[8])

            region_name = CPF_REGION_MAP.get(digit_9, "Unknown Region")
            short_code = CPF_REGION_SHORT_MAP.get(digit_9, "UNK")

            data.append(
                {
                    "name": r.name,
                    "cpf": r.cpf,
                    "score": r.score,
                    "is_present": r.is_present,
                    "cpf_digit_9": digit_9,
                    "region_name": region_name,
                    "short_code": short_code,
                }
            )

        return pd.DataFrame(data)

    def analyze(self) -> AnalysisResults:
        """Perform complete statistical analysis.

        Returns:
            AnalysisResults object containing all computed statistics.
        """
        logger.info("Computing attendance statistics...")
        total_candidates = len(self.df)
        present_candidates = int(self.df["is_present"].sum())
        absent_candidates = total_candidates - present_candidates

        attendance_rate_pct = (
            (present_candidates / total_candidates * 100.0)
            if total_candidates > 0
            else 0.0
        )
        absence_rate_pct = (
            (absent_candidates / total_candidates * 100.0)
            if total_candidates > 0
            else 0.0
        )

        attendance = AttendanceStats(
            total_candidates=total_candidates,
            present_candidates=present_candidates,
            absent_candidates=absent_candidates,
            attendance_rate_pct=round(attendance_rate_pct, 2),
            absence_rate_pct=round(absence_rate_pct, 2),
        )

        logger.info("Computing descriptive statistics for present candidates...")
        present_df = self.df[self.df["is_present"]].copy()
        scores = present_df["score"].astype(float)

        mean_val = float(scores.mean())
        median_val = float(scores.median())
        mode_val = float(scores.mode()[0]) if not scores.empty else 0.0
        std_val = float(scores.std())
        var_val = float(scores.var())
        min_val = int(scores.min())
        max_val = int(scores.max())
        q1_val = float(np.percentile(scores, 25))
        q3_val = float(np.percentile(scores, 75))
        iqr_val = q3_val - q1_val

        descriptive = DescriptiveStats(
            count=present_candidates,
            mean=round(mean_val, 2),
            median=round(median_val, 2),
            mode=round(mode_val, 2),
            std_dev=round(std_val, 2),
            variance=round(var_val, 2),
            min_score=min_val,
            max_score=max_val,
            q1_25pct=round(q1_val, 2),
            q3_75pct=round(q3_val, 2),
            iqr=round(iqr_val, 2),
        )

        logger.info("Computing threshold statistics...")
        perfect_20 = int((scores == 20).sum())
        high_18_20 = int((scores >= 18).sum())
        pass_15 = int((scores >= 15).sum())
        low_under_10 = int((scores < 10).sum())

        thresholds = ThresholdStats(
            perfect_scores_20=perfect_20,
            perfect_scores_pct=round(perfect_20 / present_candidates * 100.0, 2),
            high_scores_18_to_20=high_18_20,
            high_scores_pct=round(high_18_20 / present_candidates * 100.0, 2),
            passing_scores_15_plus=pass_15,
            passing_scores_pct=round(pass_15 / present_candidates * 100.0, 2),
            low_scores_under_10=low_under_10,
            low_scores_pct=round(low_under_10 / present_candidates * 100.0, 2),
        )

        logger.info("Computing score frequency distribution...")
        score_counts = scores.value_counts().sort_index(ascending=False)
        score_frequencies: List[ScoreFrequencyRow] = []

        cumulative_count = 0
        # Iterate from score 20 down to 0
        for score_val in range(20, -1, -1):
            count = int(score_counts.get(score_val, 0))
            percentage = (
                round(count / present_candidates * 100.0, 2)
                if present_candidates > 0
                else 0.0
            )
            cumulative_count += count
            cum_pct = (
                round(cumulative_count / present_candidates * 100.0, 2)
                if present_candidates > 0
                else 0.0
            )

            score_frequencies.append(
                ScoreFrequencyRow(
                    score=score_val,
                    count=count,
                    percentage=percentage,
                    cumulative_count=cumulative_count,
                    cumulative_percentage=cum_pct,
                )
            )

        logger.info("Computing regional statistics...")
        regional_breakdown: List[RegionalStatsRow] = []
        grouped = self.df.groupby("cpf_digit_9")

        for digit in sorted(CPF_REGION_MAP.keys()):
            if digit in grouped.groups:
                group_df = grouped.get_group(digit)
                reg_total = len(group_df)
                reg_present_df = group_df[group_df["is_present"]]
                reg_present = len(reg_present_df)
                reg_absent = reg_total - reg_present

                if reg_present > 0:
                    reg_mean = float(reg_present_df["score"].mean())
                    reg_median = float(reg_present_df["score"].median())
                    reg_perfect = int((reg_present_df["score"] == 20).sum())
                else:
                    reg_mean = 0.0
                    reg_median = 0.0
                    reg_perfect = 0

                regional_breakdown.append(
                    RegionalStatsRow(
                        digit=digit,
                        region_name=CPF_REGION_MAP[digit],
                        short_code=CPF_REGION_SHORT_MAP[digit],
                        total_candidates=reg_total,
                        present_candidates=reg_present,
                        absent_candidates=reg_absent,
                        mean_score=round(reg_mean, 2),
                        median_score=round(reg_median, 2),
                        perfect_scores_count=reg_perfect,
                    )
                )

        return AnalysisResults(
            attendance=attendance,
            descriptive=descriptive,
            thresholds=thresholds,
            score_frequencies=score_frequencies,
            regional_breakdown=regional_breakdown,
            df=self.df,
        )
