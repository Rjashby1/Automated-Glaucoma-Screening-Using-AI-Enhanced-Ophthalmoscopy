# Experiment plan

## Research question

Can targeted online augmentation and offline synthetic data expansion reduce the public-to-clinical domain gap for optic cup/disc segmentation?

## Model comparison

Reportable model aliases:

- `baseline_unet`
- `unet_resnet50`
- `unet_efficientnet_b0`
- `unetplusplus_resnet50`
- `unetplusplus_efficientnet_b0`
- `deeplabv3plus_resnet50`
- `deeplabv3plus_efficientnet_b0` if stable

## Online augmentation ladder

1. none: resize/normalize only
2. geometric shift/rotation
3. mirror flip
4. scale/crop style affine jitter
5. color jitter/hue-like perturbation
6. blur/compression/noise
7. artificial glare
8. combined domain-gap augmentation

## Offline synthetic expansion ladder

Generate augmented copies only from training rows. Validation/test rows are never synthetically expanded.

1. raw only
2. raw + geometric synthetic copy
3. add mirrored copy
4. add color/hue copy
5. add scale/crop copy
6. add blur/compression/noise copy
7. add glare copy
8. optional CutMix/copy-paste as explicitly experimental

## Primary metrics

- optic disc Dice
- optic cup Dice
- mean foreground Dice
- disc IoU
- cup IoU
- vertical cup-to-disc-ratio MAE

Headline metric should be clinical/sponsor holdout cup Dice and combined cup/disc performance, provided the clinical holdout is valid and leakage-safe.
