### Import data
df = pd.read_csv('imputate(fivecountries).tab', delimiter='\t')
df.to_csv('imputate(fivecountries).csv', index=False)
df2 = pd.read_csv('imputate(fivecountries).csv')

### Drop columns
df2.drop(columns=['group', 'Gender', 'age', 'edu_level', 'profession'], inplace=True)

### Check null value
null_values = df2.isnull().sum()
print(null_values)

new_data = []
for index, row in df2.iterrows():
    for column in df2.columns:
        new_data.append([index + 1, column, row[column]])  

op = pd.DataFrame(new_data, columns=['id', 'item', 'resp'])

### Save result to csv
op.to_csv('imputate_(fivecountries).csv', index=False)

##bd note: table name changed to movac_pakpour2022
