# Raw Data Audit Summary

Created: 2026-06-04T12:11:33

Audited folder: `/sfs/gpfs/tardis/home/gsr3qz/Documents/MSDS/CAPSTONE/GitHub/Automated-Glaucoma-Screening-Using-AI-Enhanced-Ophthalmoscopy/data/raw`

## Project Objective Context

This audit supports a data-centric segmentation and generalization study for optic cup and optic disc segmentation. The core project question is whether targeted augmentation, synthetic data expansion, and careful held-out evaluation can improve segmentation on low-quality head-mounted ophthalmoscopy frames while maintaining performance on clean public fundus data.

The most important audit task is to separate public/reference data from sponsor/clinic data, identify cup/disc labels or masks, and determine whether patient/video/eye grouping information exists for leakage-safe train/validation/test splits.

## High-Level Counts

- Total files audited: **17,932**
- Total audited size: **4,377.143 MB**
- Image files: **15,251**
- Possible mask/label/prediction files: **17,868**
- Metadata/annotation-like files: **2,620**
- Video files: **2**
- Model artifacts: **7**
- Code/config artifacts: **29**
- Document/log artifacts: **1,975**

## Immediate Interpretation

- Review `manual_review_targets.csv` first. It is the triage list for finding sponsor data, masks, public data, and prior baseline artifacts.
- Review `sponsor_clinic_candidate_dirs.csv` to locate Dr. D / Tien clinic data and possible grouped split clues.
- Review `public_reference_candidate_dirs.csv` to confirm ORIGA or other public fundus data provided in the handoff.
- Review `candidate_mask_label_directories.csv` to pair input images with optic cup/disc masks, predictions, PSD labels, bounding boxes, or MATLAB annotations.
- Review `group_split_clues.csv` before any train/validation/test split. Frames from the same patient, video, or eye should not be split across train and holdout.

## File Types

| extension | file_count | total_size_mb |
| --- | --- | --- |
| .jpg | 8144 | 1670.328387 |
| .png | 7105 | 745.759912 |
| .txt | 1957 | 3.884429 |
| .mat | 650 | 16.017994 |
| .py | 19 | 0.150592 |
| .docx | 9 | 1.274978 |
| .csv | 9 | 0.200359 |
| .sh | 6 | 0.00681 |
| .ckpt | 6 | 778.432848 |
| .pdf | 4 | 23.860342 |
| .psd | 4 | 15.080081 |
| .mp4 | 2 | 642.237878 |
| .zip | 2 | 428.205204 |
| .tif | 2 | 0.047823 |
| .xlsx | 2 | 0.036036 |
| .pptx | 2 | 8.180976 |
| .pyc | 2 | 0.015803 |
| .yaml | 2 | 2.1e-05 |
| .log | 1 | 0.000322 |
| .ipynb | 1 | 0.167791 |
| .pth | 1 | 43.252275 |
| .bat | 1 | 0.001008 |
| .0 | 1 | 0.001062 |

## Top-Level Source Areas

| source_area | file_count | total_size_mb |
| --- | --- | --- |
| extracted_zips | 17926 | 4374.227535 |
| loose_files | 6 | 2.915399 |

## Source Package Areas

| package_area | file_count | total_size_mb | public_keyword_hits | sponsor_keyword_hits | baseline_keyword_hits |
| --- | --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive | 10002 | 2363.545887 | 0 | 1 | 0 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025 | 5433 | 865.898868 | 1 | 1 | 0 |
| extracted_zips/rivanna_train_discview | 2087 | 963.514951 | 0 | 1 | 0 |
| extracted_zips/convert_psd_to_label | 238 | 85.530671 | 0 | 0 | 0 |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images | 109 | 58.332504 | 0 | 1 | 0 |
| extracted_zips/Tien_DiscView/Test_Processed_Images | 48 | 5.31279 | 0 | 1 | 0 |
| loose_files | 6 | 2.915399 | 0 | 0 | 0 |
| extracted_zips/Tien_DiscView/paper_pdfs | 4 | 23.860342 | 0 | 1 | 0 |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt | 3 | 8.202491 | 0 | 2 | 0 |
| extracted_zips/Tien_DiscView/Segmentation_Model | 1 | 0.011416 | 0 | 1 | 1 |
| extracted_zips/Tien_DiscView/web_application | 1 | 0.017615 | 0 | 1 | 0 |

## Manual Review Targets

| priority | review_type | directory | file_count | image_file_count | total_size_mb | why_review |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 484 | 499.794535 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 650 | 465.651101 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 650 | 182.675507 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-3 | 215 | 215 | 153.447057 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-2 | 208 | 208 | 140.022337 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 650 | 90.597908 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 488 | 83.191399 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 113 | 67.969578 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 113 | 67.969578 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 455 | 63.436172 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 650 | 46.608776 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 650 | 46.608776 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 650 | 35.066236 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 650 | 35.066236 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Images_Square | 650 | 650 | 35.066236 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 455 | 32.426007 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 650 | 6.949396 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 650 | 5.839859 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 650 | 5.102674 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 650 | 5.028817 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Cropped | 650 | 650 | 1.641981 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Square | 651 | 651 | 0.993426 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Masks_Square | 650 | 650 | 0.98952 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Masks_Square | 650 | 650 | 0.98952 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/masks | 455 | 455 | 0.692397 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/masks | 455 | 455 | 0.692397 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 1 | sponsor_clinic_candidate | extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_image_masks | 113 | 113 | 0.303635 | Potential Dr. Dirghangi / clinic / head-mounted frame data. Needed for sponsor holdout and grouped splitting. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 650 | 90.597908 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 488 | 83.191399 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 113 | 67.969578 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 113 | 67.969578 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 455 | 63.436172 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 109 | 58.332504 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 650 | 46.608776 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |
| 2 | mask_label_candidate | extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 650 | 46.608776 | Potential cup/disc masks, predictions, PSD labels, or bounding boxes. Needed to pair images with ground truth. |

_Showing top 40 of 127 rows._

## Public / Reference Dataset Candidates

| directory | image_file_count | metadata_file_count | total_size_mb | matched_public_keywords | extension_counts |
| --- | --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Square | 651 | 0 | 0.993426 | origa | .png:651 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 0 | 465.651101 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 0 | 182.675507 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 0 | 90.597908 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 0 | 46.608776 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 0 | 35.066236 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 0 | 35.066236 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 0 | 6.949396 | origa | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 0 | 5.839859 | origa | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 0 | 5.102674 | origa | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 0 | 5.028817 | origa | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Cropped | 650 | 0 | 1.641981 | origa | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Masks_Square | 650 | 0 | 0.98952 | origa | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 0 | 63.436172 | origa | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 0 | 32.426007 | origa | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/masks | 455 | 0 | 0.692397 | origa | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/masks | 455 | 0 | 0.692397 | origa | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 0 | 67.969578 | origa | .png:113 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 0 | 58.332504 | origa | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/images | 98 | 0 | 13.673573 | origa | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/images | 98 | 0 | 7.404378 | origa | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/masks | 98 | 0 | 0.149886 | origa | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/masks | 98 | 0 | 0.149886 | origa | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/images | 97 | 0 | 13.488162 | origa | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/images | 97 | 0 | 6.778391 | origa | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/masks | 97 | 0 | 0.147237 | origa | .png:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/masks | 97 | 0 | 0.147237 | origa | .png:97 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 0 | 6.819179 | origa | .jpg:21 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations | 2 | 650 | 16.065817 | origa | .mat:650; .tif:2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA | 0 | 2 | 1.194704 | origa | .csv:2; .zip:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square_Boxed | 0 | 1 | 0.054888 | origa | .csv:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 0 | 499.794535 | fundus | .jpg:484 |

## Sponsor / Clinic / Head-Mounted Data Candidates

| directory | image_file_count | video_file_count | metadata_file_count | mask_label_file_count | total_size_mb | matched_sponsor_keywords | extension_counts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Square | 651 | 0 | 0 | 651 | 0.993426 | discview; uva | .png:651 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 0 | 0 | 650 | 465.651101 | discview; uva | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 0 | 0 | 650 | 182.675507 | discview; uva | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 0 | 0 | 650 | 90.597908 | discview | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 0 | 0 | 650 | 46.608776 | discview | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 0 | 0 | 650 | 46.608776 | discview | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 0 | 0 | 650 | 35.066236 | discview; uva | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 0 | 0 | 650 | 35.066236 | discview | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Images_Square | 650 | 0 | 0 | 650 | 35.066236 | discview | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 0 | 0 | 650 | 6.949396 | discview; uva | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 0 | 0 | 650 | 5.839859 | discview; uva | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 0 | 0 | 650 | 5.102674 | discview; uva | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 0 | 0 | 650 | 5.028817 | discview; uva | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Cropped | 650 | 0 | 0 | 650 | 1.641981 | discview; uva | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Masks_Square | 650 | 0 | 0 | 650 | 0.98952 | discview | .png:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Masks_Square | 650 | 0 | 0 | 650 | 0.98952 | discview | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 0 | 0 | 488 | 83.191399 | discview; uva | .jpg:488 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 0 | 0 | 484 | 499.794535 | discview; uva | .jpg:484 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 0 | 0 | 455 | 63.436172 | discview | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 0 | 0 | 455 | 32.426007 | discview | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/masks | 455 | 0 | 0 | 455 | 0.692397 | discview | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/masks | 455 | 0 | 0 | 455 | 0.692397 | discview | .png:455 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-3 | 215 | 0 | 0 | 215 | 153.447057 | clinic; discview; subject; uva | .png:215 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-2 | 208 | 0 | 0 | 208 | 140.022337 | clinic; discview; subject; uva | .png:208 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 0 | 0 | 113 | 67.969578 | clinic; discview; psd_clinic | .png:113 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 0 | 0 | 113 | 67.969578 | clinic | .png:113 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_image_masks | 113 | 0 | 0 | 113 | 0.303635 | clinic | .png:113 |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 0 | 0 | 109 | 58.332504 | discview | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 0 | 0 | 109 | 58.332504 | discview | .png:109 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 0 | 0 | 109 | 58.332504 | discview | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/images | 98 | 0 | 0 | 98 | 13.673573 | discview | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/images | 98 | 0 | 0 | 98 | 7.404378 | discview | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/masks | 98 | 0 | 0 | 98 | 0.149886 | discview | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/masks | 98 | 0 | 0 | 98 | 0.149886 | discview | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/images | 97 | 0 | 0 | 97 | 13.488162 | discview | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/images | 97 | 0 | 0 | 97 | 6.778391 | discview | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/masks | 97 | 0 | 0 | 97 | 0.147237 | discview | .png:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/masks | 97 | 0 | 0 | 97 | 0.147237 | discview | .png:97 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-1 | 74 | 0 | 0 | 74 | 69.521852 | clinic; discview; subject; uva | .png:74 |
| extracted_zips/Tien_DiscView/Test_Processed_Images/Test Preprocessed Images Data | 48 | 0 | 0 | 48 | 5.31279 | discview | .png:48 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-2 | 38 | 0 | 0 | 38 | 39.980389 | clinic; discview; subject; uva | .png:38 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 0 | 0 | 21 | 6.819179 | discview; uva | .jpg:21 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Videos | 0 | 2 | 0 | 0 | 642.237878 | clinic; discview; uva; video | .mp4:2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations | 2 | 0 | 650 | 652 | 16.065817 | discview; uva | .mat:650; .tif:2 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump | 1 | 0 | 0 | 1 | 302.866179 | discview | .ckpt:2; .jpg:1; .pth:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview | 1 | 0 | 1 | 2 | 260.15756 | discview | .py:9; .ckpt:2; .ipynb:1; .csv:1; .png:1; .sh:1; .bat:1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025 | 0 | 0 | 0 | 0 | 427.103208 | discview | .zip:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints | 0 | 0 | 0 | 0 | 259.47695 | discview | .ckpt:2 |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs | 0 | 0 | 0 | 0 | 23.860342 | discview | .pdf:4 |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt/UVA Health Frontiers in Clinical AI Symposium | 0 | 0 | 0 | 0 | 8.202491 | clinic; discview; uva | .pptx:2; .docx:1 |

_Showing top 50 of 66 rows._

## Candidate Image Directories

| directory | image_file_count | total_size_mb | likely_source | public_keyword_hits | sponsor_keyword_hits | extension_counts |
| --- | --- | --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Square | 651 | 0.993426 | sponsor_or_clinic | 1 | 2 | .png:651 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 465.651101 | sponsor_or_clinic | 1 | 2 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 182.675507 | sponsor_or_clinic | 1 | 2 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 46.608776 | sponsor_or_clinic | 0 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 35.066236 | sponsor_or_clinic | 1 | 2 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Images_Square | 650 | 35.066236 | sponsor_or_clinic | 0 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 6.949396 | sponsor_or_clinic | 1 | 2 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 5.839859 | sponsor_or_clinic | 1 | 2 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 5.102674 | sponsor_or_clinic | 1 | 2 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 5.028817 | sponsor_or_clinic | 1 | 2 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Cropped | 650 | 1.641981 | sponsor_or_clinic | 1 | 2 | .png:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Masks_Square | 650 | 0.98952 | sponsor_or_clinic | 0 | 1 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 83.191399 | sponsor_or_clinic | 0 | 2 | .jpg:488 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 499.794535 | sponsor_or_clinic | 1 | 2 | .jpg:484 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-3 | 215 | 153.447057 | sponsor_or_clinic | 0 | 4 | .png:215 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-2 | 208 | 140.022337 | sponsor_or_clinic | 0 | 4 | .png:208 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 67.969578 | sponsor_or_clinic | 1 | 3 | .png:113 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 67.969578 | sponsor_or_clinic | 0 | 1 | .png:113 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_image_masks | 113 | 0.303635 | sponsor_or_clinic | 0 | 1 | .png:113 |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 58.332504 | sponsor_or_clinic | 0 | 1 | .png:109 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 58.332504 | sponsor_or_clinic | 0 | 1 | .png:109 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-1 | 74 | 69.521852 | sponsor_or_clinic | 0 | 4 | .png:74 |
| extracted_zips/Tien_DiscView/Test_Processed_Images/Test Preprocessed Images Data | 48 | 5.31279 | sponsor_or_clinic | 0 | 1 | .png:48 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-2 | 38 | 39.980389 | sponsor_or_clinic | 0 | 4 | .png:38 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 6.819179 | sponsor_or_clinic | 1 | 2 | .jpg:21 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 90.597908 | uncertain | 1 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 46.608776 | uncertain | 1 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 35.066236 | uncertain | 1 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Masks_Square | 650 | 0.98952 | uncertain | 1 | 1 | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 63.436172 | uncertain | 1 | 1 | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 32.426007 | uncertain | 1 | 1 | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/masks | 455 | 0.692397 | uncertain | 1 | 1 | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/masks | 455 | 0.692397 | uncertain | 1 | 1 | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 58.332504 | uncertain | 1 | 1 | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/images | 98 | 13.673573 | uncertain | 1 | 1 | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/images | 98 | 7.404378 | uncertain | 1 | 1 | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/masks | 98 | 0.149886 | uncertain | 1 | 1 | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/masks | 98 | 0.149886 | uncertain | 1 | 1 | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/images | 97 | 13.488162 | uncertain | 1 | 1 | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/images | 97 | 6.778391 | uncertain | 1 | 1 | .jpg:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/masks | 97 | 0.147237 | uncertain | 1 | 1 | .png:97 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/masks | 97 | 0.147237 | uncertain | 1 | 1 | .png:97 |

## Candidate Mask / Label / Prediction Directories

| directory | file_count | image_file_count | mask_label_file_count | metadata_file_count | total_size_mb | mask_label_keyword_hits | extension_counts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 650 | 650 | 0 | 5.028817 | 5 | .png:650 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_image_masks | 113 | 113 | 113 | 0 | 0.303635 | 5 | .png:113 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 650 | 650 | 0 | 5.102674 | 4 | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/masks | 455 | 455 | 455 | 0 | 0.692397 | 4 | .png:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/masks | 98 | 98 | 98 | 0 | 0.149886 | 4 | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/masks | 97 | 97 | 97 | 0 | 0.147237 | 4 | .png:97 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations | 652 | 2 | 652 | 650 | 16.065817 | 3 | .mat:650; .tif:2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Square | 651 | 651 | 651 | 0 | 0.993426 | 3 | .png:651 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 650 | 650 | 0 | 90.597908 | 3 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 650 | 650 | 0 | 46.608776 | 3 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 650 | 650 | 0 | 46.608776 | 3 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 650 | 650 | 0 | 6.949396 | 3 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks_Cropped | 650 | 650 | 650 | 0 | 1.641981 | 3 | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Masks_Square | 650 | 650 | 650 | 0 | 0.98952 | 3 | .png:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Masks_Square | 650 | 650 | 650 | 0 | 0.98952 | 3 | .png:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/masks | 455 | 455 | 455 | 0 | 0.692397 | 3 | .png:455 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 113 | 113 | 0 | 67.969578 | 3 | .png:113 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/masks | 98 | 98 | 98 | 0 | 0.149886 | 3 | .png:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/masks | 97 | 97 | 97 | 0 | 0.147237 | 3 | .png:97 |
| extracted_zips/Tien_DiscView/Segmentation_Model/Segmentation_Model | 1 | 0 | 0 | 0 | 0.011416 | 3 | .docx:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours | 1952 | 0 | 1952 | 1952 | 1.007017 | 2 | .txt:1952 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 488 | 488 | 0 | 83.191399 | 2 | .jpg:488 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 455 | 455 | 0 | 63.436172 | 2 | .jpg:455 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 113 | 113 | 0 | 67.969578 | 2 | .png:113 |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 109 | 109 | 0 | 58.332504 | 2 | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 109 | 109 | 0 | 58.332504 | 2 | .png:109 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 109 | 109 | 0 | 58.332504 | 2 | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/images | 98 | 98 | 98 | 0 | 13.673573 | 2 | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/images | 97 | 97 | 97 | 0 | 13.488162 | 2 | .jpg:97 |
| extracted_zips/Tien_DiscView/Test_Processed_Images/Test Preprocessed Images Data | 48 | 48 | 48 | 0 | 5.31279 | 2 | .png:48 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/pngs | 4 | 4 | 4 | 0 | 2.158178 | 2 | .png:4 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label | 8 | 0 | 4 | 0 | 15.09928 | 2 | .psd:4; .py:4 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump | 4 | 1 | 1 | 0 | 302.866179 | 2 | .ckpt:2; .jpg:1; .pth:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square_Boxed | 1 | 0 | 1 | 1 | 0.054888 | 2 | .csv:1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/emd_gridsearch_thresholdparams | 3 | 0 | 0 | 0 | 0.004162 | 2 | .py:1; .log:1; .sh:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 650 | 650 | 0 | 465.651101 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 650 | 650 | 0 | 182.675507 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 650 | 650 | 0 | 35.066236 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 650 | 650 | 0 | 35.066236 | 1 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Images_Square | 650 | 650 | 650 | 0 | 35.066236 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 650 | 650 | 0 | 5.839859 | 1 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 484 | 484 | 0 | 499.794535 | 1 | .jpg:484 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 455 | 455 | 0 | 32.426007 | 1 | .jpg:455 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-3 | 215 | 215 | 215 | 0 | 153.447057 | 1 | .png:215 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-2 | 208 | 208 | 208 | 0 | 140.022337 | 1 | .png:208 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/images | 98 | 98 | 98 | 0 | 7.404378 | 1 | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/images | 97 | 97 | 97 | 0 | 6.778391 | 1 | .jpg:97 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-1 | 74 | 74 | 74 | 0 | 69.521852 | 1 | .png:74 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-2 | 38 | 38 | 38 | 0 | 39.980389 | 1 | .png:38 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 21 | 21 | 0 | 6.819179 | 1 | .jpg:21 |

_Showing top 50 of 68 rows._

## Group Split Clues

| relative_path | extension | matched_grouping_clues |
| --- | --- | --- |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0000 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0000 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0000.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0001 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0001 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0001 (3).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0001.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0002 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0002 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0002 (3).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0002.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0003 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0003 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0003 (3).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0003.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0004 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0004.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0005 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0005.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0006 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0006.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0007 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0007.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0008 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0008.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0009 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0009.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0010.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0011 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0011 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0011.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0012 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0012 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0012.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0013 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0013.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0014 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0014.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0015 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0015 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0015.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0016 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0016 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0016.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0017 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0017.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0018 (1).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0018 (2).png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0018.png | .png | frame_number |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data/frame_0019 (1).png | .png | frame_number |

_Showing top 50 of 16546 rows._

## Prior Baseline Directories

| directory | file_count | model_file_count | code_file_count | total_size_mb | baseline_keyword_hits | extension_counts |
| --- | --- | --- | --- | --- | --- | --- |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump | 4 | 3 | 0 | 302.866179 | 0 | .ckpt:2; .jpg:1; .pth:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview | 16 | 2 | 12 | 260.15756 | 0 | .py:9; .ckpt:2; .ipynb:1; .csv:1; .png:1; .sh:1; .bat:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints | 2 | 2 | 0 | 259.47695 | 3 | .ckpt:2 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/tensorboard/version_0 | 2 | 0 | 1 | 0.001073 | 1 | .0:1; .yaml:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/csv/version_0 | 2 | 0 | 1 | 0.000348 | 1 | .yaml:1; .csv:1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 0 | 0 | 6.819179 | 2 | .jpg:21 |
| extracted_zips/Tien_DiscView/Segmentation_Model/Segmentation_Model | 1 | 0 | 0 | 0.011416 | 1 | .docx:1 |

## Prior Baseline / Model Files

| relative_path | extension | size_mb | artifact_type | keyword_hits |
| --- | --- | --- | --- | --- |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints/model-epoch=01-val_loss=5.7846e-02.ckpt | .ckpt | 129.738718 | model_artifact | 4 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints/model-epoch=00-val_loss=5.9526e-02.ckpt | .ckpt | 129.738232 | model_artifact | 4 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model_state_dict.pth | .pth | 43.252275 | model_artifact | 2 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/model-epoch=406-val_loss=4.0005e-03.ckpt | .ckpt | 129.738975 | model_artifact | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/model-epoch=409-val_loss=4.0481e-03.ckpt | .ckpt | 129.738975 | model_artifact | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model-epoch=266-val_loss=4.0820e-03.ckpt | .ckpt | 129.738975 | model_artifact | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model-epoch=411-val_loss=7.2768e-03.ckpt | .ckpt | 129.738975 | model_artifact | 1 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_004-checkpoint.jpg | .jpg | 0.391918 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_100-checkpoint.jpg | .jpg | 0.390614 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_005-checkpoint.jpg | .jpg | 0.382889 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_025-checkpoint.jpg | .jpg | 0.379813 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_011-checkpoint.jpg | .jpg | 0.377788 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_016-checkpoint.jpg | .jpg | 0.368752 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_024-checkpoint.jpg | .jpg | 0.3481 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_017-checkpoint.jpg | .jpg | 0.345533 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_002-checkpoint.jpg | .jpg | 0.343183 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_001-checkpoint.jpg | .jpg | 0.337258 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_020-checkpoint.jpg | .jpg | 0.330503 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_019-checkpoint.jpg | .jpg | 0.329648 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_007-checkpoint.jpg | .jpg | 0.326254 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_021-checkpoint.jpg | .jpg | 0.317967 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_006-checkpoint.jpg | .jpg | 0.289833 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_003-checkpoint.jpg | .jpg | 0.28417 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_381-checkpoint.jpg | .jpg | 0.279286 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_009-checkpoint.jpg | .jpg | 0.266079 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_012-checkpoint.jpg | .jpg | 0.258072 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_335-checkpoint.jpg | .jpg | 0.236712 | mask_label_prediction_image | 2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints/glare_055-checkpoint.jpg | .jpg | 0.234806 | mask_label_prediction_image | 2 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/compare_trained_models_clean.py | .py | 0.007005 | code_or_config | 2 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/clinic_dataset_model_comparison.png | .png | 0.402631 | mask_label_prediction_image | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Interactive - test_trained_model.py.ipynb | .ipynb | 0.167791 | code_or_config | 1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/train_unet.py | .py | 0.02754 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/train_unet.py | .py | 0.02754 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/clinic_dataset_model_comparison.csv | .csv | 0.022923 | metadata_or_annotation | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/__pycache__/train_unet.cpython-310.pyc | .pyc | 0.011877 | other | 1 |
| extracted_zips/Tien_DiscView/Segmentation_Model/Segmentation_Model/model_training_brainstorming.docx | .docx | 0.011416 | document_or_log | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/test_trained_model.py | .py | 0.008607 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/__pycache__/unet.cpython-310.pyc | .pyc | 0.003926 | other | 1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/unet.py | .py | 0.003887 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/unet.py | .py | 0.003887 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/optuna_train_unet.sh | .sh | 0.001335 | code_or_config | 1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/optuna_train_unet.sh | .sh | 0.001255 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/tensorboard/version_0/events.out.tfevents.1757365751.DESKTOP-8C8AC91.22424.0 | .0 | 0.001062 | other | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/train_unet_windows.bat | .bat | 0.001008 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/csv/version_0/metrics.csv | .csv | 0.000338 | metadata_or_annotation | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/csv/version_0/hparams.yaml | .yaml | 1e-05 | code_or_config | 1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/tensorboard/version_0/hparams.yaml | .yaml | 1e-05 | code_or_config | 1 |

## Model Artifacts

| relative_path | extension | size_mb | artifact_type |
| --- | --- | --- | --- |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/model-epoch=406-val_loss=4.0005e-03.ckpt | .ckpt | 129.738975 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/model-epoch=409-val_loss=4.0481e-03.ckpt | .ckpt | 129.738975 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model-epoch=266-val_loss=4.0820e-03.ckpt | .ckpt | 129.738975 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model-epoch=411-val_loss=7.2768e-03.ckpt | .ckpt | 129.738975 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints/model-epoch=01-val_loss=5.7846e-02.ckpt | .ckpt | 129.738718 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints/model-epoch=00-val_loss=5.9526e-02.ckpt | .ckpt | 129.738232 | model_artifact |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump/model_state_dict.pth | .pth | 43.252275 | model_artifact |

## Code / Config Artifacts

| relative_path | extension | size_mb | artifact_type |
| --- | --- | --- | --- |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Interactive - test_trained_model.py.ipynb | .ipynb | 0.167791 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/train_unet.py | .py | 0.02754 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/train_unet.py | .py | 0.02754 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/compare_accuracy_labeled_clinic_images.py | .py | 0.02073 | code_or_config |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/create_save_images_masks_psd.py | .py | 0.009266 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/EMD_threshold_optimization.py | .py | 0.008956 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/test_trained_model.py | .py | 0.008607 | code_or_config |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/plots_png_masks.py | .py | 0.007671 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/compare_trained_models_clean.py | .py | 0.007005 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/EMD_threshold_optimization.py | .py | 0.00642 | code_or_config |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/selecting_bbox 1.py | .py | 0.005439 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/view_dataset_processing_masks.py | .py | 0.004894 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/unet.py | .py | 0.003887 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/unet.py | .py | 0.003887 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/emd_gridsearch_thresholdparams/emd_gridsearch.py | .py | 0.00326 | code_or_config |
| loose_files/make_folder_inventory.sh | .sh | 0.002416 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/after_emd_threshold_fitting.py | .py | 0.002303 | code_or_config |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/convert_to_png.py | .py | 0.001436 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/optuna_train_unet.sh | .sh | 0.001335 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/optuna_train_unet.sh | .sh | 0.001255 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/train_unet_windows.bat | .bat | 0.001008 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/adaptive_threshold_all_origa.py | .py | 0.000924 | code_or_config |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/plot_png.py | .py | 0.000826 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/run_threshold_origa.sh | .sh | 0.000622 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/run_EMD_optimization.sh | .sh | 0.000603 | code_or_config |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/emd_gridsearch_thresholdparams/run_gridsearch.sh | .sh | 0.00058 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/csv/version_0/hparams.yaml | .yaml | 1e-05 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/tensorboard/version_0/hparams.yaml | .yaml | 1e-05 | code_or_config |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/test_trained_net.py | .py | 0.0 | code_or_config |

## Video Artifacts

| relative_path | extension | size_mb | artifact_type |
| --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Videos/RPReplay_Final1743082598.MP4 | .mp4 | 443.343374 | video |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Videos/RPReplay_Final1743082848.MP4 | .mp4 | 198.894504 | video |

## Metadata / Annotation-Like Artifacts

| relative_path | extension | size_mb | artifact_type |
| --- | --- | --- | --- |
| loose_files/folder_inventory_20260513_121508.txt | .txt | 2.868279 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/origa_info.csv | .csv | 0.078492 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square_Boxed/bounding_boxes.csv | .csv | 0.054888 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/290.mat | .mat | 0.026065 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/225.mat | .mat | 0.026052 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/610.mat | .mat | 0.026027 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/177.mat | .mat | 0.026005 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/168.mat | .mat | 0.025999 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/591.mat | .mat | 0.025885 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/389.mat | .mat | 0.025868 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/625.mat | .mat | 0.025833 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/624.mat | .mat | 0.025828 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/103.mat | .mat | 0.025812 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/391.mat | .mat | 0.025812 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/646.mat | .mat | 0.02581 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/228.mat | .mat | 0.025803 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/643.mat | .mat | 0.025795 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/270.mat | .mat | 0.02579 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/058.mat | .mat | 0.025785 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/167.mat | .mat | 0.025775 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/197.mat | .mat | 0.025764 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/623.mat | .mat | 0.025717 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/609.mat | .mat | 0.025712 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/207.mat | .mat | 0.025688 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/403.mat | .mat | 0.025688 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/067.mat | .mat | 0.025652 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/066.mat | .mat | 0.025647 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/401.mat | .mat | 0.025638 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/626.mat | .mat | 0.025627 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/642.mat | .mat | 0.025607 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/206.mat | .mat | 0.025591 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/102.mat | .mat | 0.025565 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/593.mat | .mat | 0.025562 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/277.mat | .mat | 0.025545 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/375.mat | .mat | 0.025541 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/644.mat | .mat | 0.025532 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/017.mat | .mat | 0.025517 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/579.mat | .mat | 0.025512 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/632.mat | .mat | 0.025511 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/057.mat | .mat | 0.025493 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/239.mat | .mat | 0.025474 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/603.mat | .mat | 0.025465 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/176.mat | .mat | 0.02546 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/005.mat | .mat | 0.025441 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/227.mat | .mat | 0.025439 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/001.mat | .mat | 0.02543 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/064.mat | .mat | 0.025404 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/175.mat | .mat | 0.025399 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/390.mat | .mat | 0.025387 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/161.mat | .mat | 0.025386 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/323.mat | .mat | 0.025378 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/110.mat | .mat | 0.025375 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/645.mat | .mat | 0.025363 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/433.mat | .mat | 0.025353 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/097.mat | .mat | 0.02535 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/630.mat | .mat | 0.025341 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/580.mat | .mat | 0.025335 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/226.mat | .mat | 0.025331 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/221.mat | .mat | 0.025319 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations/588.mat | .mat | 0.025317 | metadata_or_annotation |

_Showing top 60 of 2620 rows._

## Document / Log Artifacts

| relative_path | extension | size_mb | artifact_type |
| --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs/G-RISK.pdf | .pdf | 15.589192 | document_or_log |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs/DS_Project_Writeup_Automation_of_Glaucoma_Screening.pdf | .pdf | 5.688745 | document_or_log |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt/UVA Health Frontiers in Clinical AI Symposium/Disc View Poster Draft.pptx | .pptx | 5.245013 | document_or_log |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt/UVA Health Frontiers in Clinical AI Symposium/Disc View Poster Final.pptx | .pptx | 2.935963 | document_or_log |
| loose_files/folder_inventory_20260513_121508.txt | .txt | 2.868279 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs/Automated_Glaucoma_Detection_Review.pdf | .pdf | 1.531343 | document_or_log |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs/DDLSNet.pdf | .pdf | 1.051062 | document_or_log |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Assignment Papers/4-11 Progress Report.docx | .docx | 0.675312 | document_or_log |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Assignment Papers/2-28 Progress Report.docx | .docx | 0.480757 | document_or_log |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Assignment Papers/Final Capstone Project Proposal.docx | .docx | 0.022079 | document_or_log |
| loose_files/Tien_DiscView/Weekly_agenda.docx | .docx | 0.021917 | document_or_log |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt/UVA Health Frontiers in Clinical AI Symposium/AI Symposium Poster Outline.docx | .docx | 0.021515 | document_or_log |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ClinicalData/patient_data_os.xlsx | .xlsx | 0.018061 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ClinicalData/patient_data_od.xlsx | .xlsx | 0.017976 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/web_application/web_application/discview_project_specification.docx | .docx | 0.017615 | document_or_log |
| loose_files/Tien_DiscView/Lit Review Annotated Bibliography.docx | .docx | 0.017246 | document_or_log |
| extracted_zips/Tien_DiscView/Segmentation_Model/Segmentation_Model/model_training_brainstorming.docx | .docx | 0.011416 | document_or_log |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Assignment Papers/SEIDS Abstract_.docx | .docx | 0.00712 | document_or_log |
| loose_files/FILE_LOG.txt | .txt | 0.005489 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/___All_Errors.txt | .txt | 0.003364 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET002OD_disc_exp2.txt | .txt | 0.00236 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET006OS_disc_exp2.txt | .txt | 0.001385 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET008OD_disc_exp2.txt | .txt | 0.001385 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET008OS_disc_exp2.txt | .txt | 0.001322 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET005OS_disc_exp2.txt | .txt | 0.00129 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET002OS_disc_exp2.txt | .txt | 0.001259 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET004OD_disc_exp2.txt | .txt | 0.001259 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET026OD_disc_exp2.txt | .txt | 0.001259 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET028OS_disc_exp2.txt | .txt | 0.001227 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET005OD_cup_exp2.txt | .txt | 0.001196 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET005OD_disc_exp2.txt | .txt | 0.001196 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET006OD_disc_exp2.txt | .txt | 0.001196 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET013OD_disc_exp2.txt | .txt | 0.001196 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET010OS_cup_exp2.txt | .txt | 0.001164 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET147OD_disc_exp1.txt | .txt | 0.001164 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET007OS_disc_exp2.txt | .txt | 0.001133 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET009OD_disc_exp2.txt | .txt | 0.001101 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET010OS_disc_exp2.txt | .txt | 0.001101 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET014OD_cup_exp2.txt | .txt | 0.001101 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET129OD_disc_exp1.txt | .txt | 0.001101 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET189OS_disc_exp1.txt | .txt | 0.001101 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET023OD_disc_exp2.txt | .txt | 0.00107 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET035OS_disc_exp2.txt | .txt | 0.00107 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET190OS_disc_exp1.txt | .txt | 0.00107 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET004OS_disc_exp2.txt | .txt | 0.001039 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET030OD_disc_exp2.txt | .txt | 0.001039 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET038OS_disc_exp2.txt | .txt | 0.001039 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET006OD_cup_exp2.txt | .txt | 0.001007 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET007OD_disc_exp2.txt | .txt | 0.001007 | metadata_or_annotation |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/Contours/RET010OD_disc_exp2.txt | .txt | 0.001007 | metadata_or_annotation |

_Showing top 50 of 1975 rows._

## Largest Directories

| directory | file_count | total_size_mb | image_file_count | extension_counts |
| --- | --- | --- | --- | --- |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Videos | 2 | 642.237878 | 0 | .mp4:2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/FundusImages | 484 | 499.794535 | 484 | .jpg:484 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images | 650 | 465.651101 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025 | 1 | 427.103208 | 0 | .zip:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/testing_doc_dump | 4 | 302.866179 | 1 | .ckpt:2; .jpg:1; .pth:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview | 16 | 260.15756 | 1 | .py:9; .ckpt:2; .ipynb:1; .csv:1; .png:1; .sh:1; .bat:1 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/training_logs_15_4/checkpoints | 2 | 259.47695 | 0 | .ckpt:2 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare | 650 | 182.675507 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-3 | 215 | 153.447057 | 215 | .png:215 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject-2 | 208 | 140.022337 | 208 | .png:208 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square | 650 | 90.597908 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Papila/ExpertsSegmentations/ImagesWithContours | 488 | 83.191399 | 488 | .jpg:488 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-1 | 74 | 69.521852 | 74 | .png:74 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/psd_clinic_images_png | 113 | 67.969578 | 113 | .png:113 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label/processed_pngs/clinic_images | 113 | 67.969578 | 113 | .png:113 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/train/images | 455 | 63.436172 | 455 | .jpg:455 |
| extracted_zips/Tien_DiscView/Test_Non_Processed_Images/Test Non-processed Images Data | 109 | 58.332504 | 109 | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Test Non-processed Images Data | 109 | 58.332504 | 109 | .png:109 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Test Non-processed Images Data | 109 | 58.332504 | 109 | .png:109 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Thresholded_Images_Square_15_4 | 650 | 46.608776 | 650 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Thresholded_Images_Square_15_4 | 650 | 46.608776 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/Clinic/Subject 1 CD-2 | 38 | 39.980389 | 38 | .png:38 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Square | 650 | 35.066236 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/Images_Square | 650 | 35.066236 | 650 | .jpg:650 |
| extracted_zips/rivanna_train_discview/rivanna_train_discview/Images_Square | 650 | 35.066236 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/train/images | 455 | 32.426007 | 455 | .jpg:455 |
| extracted_zips/Tien_DiscView/paper_pdfs/paper_pdfs | 4 | 23.860342 | 0 | .pdf:4 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Semi-automatic-annotations | 652 | 16.065817 | 2 | .mat:650; .tif:2 |
| extracted_zips/convert_psd_to_label/convert_psd_to_label | 8 | 15.09928 | 0 | .psd:4; .py:4 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/test/images | 98 | 13.673573 | 98 | .jpg:98 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/oldthreshold_mistake_training_split/val/images | 97 | 13.488162 | 97 | .jpg:97 |
| extracted_zips/Tien_DiscView/UVA_Health_Frontiers_Symp_ppt/UVA Health Frontiers in Clinical AI Symposium | 3 | 8.202491 | 0 | .pptx:2; .docx:1 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/test/images | 98 | 7.404378 | 98 | .jpg:98 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Masks | 650 | 6.949396 | 650 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Glare/.ipynb_checkpoints | 21 | 6.819179 | 21 | .jpg:21 |
| extracted_zips/Tien_DiscView/rivanna_origa_train_backup_10082025/rivanna_origa_train_backup_10082025/automated_screening/ORIGA/training_split/val/images | 97 | 6.778391 | 97 | .jpg:97 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Images_Cropped | 650 | 5.839859 | 650 | .jpg:650 |
| extracted_zips/Tien_DiscView/Test_Processed_Images/Test Preprocessed Images Data | 48 | 5.31279 | 48 | .png:48 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Disc | 650 | 5.102674 | 650 | .png:650 |
| extracted_zips/Tien_DiscView/Tien_MSDS_Google_Drive/MSDS Google Drive/UVA Capstone/Data Sets/ORIGA/Predictions/Cup | 650 | 5.028817 | 650 | .png:650 |

_Showing top 40 of 69 rows._

## Recommended Next Manual Steps

1. Confirm which ORIGA/public folders contain raw images and ground-truth masks.
2. Confirm which clinic folders contain Dr. D / Tien head-mounted frames.
3. Pair sponsor images with masks, PSD-derived labels, bounding boxes, or clinician labels.
4. Decide grouping variables for sponsor splits: patient, video, eye, and/or frame sequence.
5. Create a cleaned manifest under `data/processed/manifests/`, not by moving raw files.
6. Reproduce or evaluate prior U-Net checkpoints only after the image/mask map is verified.
7. Use public and sponsor holdouts separately; sponsor holdout should be the headline generalization metric.

## Notes

- This audit is heuristic. It narrows the manual search space but does not prove label correctness.
- `data/raw/` should remain ignored by Git. Review summary reports before committing them.
- Do not create train/validation/test splits by random frame alone if patient/video/eye grouping is recoverable.
