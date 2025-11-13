import re
import subprocess
from pathlib import Path

import torch
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer


class ReceiptData(BaseModel):
    shop_name: str
    total_amount: int


class ReceiptDataList(BaseModel):
    receipts: list[ReceiptData]

    def __str__(self) -> str:
        return "\n".join([f"{r.shop_name},{r.total_amount}" for r in self.receipts])

    def __repr__(self):
        return self.__str__()

    def add_receipt(self, receipt: ReceiptData) -> None:
        self.receipts.append(receipt)


def run_yomitoku(
    path: Path,
    format: str = "md",
    outdir: Path = Path("results"),
    with_viz: bool = False,
    with_figure: bool = False,
    verbose: bool = False,
) -> None:
    """Run the Yomitoku application."""
    cmd = f"uv run yomitoku {path} -f {format} -o {outdir}"
    if with_viz:
        cmd += " -v"
    if with_figure:
        cmd += " --figure"
    subprocess.run([cmd], shell=True, check=True)


def _extract_with_gemma(text: str, prompt: str) -> str:
    """Extract information using Gemma-2-baku-2b-it model."""
    model_id = "rinna/gemma-2-baku-2b-it"
    dtype = torch.bfloat16

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        dtype=dtype,
        attn_implementation="eager",
    )

    chat = [{"role": "user", "content": f"{prompt}\n\n{text}"}]
    formatted_prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

    input_ids = tokenizer.encode(formatted_prompt, add_special_tokens=False, return_tensors="pt").to(model.device)
    outputs = model.generate(
        input_ids,
        max_new_tokens=128,
        temperature=0.1,
        do_sample=True,
    )

    response = tokenizer.decode(outputs[0][input_ids.shape[-1] :], skip_special_tokens=True)
    return response.strip()


def extract_receipt_data_from_text(receipt_text: str) -> ReceiptDataList:
    """Extract shop name and total amount from receipt text."""
    prompt = """
        このレシートから店名と合計金額を抽出してください。店名と合計額のみを回答してください。複数ある場合はすべて回答してください。
        回答形式は以下の通りです。
        店名: <店名>,合計金額: <合計金額>\n店名: <店名>,合計金額: <合計金額>\n...
    """
    response = _extract_with_gemma(receipt_text, prompt)
    shop_name = ""
    total_amount = 0
    receipt_data_list = ReceiptDataList(receipts=[])
    lines = response.splitlines()
    for line in lines:
        match = re.match(r"店名:\s*(.+),\s*合計金額:\s*([0-9,]+)", line)
        if match:
            shop_name = match.group(1).strip()
            amount_str = match.group(2).replace(",", "")
            try:
                total_amount = int(amount_str)
            except ValueError:
                total_amount = 0
            receipt_data_list.add_receipt(ReceiptData(shop_name=shop_name, total_amount=total_amount))
    return receipt_data_list


def extract_receipt_data(receipt_file_path: Path) -> ReceiptDataList:
    """Extract shop name and total amount from yomitoku result file."""
    receipt_text = receipt_file_path.read_text(encoding="utf-8")
    return extract_receipt_data_from_text(receipt_text)
