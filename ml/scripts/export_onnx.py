"""Export a HuggingFace pretrained model to ONNX (with optional int8 quantisation).

Used for the Synthetic Reality Detectors that run in-browser via ONNX Runtime Web.
The same ONNX file is also loadable from Python (backend) for testing.

Phase 2 implementation (Step 2.17 — MUST-DO per Sovereign AI narrative): in-browser
AI detection means content never leaves the device for synthetic-reality scoring.
Provenance Agent's `text_ai_confidence` + `avatar_ai_confidence` consume these
ONNX scores in Year 1 plan.

Usage (run from ml/):
    uv run python scripts/export_onnx.py \\
      --hf-model Hello-SimpleAI/chatgpt-detector-roberta \\
      --task text-classification \\
      --output ../demo/site/public/models/text-ai-detector

    uv run python scripts/export_onnx.py \\
      --hf-model umm-maybe/AI-image-detector \\
      --task image-classification \\
      --output ../demo/site/public/models/image-ai-detector

Honest pitch caveat (anti-pattern #7): ONNX detectors are pretrained — confidence
varies. Always show score, never claim "99% accuracy". UI surfaces the model's
score with a "this is a signal, not a verdict" note.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _export_via_cli(hf_model: str, task: str, output: Path) -> None:
    """Use optimum-cli (optimum 2.x — Python API moved to separate optimum-onnx pkg)."""
    import subprocess

    output.mkdir(parents=True, exist_ok=True)
    cmd = [
        "optimum-cli", "export", "onnx",
        "--model", hf_model,
        "--task", task,
        str(output),
    ]
    print(f"[export_onnx] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"[export_onnx] optimum-cli failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"[export_onnx] Saved to {output}")


def _quantize_int8(model_dir: Path) -> None:
    """Dynamic int8 quantisation via onnxruntime.quantization. ~3-4x size reduction."""
    onnx_files = [f for f in model_dir.glob("*.onnx") if "quant" not in f.name.lower()]
    if not onnx_files:
        print(f"[export_onnx] No .onnx file in {model_dir}, skipping quantisation",
              file=sys.stderr)
        return

    try:
        from onnxruntime.quantization import QuantType, quantize_dynamic
    except ImportError as e:
        print(f"[export_onnx] onnxruntime.quantization unavailable ({e}); skipping",
              file=sys.stderr)
        return

    src = onnx_files[0]
    dst = src.with_name(f"{src.stem}-int8{src.suffix}")
    print(f"[export_onnx] Quantising int8 (dynamic): {src.name} -> {dst.name}")
    quantize_dynamic(str(src), str(dst), weight_type=QuantType.QInt8)
    # Replace fp32 with int8 (smaller for browser shipping)
    src.unlink()
    dst.rename(src)
    print("[export_onnx] Quantisation done (replaced fp32 file)")


def _report(model_dir: Path) -> None:
    """Print sizes of exported ONNX files."""
    onnx_files = sorted(model_dir.glob("*.onnx"))
    if not onnx_files:
        print(f"[export_onnx] WARNING: no .onnx files found in {model_dir}",
              file=sys.stderr)
        return
    print(f"[export_onnx] Final files in {model_dir}:")
    for f in onnx_files:
        sz_mb = f.stat().st_size / 1024 / 1024
        print(f"  {f.name:50s} {sz_mb:6.1f} MB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hf-model", required=True,
        help="HuggingFace model id (e.g., Hello-SimpleAI/chatgpt-detector-roberta)",
    )
    parser.add_argument(
        "--task", required=True,
        choices=["text-classification", "image-classification"],
        help="Optimum task type",
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Output directory (ONNX + tokenizer/processor saved here)",
    )
    parser.add_argument(
        "--quantize", choices=["none", "int8"], default="int8",
        help="Quantisation level (int8 = ~3x smaller, slight accuracy hit)",
    )
    args = parser.parse_args()

    _export_via_cli(args.hf_model, args.task, args.output)

    if args.quantize == "int8":
        _quantize_int8(args.output)

    _report(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
