# Project scope

The capstone center of gravity is optic cup/disc segmentation under domain shift.

In scope:

1. public dataset audit and manifest validation;
2. leakage-aware train/validation/test split construction;
3. baseline U-Net reproduction/sanity training;
4. model comparison across U-Net, U-Net++, and DeepLabV3+ with pretrained encoders;
5. online augmentation ablation;
6. offline synthetic dataset expansion through augmentation;
7. public holdout and sponsor/clinical holdout evaluation when valid clinical masks exist;
8. result tables, figures, code documentation, and sponsor handoff.

Out of scope for this package:

- full DDLS clinical product;
- EHR/Epic integration;
- production iPad app;
- raw video frame selection unless explicitly requested later;
- formal clinical validation beyond capstone evaluation;
- committing clinical data to GitHub.
