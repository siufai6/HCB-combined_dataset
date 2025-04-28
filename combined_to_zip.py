import pandas as pd

## this script maps LSOA 2021 codes to postcodes using a mapping file and performs various checks on the data integrity.
## mapping file -> https://geoportal.statistics.gov.uk/datasets/c7debafcef564e7a9dfb8ca881be4253/about
## the combined_losa_data.csv file is created by combine_all_sourcedata.py script

# Load the zipcode and data files
zipcode_file = './lsoa 2021/lsoa21zipcode.csv'  # mapping file available on https://geoportal.statistics.gov.uk/datasets/c7debafcef564e7a9dfb8ca881be4253/about
data_file = 'combined_lsoa_data.csv'        # Replace with your data file path

zipcode_df = pd.read_csv(zipcode_file)
data_df = pd.read_csv(data_file)

data_df=data_df.round(2)


# Check 1: Input Data Integrity
print("Checking Input Data Integrity...")
# Check for missing values in critical columns
if data_df['LSOA21CD'].isna().any():
    print("Warning: Missing LSOA21CD values in data file")
if zipcode_df['lsoa21'].isna().any():
    print("Warning: Missing lsoa21 values in zipcode file")
if zipcode_df['pcds'].isna().any():
    print("Warning: Missing pcds values in zipcode file")

# Check for duplicates in LSOA21CD
duplicates = data_df['LSOA21CD'].duplicated().sum()
if duplicates > 0:
    print(f"Warning: Found {duplicates} duplicate LSOA21CD values in data file")

# Check if score is numeric
if not pd.api.types.is_numeric_dtype(data_df['score']):
    print("Error: 'score' column is not numeric")
    exit()

# Check 2: Sorting and Filtering
print("\nChecking Sorting and Filtering...")
# Sort by score in descending order and take top 50
top_50_df = data_df.sort_values(by='score', ascending=False).head(50)

# Verify sorting
if not top_50_df['score'].is_monotonic_decreasing:
    print("Warning: Top 50 records are not sorted in descending order by score")

# Verify number of records
num_records = len(top_50_df)
print(f"Number of records in top 50: {num_records}")
if num_records > 50:
    print("Error: More than 50 records selected")
elif num_records < 50:
    print("Warning: Fewer than 50 records available in data file")

# Check 3: Perform the Mapping
print("\nPerforming Mapping...")
merged_df = pd.merge(
    top_50_df,
    zipcode_df[['lsoa21', 'pcds']],
    left_on='LSOA21CD',
    right_on='lsoa21',
    how='left'
)

# Drop redundant lsoa21 column
merged_df = merged_df.drop(columns=['lsoa21'])


# Verify pcds values exist in zipcode file
invalid_pcds = merged_df[~merged_df['pcds'].isna() & ~merged_df['pcds'].isin(zipcode_df['pcds'])]
if not invalid_pcds.empty:
    print("Error: Found pcds values in merged dataset not present in zipcode file")

# Check 4: Unmapped LSOA21CD Codes
unmapped_lsoa = merged_df[merged_df['pcds'].isna()]['LSOA21CD'].unique()
unmapped_count = len(unmapped_lsoa)
unmapped_percentage = (unmapped_count / num_records) * 100
print(f"\nLSOA21CD codes that could not be mapped to a postcode: {unmapped_count}")
print(f"Percentage of unmapped LSOA21CD codes: {unmapped_percentage:.2f}%")
if unmapped_count > 0:
    print("Unmapped LSOA21CD codes:")
    for lsoa in unmapped_lsoa:
        print(lsoa)
else:
    print("All LSOA21CD codes were successfully mapped to postcodes.")

# Check 5: LSOA21CD Consistency
if not merged_df['LSOA21CD'].isin(top_50_df['LSOA21CD']).all():
    print("Error: Some LSOA21CD values in merged dataset do not match top 50 input")

# Check 6: Unexpected NaN Values
print("\nChecking for unexpected NaN values...")
nan_columns = merged_df.drop(columns=['pcds']).isna().any()
if nan_columns.any():
    print("Warning: NaN values found in the following columns (excluding pcds):")
    print(nan_columns[nan_columns].index.tolist())

# Output Results
print("\nMerged Dataset (First 5 rows):")
print(merged_df.head())

# Save the merged dataset
merged_df.to_csv('mapped_lsoa_to_postcode_top50.csv', index=False)
print("\nMerged dataset saved to 'mapped_lsoa_to_postcode_top50.csv'")

# Optional: Spot-check a few mappings
print("\nSpot-checking mappings (first 3 mapped records):")
mapped_records = merged_df[~merged_df['pcds'].isna()][['LSOA21CD', 'pcds']].head(3)
if not mapped_records.empty:
    for _, row in mapped_records.iterrows():
        lsoa = row['LSOA21CD']
        pcd = row['pcds']
        # Verify in original zipcode file
        if zipcode_df[(zipcode_df['lsoa21'] == lsoa) & (zipcode_df['pcds'] == pcd)].empty:
            print(f"Error: Mapping {lsoa} -> {pcd} not found in zipcode file")
        else:
            print(f"Verified: {lsoa} -> {pcd}")
else:
    print("No mapped records to spot-check")


