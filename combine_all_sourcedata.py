import pandas as pd

# combine all sourcedata into a single file and aggregate the score 
# this file can be used to create maps to show how each LSOA is doing in terms of the factors
# or to sort and map to zip code for other analysis or for identifying areas that may need more help.
# 

# List of file paths
files = ["../dpi/dpi lsoa 2021 reverse_normalized.csv", "../language/nomis_language_proficiency_lsoa.csv", "../employment/nomis_employment_lsoa_normalized.csv","../household deprev/nomis_household_depriv_normalized.csv"]
files = ["../dpi/mapped_lsoa11_to_lsoa21.csv", "../language/nomis_language_proficiency_lsoa.csv", "../employment/nomis_employment_lsoa_normalized.csv","../household deprev/nomis_household_depriv_normalized.csv"]

# Load all datasets into a list of DataFrames with LSOA Code as index
dfs = [pd.read_csv(file) for file in files]

dfs[0] = dfs[0].loc[dfs[0].groupby('LSOA21CD')['score_normalized'].idxmax()]
print(len(dfs))
for d in dfs:
    
    d.rename(columns={"geography code": "LSOA21CD"}, inplace=True) if "geography code" in d.columns else None
    d.set_index("LSOA21CD", inplace=True)

print(dfs[3].head(5))

combined_df = None

for df in dfs:
    if combined_df is None: combined_df = df
    else:
        combined_df = combined_df.join(df, how="inner", lsuffix='_left', rsuffix='_right')

combined_df.rename(columns={"score_normalized":"dpi normalized","Pct normalized":"Pct unemployed or econ inactive normalized"}, inplace=True)

# Check the result
combined_df['score']= combined_df['dpi normalized']+combined_df['Pct of population speaks no or little English normalized']+combined_df['Pct household deprivation normalized']+combined_df['Pct unemployed or econ inactive normalized']
combined_df = combined_df[['Local Authority name','dpi normalized','Pct of population speaks no or little English normalized','Pct unemployed or econ inactive normalized','Pct household deprivation normalized','score','LSOA21 Name']]

combined_df = combined_df.round(2)
print(combined_df.head())

# Save to a new file
combined_df.to_csv("combined_lsoa_data.csv")