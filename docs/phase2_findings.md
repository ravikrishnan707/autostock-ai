
# Phase 2 - Data Analysis and Feature Engineering

## Dataset
- Source: Kaggle High-Dimensional Supply Chain Inventory Dataset
- Records: 91,250
- Original columns: 15
- Dataset type: Synthetic supply-chain data

## Data preparation
- Checked missing values, duplicate records, and numeric values.
- Created a cleaned dataset.
- Added calendar and inventory-status features.
- Created previous-day sales and rolling demand features.

## Baseline comparison

| Method | MAE | RMSE |
|---|---:|---:|
| Previous day's sales | 5.923 | 7.476 |
| Previous 7-day average | 4.479 | 5.653 |

## Finding
The previous 7-day average performed better than the
previous-day-sales baseline on the evaluated test records.

## Limitation
Stockout_Flag is zero for every record, so this dataset
cannot train a meaningful stockout classifier using that label.

## Next steps
- Review feature quality and time-based evaluation.
- Test a more advanced demand forecasting model.
- Keep stockout prediction separate until suitable target labels
  are available.



### Final Baseline Evaluation

- Dataset: Kaggle High-Dimensional Supply Chain Inventory Dataset.
- Test period: 2024-10-19 to 2024-12-30.
- Eligible test rows: 18,250.
- Previous-day sales MAE: 5.923.
- Previous 7-day average MAE: 4.479.
- Previous 7-day average RMSE: 5.653.
- The 7-day average performed better than the previous-day baseline on this test set.
- Limitation: `Stockout_Flag` is zero for every row, so this dataset cannot train a useful stockout classifier using that label.
