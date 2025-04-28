# combined_dataset
Combining multiple data source into 1 dataset for identifying areas that are more likely to be in proverty.

## The dpi_reverse_normalize_lsoa21.py
- take the DPI data (https://www.ons.gov.uk/peoplepopulationandcommunity/householdcharacteristics/homeinternetandsocialmediausage/datasets/digitalpropensityindexforcensus2021atlowerlayersuperoutputareaslsoasenglandandwales), normalize the scores to a range of 0 to 10. Note that in the original data file is score is in the range of 0 to 100, while 100 is the best score in order to combine with other datasets, we need to invert the score, i.e. 100 in the original data is 0 in the normalized data.  
- the DPI data is based on 2011 LSOA. So we used the mapping file LSOA 2021 mapping file (https://www.data.gov.uk/dataset/03a52a27-36e7-4f33-a632-83282faea36f/lsoa-2011-to-lsoa-2021-to-local-authority-district-2022-exact-fit-lookup-for-ew-v3) to convert the LSOA to 2021

## combined_all_sourcedata.py
- combines all source data into a single file.

## combined_to_zip.py
- sort the score in the combined csv for the top 50 with the highest score i.e. need most attention
- map the LSOA to find out the postal codes, mapping file is https://geoportal.statistics.gov.uk/datasets/c7debafcef564e7a9dfb8ca881be4253/about

The result is poverty_factors_lsoa_to_postcode_top50.csv which lists postal codes of areas that are more vulnerable to poverty.
## how to read the csv
1. LSOA21CD - lsoa code
2. Local Authority name
3. dpi normalized - normalized DPI score, higher score meaning less likely people have access/would use internet/digital services.
4. Pct of population speaks no or little English normalized - normalized score of population speaks little or no English. higher score meaning less people speaks English.
5. Pct unemployed or econ inactive normalized - normalized score of population without a job or economically inactive. higher score meaning less or no employment.
6. Pct household deprivation normalized - normalized score of household deprivation. higher score meaning the households are deprived in multiple dimensions (among health, employment, education, housing)
7. score - the total of of the 4 factors above.
8. LSOA21 Names9. pcds - full postal code.

