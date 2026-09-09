# Smits, Dolan, Vorst, Wicherts & Timmerman (2011), "Cohort differences in Big
# Five personality factors over a period of 25 years", JPSP 100(6):1124-1138.
# doi:10.1037/a0022874
#
# Source: DANS, doi:10.17026/DANS-Z5P-ZEDJ (CC0), file `data5pft19822007.tab`.
# The dictionary still records the retired EASY URL (easy-dataset:51655), which
# now answers with an anti-bot challenge rather than the data; the Data Station
# DOI above is the live copy of the same deposit -- 8,954 rows, matching the
# published table's id count. (The dictionary also records CC BY 4.0; DANS
# states CC0-1.0.)
#
# `TWNO` IS NOT UNIQUE. 18 participant numbers appear twice, and all 18 are two
# different students rather than one student recorded twice (#1842):
#
#   * not one of the 18 pairs is byte-identical on the whole row;
#   * they agree on 5 to 52 of the 70 items, mostly 8-18 -- about what two
#     unrelated people score on a 7-point scale by chance;
#   * `cohort` and `testweek` are identical within every pair, so no occasion
#     column explains them;
#   * twno 16167 is explicit: sex 2 vs 1, age 18 vs 24.
#
# The published table used `twno` alone, so 18 pairs of students are merged into
# one respondent each. Block H prescribed "dedupe 264, chase 996"; deduping
# would delete 18 people. They take an occurrence suffix, as PEPABAS2C's and
# SAS_Deters_2022's did.
#
# `age` also becomes `cov_age` -- a person-level covariate must carry the prefix.
#
# Not shipped, though the source has them and this study is *about* them:
# `cohort` (13 values) and `testweek` (25). Adding them changes the table's
# shape, so it is left for its own pass -- but a table built from the Smits
# cohort study without its cohort column is missing the study's own variable.
library(tidyverse)
library(readr)

df <- read_tsv('data5pft19822007.tab', show_col_types = FALSE)

names(df) <- tolower(names(df))

stopifnot(anyDuplicated(df$twno) > 0)   # the collision this file exists to fix
rep_twno <- df$twno %in% df$twno[duplicated(df$twno)]
if (any(rep_twno)) {
  df$twno <- as.character(df$twno)
  ## A LETTER suffix, not ".1": `twno` is purely numeric, so "16167.1" parses
  ## straight back to a double and reads as a decimal rather than as two people.
  ## "16167a"/"16167b" cannot.
  df$twno[rep_twno] <- paste0(df$twno[rep_twno],
                              letters[ave(seq_len(sum(rep_twno)),
                                          df$twno[rep_twno], FUN = seq_along)])
  message(sprintf("5personalityfactors: %d participant number(s) held by two students; suffixed %d row(s)",
                  sum(rep_twno) / 2L, sum(rep_twno)))
}
stopifnot(!anyDuplicated(df$twno))

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

# A missing response is not a response. These were written out as NA and land in
# the warehouse as the literal string "NA", which is what types `resp` as a
# string rather than an integer (#1842).
df <- df[!is.na(df$resp), ]

# `age` is a person-level covariate and must carry the prefix; 99 is the
# codebook's missing code for it, already mapped to -9 above.
names(df)[names(df) == "age"] <- "cov_age"
df$cov_age[df$cov_age == -9] <- NA

stopifnot(!anyDuplicated(df[, c("id", "item")]))

# save df to Rdata file
save(df, file="5personalityfactors.Rdata")
write.csv(df, "5personalityfactors.csv", row.names = FALSE)
