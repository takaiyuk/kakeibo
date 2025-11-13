from pathlib import Path

import structlog

from receipt.receipt import extract_receipt_data, run_yomitoku


def main() -> int:
    logger = structlog.get_logger(__name__)
    logger.debug("Receipt main executed")

    pwd = Path(__file__).parent.parent.parent.parent
    result_dir = Path(f"{pwd}/results")
    base_filename = "IMG_5240"
    original_path = Path(f"{pwd}/tmp/{base_filename}.jpg")
    result_path = result_dir / f"tmp_{base_filename}_p1.md"

    run_yomitoku(original_path, outdir=result_dir)
    receipt_data_list = extract_receipt_data(result_path)
    logger.info(f"Extracted receipt data: {receipt_data_list}")
    return 0
