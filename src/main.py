"""Main entry point for PROFNIT 2027 Entrance Exam Statistical Analysis.

This module orchestrates PDF parsing, statistical computations, chart generation,
and executive PDF report creation.
"""

import argparse
import logging
from pathlib import Path
import sys

from src.analyzer import StatisticalAnalyzer
from src.charts import ChartGenerator
from src.parser import PDFParser
from src.pdf_generator import PDFReportGenerator

# Configure console logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("profnit_stats")


def main() -> int:
    """Main execution function for CLI workflow.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="PROFNIT 2027 Exame Nacional de Acesso (ENA27) - Análise Estatística & Gerador de PDF"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="data/ENA27-Resultado-Preliminar-Prova-Nacional.pdf",
        help="Caminho para o arquivo PDF com o resultado preliminar.",
    )
    parser.add_argument(
        "--output-pdf",
        "-o",
        type=str,
        default="output/PROFNIT_2027_Preliminary_Results_Report.pdf",
        help="Caminho onde o relatório PDF será salvo.",
    )
    parser.add_argument(
        "--charts-dir",
        "-c",
        type=str,
        default="output/charts",
        help="Diretório onde os gráficos PNG serão salvos.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_pdf_path = Path(args.output_pdf)
    charts_dir = Path(args.charts_dir)

    print("=" * 70)
    print("  PROFNIT 2027 - Exame Nacional de Acesso (ENA27) - Análise Estatística")
    print("=" * 70)

    try:
        # Step 1: Parse PDF Document
        logger.info("Etapa 1/4: Extraindo dados do arquivo PDF...")
        pdf_parser = PDFParser(input_path)
        records = pdf_parser.parse()
        logger.info("Extraídos %d registros de candidatos com sucesso.", len(records))

        # Step 2: Compute Statistical Metrics
        logger.info("Etapa 2/4: Calculando estatísticas e mapeamento por região de CPF...")
        analyzer = StatisticalAnalyzer(records)
        results = analyzer.analyze()

        print("\n" + "-" * 70)
        print("  MÉTRICAS PRINCIPAIS DE DESEMPENHO")
        print("-" * 70)
        print(f"  • Total de Candidatos Inscritos:  {results.attendance.total_candidates:,}")
        print(f"  • Candidatos Presentes:           {results.attendance.present_candidates:,} ({results.attendance.attendance_rate_pct:.2f}%)")
        print(f"  • Candidatos Ausentes:            {results.attendance.absent_candidates:,} ({results.attendance.absence_rate_pct:.2f}%)")
        print(f"  • Média Nacional de Acertos:      {results.descriptive.mean:.2f} / 20,00")
        print(f"  • Mediana Nacional de Acertos:    {results.descriptive.median:.2f} / 20,00")
        print(f"  • Gabaritaram (20/20):            {results.thresholds.perfect_scores_20:,} ({results.thresholds.perfect_scores_pct:.2f}%)")
        print(f"  • Desempenho Alto (>= 18):        {results.thresholds.high_scores_18_to_20:,} ({results.thresholds.high_scores_pct:.2f}%)")
        print(f"  • Nota de Aprovado (>= 15):       {results.thresholds.passing_scores_15_plus:,} ({results.thresholds.passing_scores_pct:.2f}%)")
        print("-" * 70 + "\n")

        # Step 3: Generate Visual Charts
        logger.info("Etapa 3/4: Gerando gráficos em alta resolução...")
        chart_gen = ChartGenerator(charts_dir)
        chart_paths = chart_gen.generate_all_charts(results)
        for key, path in chart_paths.items():
            logger.info("Gráfico gerado [%s]: %s", key, path)

        # Step 4: Build PDF Report
        logger.info("Etapa 4/4: Construindo relatório executivo em PDF...")
        pdf_gen = PDFReportGenerator(output_pdf_path)
        final_pdf_path = pdf_gen.generate(results, chart_paths)

        print("=" * 70)
        print(f"  SUCESSO! Relatório em PDF gerado em:")
        print(f"  --> {final_pdf_path.resolve()}")
        print("=" * 70 + "\n")
        return 0

    except Exception as exc:
        logger.error("Falha na execução: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
