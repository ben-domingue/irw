import pandas as pd

## Import data
df1 = pd.read_csv('fullData.csv')

## Select 122 columns to keep
columns_to_keep = [
    "MBPS_1", "MBPS_2", "MBPS_3", "MBPS_4", "MBPS_5", "MBPS_6", "MBPS_7", "MBPS_8", "MBPS_9", "MBPS_10", 
    "MBSP_11", "MBPS_12", "MBPS_13", "MBPS_14", 
    "AFPS_1", "AFPS_2", "AFPS_3", "AFPS_4", "AFPS_5", "AFPS_6", "AFPS_7", "AFPS_8", "AFPS_9", 
    "GPS_1", "GPS_2", "GPS_3", "GPS_4", "GPS_5", "GPS_6", "GPS_7", "GPS_8", "GPS_9", "GPS_10", 
    "GPS_11", "GPS_12", "GPS_13", "GPS_14", "GPS_15", "GPS_16", 
    "AIP_1", "AIP_2", "AIP_3", "AIP_4", "AIP_5", "AIP_6", "AIP_7", "AIP_8", "AIP_9", "AIP_10", "AIP_11", 
    "APS_1", "APS_2", "APS_3", "APS_4", "APS_5", "APS_6", "APS_7", "APS_8", "APS_9", "APS_10", 
    "APS_11", "APS_12", "APS_13", "APS_14", "APS_15", "APS_16", 
    "UPS_1", "UPS_2", "UPS_3", "UPS_4", "UPS_5", "UPS_6", "UPS_7", 
    "PASS_1", "PASS_2", "PASS_3", "PASS_4", "PASS_5", "PASS_6", "PASS_7", "PASS_8", "PASS_9", "PASS_10", 
    "PASS_11", "PASS_12", 
    "IPS_1", "IPS_2", "IPS_3", "IPS_4", "IPS_5", "IPS_6", "IPS_7", "IPS_8", "IPS_9", 
    "PPS_1", "PPS_2", "PPS_3", "PPS_4", "PPS_5", "PPS_6", "PPS_7", "PPS_8", "PPS_9", "PPS_10", 
    "PPS_11", "PPS_12", 
    "TPI_1", "TPI_2", "TPI_3", "TPI_4", "TPI_5", "TPI_6", "TPI_7", "TPI_8", "TPI_9", "TPI_10", 
    "TPI_11", "TPI_12", "TPI_13", "TPI_14", "TPI_15", "TPI_16"
]

df1_filtered = df1[columns_to_keep]
df1_filtered.shape      ## 242 rows × 122 columns
df2 = df1_filtered.copy()

## Check data type
df2.dtypes

##Start Convert Vector Here
new_data = []

for index, row in df2.iterrows():
    for column in df2.columns:
        new_data.append([index + 1, column, row[column]])  

output = pd.DataFrame(new_data, columns=['id', 'item', 'resp'])
output    ## 29524 rows x 3 columns

## Check and remove Null
null_counts = output.isnull().sum()
null_counts   ## 1253 null values.

## Remove Null
output_cleaned = output.dropna()
output_cleaned.shape    ## 28271 rows, 3 columns: 1253 records removed.

prefixes = ["MBPS", "AFPS", "GPS", "AIP", "APS", "UPS", "PASS", "IPS", "PPS", "TPI"]
split_data = {}

for prefix in prefixes:
    split_data[prefix] = output_cleaned[output_cleaned["item"].str.startswith(prefix)]

for prefix, df_subset in split_data.items():
    filename = f"{prefix.lower()}_vangsness_2019.csv"
    df_subset.to_csv(filename, index=False)
