import pandas as pd
## Import data
df1 = pd.read_csv('area_all_osf.csv')
df1.drop(columns=['age', 'gender', 'sample'], inplace=True)
df2 = df1.copy()

## Check Null Values
null_counts = df2.isnull().sum()
null_counts

## Remove Null Values
df2_cleaned = df2.dropna()
print("Cleaned DataFrame shape:", df2_cleaned.shape)

## Check data type
df2_cleaned.dtypes

## Start Convert Vector Here
new_data = []

for index, row in df2_cleaned.iterrows():
    for column in df2_cleaned.columns:
        new_data.append([index + 1, column, row[column]])  

output = pd.DataFrame(new_data, columns=['id', 'item', 'resp'])   
print(output)

## Save the result as csv file
output.to_csv('aa1_Silvia_2023.csv', index=False)