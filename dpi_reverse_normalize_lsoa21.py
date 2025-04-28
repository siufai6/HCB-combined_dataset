import pandas as pd

# this reads the DPI file and maps it to LSOA 2021 codes, normalize the scores to a range of 0 to 10
# note that in the original data file is score is in the range of 0 to 100, while 100 is the best score
# in order to combine with other datasets, we need to invert the score, i.e. 100 in the original data is 0 in the normalized data
# 
# DPI file source: https://www.ons.gov.uk/peoplepopulationandcommunity/householdcharacteristics/homeinternetandsocialmediausage/datasets/digitalpropensityindexforcensus2021atlowerlayersuperoutputareaslsoasenglandandwales
# LSOA 2021 mapping file source: https://www.data.gov.uk/dataset/03a52a27-36e7-4f33-a632-83282faea36f/lsoa-2011-to-lsoa-2021-to-local-authority-district-2022-exact-fit-lookup-for-ew-v3
# 
# the results would be used to combine with other datasets to create a combined score for analysis


def normalize_to_range(x, new_min=0, new_max=10):
    """
    normalized data into rnage 0 to 10
    """
    x_min, x_max = x.min(), x.max()
    return ((x_max - x) / (x_max - x_min)) * (new_max - new_min) + new_min


print("--- reading DPI file")
data_df = pd.read_csv("./digitalpropensityindexlsoasv3.csv")

data_df['score_normalized'] = normalize_to_range(data_df.Score)

# Round the normalized scores to 2 decimal places
data_df['score_normalized'] = data_df['score_normalized'].round(2)


# DPI is LSOA 2011 data
# need to  map to LSOA 2021.
LSOA11_TO_21_MAPPING="./LSOA_(2011)_to_LSOA_(2021)_to_Local_Authority_District_(2022)_Lookup_for_England_and_Wales.csv"

mapping_df = pd.read_csv(LSOA11_TO_21_MAPPING,encoding='ISO-8859-1') 
mapping_df.rename(columns={mapping_df.columns[0]: 'LSOAcode'}, inplace=True)

# Check 1: Input Data Integrity
print("Checking Input Data Integrity...")
# Check for missing LSOAcode in data file
if mapping_df['LSOAcode'].isna().any():
    print("Warning: Missing LSOAcode values in mapping file")
if data_df['LSOAcode'].isna().any():
    print("Warning: Missing LSOAcode values in data file")

# Check for duplicate LSOAcode in data file
duplicates_data = data_df['LSOAcode'].duplicated().sum()
if duplicates_data > 0:
    print(f"Warning: Found {duplicates_data} duplicate LSOAcode values in data file")

# Check 2: Mapping File Integrity
print("\nChecking Mapping File Integrity...")
# Check for missing values in mapping file
if mapping_df['LSOAcode'].isna().any():
    print("Warning: Missing LSOAcode values in mapping file")
if mapping_df['LSOA21CD'].isna().any():
    print("Warning: Missing LSOA21CD values in mapping file")

# Check for duplicate LSOAcode in mapping file
duplicates_mapping = mapping_df['LSOAcode'].duplicated().sum()
if duplicates_mapping > 0:
    print(f"Error: Found {duplicates_mapping} duplicate LSOAcode values in mapping file. Each LSOAcode should map to one LSOA21CD.")

mapping_df=mapping_df[['LSOAcode', 'LSOA21CD','LSOA21NM']]


# Check 3: Perform the Mapping  
print("\nPerforming Mapping...")
merged_df = pd.merge(
    data_df,
    mapping_df[['LSOAcode', 'LSOA21CD']],
    on='LSOAcode',
    how='left'
)

print("\nHandling Many-to-One Mappings (Keeping Highest Score)...")
# Sort by LSOA21CD and score (descending) and drop duplicates, keeping the first (highest score)
deduped_df = merged_df.sort_values(['LSOA21CD', 'score_normalized'], ascending=[True, False])\
                      .drop_duplicates(subset=['LSOA21CD'], keep='first')


# Check 4: Merge Validation
print("\nChecking Merge Results...")
# Verify number of records
if len(deduped_df) != len(data_df):
    print(f"Error: Merged dataset has {len(deduped_df)} records, expected {len(data_df)}")


# Verify LSOA21CD values exist in mapping file
invalid_lsoa21 = deduped_df[~deduped_df['LSOA21CD'].isna() & ~deduped_df['LSOA21CD'].isin(mapping_df['LSOA21CD'])]

if not invalid_lsoa21.empty:
    print("Error: Found LSOA21CD values in merged dataset not present in mapping file")

# Check 5: Unmapped LSOAcode Codes
unmapped_lsoa = deduped_df[deduped_df['LSOA21CD'].isna()]['LSOAcode'].unique()
unmapped_count = len(unmapped_lsoa)
unmapped_percentage = (unmapped_count / len(data_df)) * 100
print(f"\nLSOAcode codes that could not be mapped to LSOA21CD: {unmapped_count}")
print(f"Percentage of unmapped LSOAcode codes: {unmapped_percentage:.2f}%")
if unmapped_count > 0:
    print("Unmapped LSOAcode codes:")
    for lsoa in unmapped_lsoa:
        print(lsoa)
else:
    print("All LSOAcode codes were successfully mapped to LSOA21CD.")

# Check 6: Many-to-One Mappings
print("\nChecking for Many-to-One Mappings...")
lsoa21_counts = mapping_df.groupby('LSOA21CD')['LSOAcode'].nunique()
many_to_one = lsoa21_counts[lsoa21_counts > 1]
if not many_to_one.empty:
    print("Found LSOA21CD codes with multiple LSOAcode mappings:")
    for lsoa21, count in many_to_one.items():
        lsoa11_list = mapping_df[mapping_df['LSOA21CD'] == lsoa21]['LSOAcode'].tolist()
        print(f"LSOA21CD {lsoa21}: {count} LSOAcode codes -> {lsoa11_list}")
else:
    print("No many-to-one mappings found.")

# Check 7: Sanity Check - Spot-Check Mappings
print("\nSpot-checking mappings (first 3 mapped records):")
mapped_records = deduped_df[~deduped_df['LSOA21CD'].isna()][['LSOAcode', 'LSOA21CD']].head(3)
if not mapped_records.empty:
    for _, row in mapped_records.iterrows():
        lsoa11 = row['LSOAcode']
        lsoa21 = row['LSOA21CD']
        # Verify in original mapping file
        if mapping_df[(mapping_df['LSOAcode'] == lsoa11) & (mapping_df['LSOA21CD'] == lsoa21)].empty:
            print(f"Error: Mapping {lsoa11} -> {lsoa21} not found in mapping file")
        else:
            print(f"Verified: {lsoa11} -> {lsoa21}")
else:
    print("No mapped records to spot-check")

# Output Results
print("\nMerged Dataset (First 5 rows):")
print(deduped_df.head())

# Save the merged dataset
deduped_df.to_csv('mapped_lsoa11_to_lsoa21.csv', index=False)
print("\nMerged dataset saved to 'mapped_lsoa11_to_lsoa21.csv'")


