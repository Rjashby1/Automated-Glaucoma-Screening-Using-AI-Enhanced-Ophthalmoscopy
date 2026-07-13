# Final Project Interpretation

The final project arc supports a clear conclusion: the public-data segmentation pipeline became strong on held-out public data, but public performance alone did not solve clinical/head-mounted transfer.

The selected public-data model from Notebook 07 achieved a public test mean foreground Dice of 0.817976. Longer public-data training with the selected combined augmentation recipe improved this to 0.842136 in Notebook 10. The hybrid public-clinical model in Notebook 13 preserved strong public performance with a public test mean foreground Dice of 0.843930.

Clinical transfer remained the central difficulty. In pure clinical generalization, the long public-trained model reached a patient-weighted clinical mean foreground Dice of 0.250879, far below its public test performance. Notebook 12 showed that clinical-only fine-tuning on very small PSD-derived subsets was unstable and did not reliably improve held-out patient-weighted performance.

Notebook 13 produced the strongest clinical-domain result. Adding 50% of clinical patient/encounter groups into the public training pool before virtual synthetic expansion improved held-out patient-weighted clinical mean foreground Dice by 0.065245 relative to the internal zero-shot Notebook 10 baseline and improved patient-weighted CDR absolute error by 0.122274. This suggests that hybrid training can use clinical-domain signal more effectively than tiny clinical-only fine-tuning.

The result remains exploratory. The clinical subset is small, the masks are approximate PSD-derived labels, and individual-image performance remains uneven. The model is not clinically deployable. The next research step is larger patient-group clinical annotation, more robust domain adaptation, and prospective validation with clinical review.