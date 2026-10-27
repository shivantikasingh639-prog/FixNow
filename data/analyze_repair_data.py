import pandas as pd
from pathlib import Path

# ================= FIXNOW DATA DIRECTORY =================

DATA_DIR = Path(__file__).parent

FILES = {
    "EEE": "OpenRepairData_v0.3_aggregate_202607_eee.csv",
    "Non-EEE": "OpenRepairData_v0.3_aggregate_202607_non-eee.csv",
}

summary_rows = []
status_rows = []

# ================= ANALYSE DATASETS =================

for dataset_name, filename in FILES.items():

    file_path = DATA_DIR / filename

    if not file_path.exists():
        print(f"\nERROR: Dataset file not found: {file_path}")
        continue

    print(f"\nAnalysing dataset: {dataset_name}")
    print(f"File: {filename}")

    total_records = 0
    missing_problem = 0
    status_counts = {}

    # Read large CSV files in chunks
    for chunk in pd.read_csv(file_path, chunksize=10000):

        total_records += len(chunk)

        # Count missing problem descriptions
        if "problem" in chunk.columns:
            missing_problem += int(chunk["problem"].isna().sum())

        # Count repair statuses
        if "repair_status" in chunk.columns:

            counts = chunk["repair_status"].fillna(
                "Unknown"
            ).value_counts()

            for status, count in counts.items():
                status_counts[status] = (
                    status_counts.get(status, 0) + int(count)
                )

    # Save dataset summary
    summary_rows.append({
        "dataset": dataset_name,
        "file_name": filename,
        "total_records": total_records,
        "missing_problem_descriptions": missing_problem,
    })

    # Save repair status summary
    for status, count in status_counts.items():

        status_rows.append({
            "dataset": dataset_name,
            "repair_status": status,
            "record_count": count,
        })

# ================= GENERATE REPORTS =================

summary_df = pd.DataFrame(summary_rows)
status_df = pd.DataFrame(status_rows)

summary_path = DATA_DIR / "repair_data_summary.csv"
status_path = DATA_DIR / "repair_status_summary.csv"

summary_df.to_csv(summary_path, index=False)
status_df.to_csv(status_path, index=False)

# ================= DISPLAY RESULTS =================

print("\n========== DATASET SUMMARY ==========")

if not summary_df.empty:
    print(summary_df.to_string(index=False))
else:
    print("No dataset summaries were generated.")

print("\n========== REPAIR STATUS SUMMARY ==========")

if not status_df.empty:
    print(status_df.to_string(index=False))
else:
    print("No repair status data was generated.")

print("\nReports saved:")

print(summary_path)
print(status_path)

print("\nDataset analysis completed.")