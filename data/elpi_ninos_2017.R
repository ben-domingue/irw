library(haven)
library(tidyverse)
library(labelled)

df <- read_sav("Base Niños y Niñas ELPI III (SPSS).sav")

df <- df |>
  # drop unneeded variables
  select(-sexo,
         -idregion,
         -idcomuna,
         -pd1,
         -pd2_1,
         -pd2_2,
         -p1,
         -p2,
         -p2_curso,
         -asentimiento,
         -a7_esp,
         -b2_8_esp,
         -e7,
         -e7_cod,
         -e9,
         -e9_cod,
         -fexp_enc0_2,
         -fexp_eva0_2,
         -fexp_hog0_2,
         -estrato) |>
  # rename variables to their english equivalent
  rename(id = folio,
         age = edad) |>
  # recode variables to standardize no/yes answers to 0/1 binaries
  # recode "don't know" answers to NA
  mutate(a1 = if_else(a1 == 2, 0, a1),
         a2 = if_else(a2 == 2, 0, a2),
         a3 = if_else(a3 == 2, 0, a3),
         a4 = if_else(a4 == 2, 0, a4),
         a5 = if_else(a5 == 2, 0, a5),
         a6 = if_else(a6 == 2, 0, a6),
         a7 = if_else(a7 == 2, 0, a7),
         a8 = if_else(a8 == 4, 0, a8),
         a12 = if_else(a12 == 2, 0, a12),
         a21_1 = if_else(a21_1 == 2, 0, a21_1),
         a21_2 = if_else(a21_2 == 2, 0, a21_2),
         a21_3 = if_else(a21_3 == 2, 0, a21_3),
         a21_4 = if_else(a21_4 == 2, 0, a21_4),
         a21_5 = if_else(a21_5 == 2, 0, a21_5),
         a21_6 = if_else(a21_6 == 2, 0, a21_6),
         a21_7 = if_else(a21_7 == 2, 0, a21_7),
         a21_8 = if_else(a21_8 == 2, 0, a21_8),
         b2_1 = if_else(b2_1 == 2, 0, b2_1),
         b2_2 = if_else(b2_2 == 2, 0, b2_2),
         b2_3 = if_else(b2_3 == 2, 0, b2_3),
         b2_4 = if_else(b2_4 == 2, 0, b2_4),
         b2_5 = if_else(b2_5 == 2, 0, b2_5),
         b2_6 = if_else(b2_6 == 2, 0, b2_6),
         b2_7 = if_else(b2_7 == 2, 0, b2_7),
         b2_8 = if_else(b2_8 == 2, 0, b2_8),
         b2_9 = if_else(b2_9 == 2, 0, b2_9),
         b8_1 = if_else(b8_1 == 2, 0, b8_1),
         b8_2 = if_else(b8_2 == 2, 0, b8_2),
         b8_3 = if_else(b8_3 == 2, 0, b8_3),
         b10 = if_else(b10 == 4, NA, b10),
         b13_1 = if_else(b13_1 == 2, 0, b13_1),
         b13_2 = if_else(b13_2 == 2, 0, b13_2),
         b13_3 = if_else(b13_3 == 2, 0, b13_3),
         b17 = if_else(b17 == 2, 0, b17),
         b18 = if_else(b18 == 2, 0, b18),
         b19 = if_else(b19 == 2, 0, b19),
         b20 = if_else(b20 == 2, 0, b20),
         b21 = if_else(b21 == 2, 0, b21),
         b22 = if_else(b22 == 2, 0, b22),
         b23 = if_else(b23 == 6, NA, b23),
         b24 = if_else(b24 == 6, NA, b24),
         c1 = case_when(c1 == 1 ~ 1,
                        c1 == 2 ~ 0,
                        c1 == 3 ~ NA),
         d4_1 = if_else(d4_1 == 2, 0, d4_1),
         d4_2 = if_else(d4_2 == 2, 0, d4_2),
         d4_3 = if_else(d4_3 == 2, 0, d4_3),
         d4_4 = if_else(d4_4 == 2, 0, d4_4),
         d5 = if_else(d5 == 5, NA, d5),
         d6 = if_else(d6 == 5, NA, d6),
         d7 = if_else(d7 == 5, NA, d7),
         d8 = if_else(d8 == 5, NA, d8),
         d9 = if_else(d9 == 5, NA, d9),
         d10 = if_else(d10 == 5, NA, d10),
         d11 = if_else(d11 == 5, NA, d11),
         d12 = if_else(d12 == 5, NA, d12),
         d13 = case_when(d13 == 1 ~ 1,
                         d13 == 2 ~ 0,
                         d13 == 3 ~ NA),
         d14 = case_when(d14 == 1 ~ 1,
                         d14 == 2 ~ 0,
                         d14 == 3 ~ NA),
         d15 = case_when(d15 == 1 ~ 1,
                         d15 == 2 ~ 0,
                         d15 == 3 ~ NA),
         d16 = case_when(d16 == 1 ~ 1,
                         d16 == 2 ~ 0,
                         d16 == 3 ~ NA),
         e8 = if_else(e8 == 8, NA, e8),
         tae_p1 = case_when(tae_p1 == 0 ~ 1,
                            tae_p1 == 1 ~ 0),
         tae_p2 = case_when(tae_p2 == 0 ~ 1,
                            tae_p2 == 1 ~ 0),
         tae_p3 = case_when(tae_p3 == 0 ~ 1,
                            tae_p3 == 1 ~ 0),
         tae_p4 = case_when(tae_p4 == 0 ~ 1,
                            tae_p4 == 1 ~ 0),
         tae_p5 = case_when(tae_p5 == 0 ~ 1,
                            tae_p5 == 1 ~ 0),
         tae_p6 = case_when(tae_p6 == 0 ~ 1,
                            tae_p6 == 1 ~ 0),
         tae_p7 = case_when(tae_p7 == 0 ~ 1,
                            tae_p7 == 1 ~ 0),
         tae_p8 = case_when(tae_p8 == 0 ~ 1,
                            tae_p8 == 1 ~ 0),
         tae_p9 = case_when(tae_p9 == 0 ~ 1,
                            tae_p9 == 1 ~ 0),
         tae_p10 = case_when(tae_p10 == 0 ~ 1,
                             tae_p10 == 1 ~ 0),
         tae_p11 = case_when(tae_p11 == 0 ~ 1,
                             tae_p11 == 1 ~ 0),
         tae_p12 = case_when(tae_p12 == 0 ~ 1,
                             tae_p12 == 1 ~ 0),
         tae_p13 = case_when(tae_p13 == 0 ~ 1,
                             tae_p13 == 1 ~ 0),
         tae_p14 = case_when(tae_p14 == 0 ~ 1,
                             tae_p14 == 1 ~ 0),
         tae_p15 = case_when(tae_p15 == 0 ~ 1,
                             tae_p15 == 1 ~ 0),
         tae_p16 = case_when(tae_p16 == 0 ~ 1,
                             tae_p16 == 1 ~ 0),
         tae_p17 = case_when(tae_p17 == 0 ~ 1,
                             tae_p17 == 1 ~ 0),
         tae_p18 = case_when(tae_p18 == 0 ~ 1,
                             tae_p18 == 1 ~ 0),
         tae_p19 = case_when(tae_p19 == 0 ~ 1,
                             tae_p19 == 1 ~ 0),
         tae_p20 = case_when(tae_p20 == 0 ~ 1,
                             tae_p20 == 1 ~ 0),
         tae_p21 = case_when(tae_p21 == 0 ~ 1,
                             tae_p21 == 1 ~ 0),
         tae_p22 = case_when(tae_p22 == 0 ~ 1,
                             tae_p22 == 1 ~ 0),
         tae_p23 = case_when(tae_p23 == 0 ~ 1,
                             tae_p23 == 1 ~ 0),
         # add timezone to date variable
         fecha = paste0(fecha, " CLT"),
         # convert date variable to unix time
         date = as.numeric(as.POSIXct(fecha, format="%Y-%m-%d"))) |>
  # drop old date variable
  select(-fecha) |>
  pivot_longer(cols = -c(id, date, age),
               names_to = 'item',
               values_to = 'resp')

# create item IDs for each survey item
items <- as.data.frame(unique(df$item))
items <- items |>
  mutate(item_id = row_number())

df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("item" = "unique(df$item)")) |>
  # drop character item variable
  select(id, item_id, resp, age) |>
  # use item_id column as the item column
  rename(item = item_id)

# remove obsolete label for resp column
df$resp <- remove_labels(df$resp)
df$id <- remove_labels(df$id)
df$age <- remove_labels(df$age)

# save df to Rdata file
save(df, file="elpi_ninos_2017.Rdata")