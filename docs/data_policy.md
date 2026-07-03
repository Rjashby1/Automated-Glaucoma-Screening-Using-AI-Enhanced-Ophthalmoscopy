# Data Policy

This repo should contain code, configs, documentation, lightweight manifests, and aggregate report artifacts only.

Do not commit:

- clinical files
- Box folder links
- videos
- Photoshop or GIMP annotation sources
- raw public images
- generated synthetic images/masks
- model checkpoints
- secrets or Kaggle credentials

Allowed artifacts:

- manifest CSVs with project-relative paths
- aggregate validation summaries
- aggregate result tables
- non-sensitive qualitative overlay figures approved for reporting

Clinical data should remain local to secure storage/Rivanna project paths and should be referenced only by local project-relative paths inside ignored directories.
