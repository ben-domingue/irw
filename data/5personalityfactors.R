library(tidyverse)
library(readr)

df <- read_csv('data.csv')

names(df) <- tolower(names(df))

df <- df |>
  # rename "twono" (participant ID) variable to id
  rename(id = twno) |>
  # drop unneeded columns
  select(-cohort,
         -sex,
         -testweek,
         -mis5pft,
         -e5pft_val,
         -v5pft_val,
         -g5pft_val,
         -n5pft_val,
         -o5pft_val) |>
  # reshape df long by item
  pivot_longer(cols = starts_with('pf'),
               names_to = 'item',
               values_to = 'resp') |>
  # recode missing values (99 for age and 0 for resp) to -9
  # replace item values with standardized IDs
  mutate(age = if_else(age == 99, -9, age),
         resp = if_else(resp == 0, -9, resp),
         item = case_when(item == 'pf01e01' ~ '1_extraversion',
                          item == 'pf02a01' ~ '1_agreeableness',
                          item == 'pf03c01' ~ '1_conscientiousness',
                          item == 'pf04n01' ~ '1_neuroticism',
                          item == 'pf05o01' ~ '1_openness',
                          item == 'pf06e02' ~ '2_extraversion',
                          item == 'pf07a02' ~ '2_agreeableness',
                          item == 'pf08c02' ~ '2_conscientiousness',
                          item == 'pf09n02' ~ '2_neuroticism',
                          item == 'pf10o02' ~ '2_openness',
                          item == 'pf11e03' ~ '3_extraversion',
                          item == 'pf12a03' ~ '3_agreeableness',
                          item == 'pf13c03' ~ '3_conscientiousness',
                          item == 'pf14n03' ~ '3_neuroticism',
                          item == 'pf15o03' ~ '3_openness',
                          item == 'pf16e04' ~ '4_extraversion',
                          item == 'pf17a04' ~ '4_agreeableness',
                          item == 'pf18c04' ~ '4_conscientiousness',
                          item == 'pf19n04' ~ '4_neuroticism',
                          item == 'pf20o04' ~ '4_openness',
                          item == 'pf21e05' ~ '5_extraversion',
                          item == 'pf22a05' ~ '5_agreeableness',
                          item == 'pf23c05' ~ '5_conscientiousness',
                          item == 'pf24n05' ~ '5_neuroticism',
                          item == 'pf25o05' ~ '5_openness',
                          item == 'pf26e06' ~ '6_extraversion',
                          item == 'pf27a06' ~ '6_agreeableness',
                          item == 'pf28c06' ~ '6_conscientiousness',
                          item == 'pf29n06' ~ '6_neuroticism',
                          item == 'pf30o06' ~ '6_openness',
                          item == 'pf31e07' ~ '7_extraversion',
                          item == 'pf32a07' ~ '7_agreeableness',
                          item == 'pf33c07' ~ '7_conscientiousness',
                          item == 'pf34n07' ~ '7_neuroticism',
                          item == 'pf35o07' ~ '7_openness',
                          item == 'pf36e08' ~ '8_extraversion',
                          item == 'pf37a08' ~ '8_agreeableness',
                          item == 'pf38c08' ~ '8_conscientiousness',
                          item == 'pf39n08' ~ '8_neuroticism',
                          item == 'pf40o08' ~ '8_openness',
                          item == 'pf41e09' ~ '9_extraversion',
                          item == 'pf42a09' ~ '9_agreeableness',
                          item == 'pf43c09' ~ '9_conscientiousness',
                          item == 'pf44n09' ~ '9_neuroticism',
                          item == 'pf45o09' ~ '9_openness',
                          item == 'pf46e10' ~ '10_extraversion',
                          item == 'pf47a10' ~ '10_agreeableness',
                          item == 'pf48c10' ~ '10_conscientiousness',
                          item == 'pf49n10' ~ '10_neuroticism',
                          item == 'pf50o10' ~ '10_openness',
                          item == 'pf51e11' ~ '11_extraversion',
                          item == 'pf52a11' ~ '11_agreeableness',
                          item == 'pf53c11' ~ '11_conscientiousness',
                          item == 'pf54n11' ~ '11_neuroticism',
                          item == 'pf55o11' ~ '11_openness',
                          item == 'pf56e12' ~ '12_extraversion',
                          item == 'pf57a12' ~ '12_agreeableness',
                          item == 'pf58c12' ~ '12_conscientiousness',
                          item == 'pf59n12' ~ '12_neuroticism',
                          item == 'pf60o12' ~ '12_openness',
                          item == 'pf61e13' ~ '13_extraversion',
                          item == 'pf62a13' ~ '13_agreeableness',
                          item == 'pf63c13' ~ '13_conscientiousness',
                          item == 'pf64n13' ~ '13_neuroticism',
                          item == 'pf65o13' ~ '13_openness',
                          item == 'pf66e14' ~ '14_extraversion',
                          item == 'pf67a14' ~ '14_agreeableness',
                          item == 'pf68c14' ~ '14_conscientiousness',
                          item == 'pf69n14' ~ '14_neuroticism',
                          item == 'pf70o14' ~ '14_openness')) |>
  # reorder columns
  select(id, item, resp, age)


df<-as.data.frame(df)
table(df$resp)
df$resp<-ifelse(df$resp<1 | df$resp>7,NA,df$resp)
table(df$resp)
# save df to Rdata file
save(df, file="5personalityfactors.Rdata")
