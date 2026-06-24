"""
GPU smoke test for Rivanna training sessions.

This script checks whether PyTorch can see the assigned GPU and run a tiny
CUDA tensor operation. It is intended to be run before launching training.

Local Mac usage:
    python scripts/smoke_test_gpu.py

Rivanna GPU usage:
    python scripts/smoke_test_gpu.py --require-cuda
"""

from __future__ import annotations

import argparse

import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test PyTorch GPU availability.")
    parser.add_argument(
        "--require-cuda",
        action="store_true",
        help="Fail if CUDA is not available. Use this on Rivanna GPU sessions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("torch:", torch.__version__)
    print("torch cuda version:", torch.version.cuda)
    print("cuda available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("cuda device count:", torch.cuda.device_count())
        print("device 0:", torch.cuda.get_device_name(0))
        print("compute capability:", torch.cuda.get_device_capability(0))
        print("torch arch list:", torch.cuda.get_arch_list())
        print("bf16 supported:", torch.cuda.is_bf16_supported())

        x = torch.randn(2, 3, 128, 128, device="cuda")
        conv = torch.nn.Conv2d(3, 8, kernel_size=3, padding=1).cuda()
        y = conv(x)

        print("cuda tensor test output shape:", tuple(y.shape))
        print("GPU smoke test passed.")
        return

    if args.require_cuda:
        raise RuntimeError(
            "CUDA is not available. Check GPU allocation, PyTorch install, "
            "or CUDA compatibility."
        )

    print("CUDA not available. This is expected on local Mac CPU/MPS development.")
    print("Non-CUDA smoke test passed.")


if __name__ == "__main__":
    main()