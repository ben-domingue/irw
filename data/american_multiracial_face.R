library(tidyverse)
library(haven)
library(janitor)

# Source: OSF project https://osf.io/qsdrp ("American Multiracial Face
# Database", Chen, Norman & Nam 2020), folder "Data and syntax for
# reliability". CC BY 4.0. The .sav files are not in the repo; fetch them
# on demand so the script runs from a clean checkout.
osf_keys <- c(
  "Smile_White_prototypicality_trans.sav"     = "rv9ec",
  "Smile_smile_final_trans.sav"               = "xa36t",
  "Neutral_Asian_prototypicality_trans.sav"   = "m2scw",
  "Neutral_Black_prototypicality_trans.sav"   = "h5z7x",
  "Neutral_Expression_trans.sav"              = "pu9rg",
  "Neutral_ambiguity_trans.sav"               = "9xfdz",
  "Neutral_Latinx_prototypicality_trans.sav"  = "j3rk6",
  "Neutral_Masculinity_trans.sav"             = "kgje6",
  "Neutral_MidEast_prototypicality_trans.sav" = "n83t2",
  "Neutral_Multi_prototypicality_trans.sav"   = "ju392",
  "Neutral_White_prototypicality_trans.sav"   = "kd5aw",
  "Smile_Asian_prototypicality_trans.sav"     = "dmztw",
  "Smile_Black_prototypicality_trans.sav"     = "435by",
  "Smile_Expression_trans.sav"                = "z7qwn",
  "Smile_Latinx_prototypicality_trans.sav"    = "2acnd",
  "Smile_Masculinity_trans.sav"               = "8pdcw",
  "Smile_MidEast_prototypicality_trans.sav"   = "fy2um",
  "Smile_Multi_prototypicality_trans.sav"     = "uewjd",
  "Smile_ambiguity_trans.sav"                 = "ztp5w",
  "Smile_attractive_trans.sav"                = "xgnkd"
)

read_osf_sav <- function(file) {
  if (!file.exists(file)) {
    download.file(paste0("https://osf.io/download/", osf_keys[[file]]), file,
                  mode = "wb", quiet = TRUE)
  }
  read_sav(file)
}

# import raw data files
smile_white_prototypicality_trans <- read_osf_sav("Smile_White_prototypicality_trans.sav")
smile_smile_final_trans <- read_osf_sav("Smile_smile_final_trans.sav")
neutral_asian_prototypicality_trans <- read_osf_sav('Neutral_Asian_prototypicality_trans.sav')
neutral_black_prototypicality_trans <- read_osf_sav('Neutral_Black_prototypicality_trans.sav')
neutral_expression_trans <- read_osf_sav('Neutral_Expression_trans.sav')
neutral_expression_trans <- neutral_expression_trans |> select(-`filter_$`)
neutral_ambiguity_trans <- read_osf_sav('Neutral_ambiguity_trans.sav')
neutral_latinx_prototypicality_trans.sav <- read_osf_sav('Neutral_Latinx_prototypicality_trans.sav')
neutral_masculinity_trans.sav <- read_osf_sav('Neutral_Masculinity_trans.sav')
neutral_midEast_prototypicality_trans.sav <- read_osf_sav('Neutral_MidEast_prototypicality_trans.sav')
neutral_multi_prototypicality_trans.sav <- read_osf_sav('Neutral_Multi_prototypicality_trans.sav')
neutral_white_prototypicality_trans.sav <- read_osf_sav('Neutral_White_prototypicality_trans.sav')
smile_asian_prototypicality_trans.sav <- read_osf_sav('Smile_Asian_prototypicality_trans.sav')
# Smiling-photo Black prototypicality: originally omitted, which left Black
# as the only one of the six racial-prototypicality traits with no smiling
# block (see issue #1660). Adding it renumbers `item`, since codes are
# row_number() over unique(case_lbl) after the rbind below.
smile_black_prototypicality_trans <- read_osf_sav('Smile_Black_prototypicality_trans.sav')
smile_expression_trans.sav <- read_osf_sav('Smile_Expression_trans.sav')
smile_latinx_prototypicality_trans.sav <- read_osf_sav('Smile_Latinx_prototypicality_trans.sav')
smile_masculinity_trans.sav <- read_osf_sav('Smile_Masculinity_trans.sav')
smile_midEast_prototypicality_trans.sav <- read_osf_sav('Smile_MidEast_prototypicality_trans.sav')
smile_multi_prototypicality_trans.sav <- read_osf_sav('Smile_Multi_prototypicality_trans.sav')
smile_ambiguity_trans.sav <- read_osf_sav('Smile_ambiguity_trans.sav')
smile_attractive_trans.sav <- read_osf_sav('Smile_attractive_trans.sav')

# append different files together
all_objects <- ls()
df_names <- all_objects[sapply(all_objects, function(obj) is.data.frame(get(obj)))]
dataframes <- mget(df_names)
df <- do.call(rbind, dataframes)

df <- df |>
  # remove index from df
  rownames_to_column(var = "row_index") |>
  # convert variable names to lowercase
  clean_names(case = 'snake') |>
  # drop unneeded variables
  select(-row_index,
         -id,
         -face) |>
  # rename variables to be consistent with IRW standards
  rename(id = rater,
         resp = rating) |>
  # recode invalid response values to NA
  mutate(resp = if_else(resp == 0, NA, resp)) |>
  # drop observations without response values
  drop_na()

# create item IDs for each survey item
items <- as.data.frame(unique(df$case_lbl))
items <- items |>
  mutate(item = row_number())


df <- df |>
  # merge item IDs with df
  left_join(items, 
            by=c("case_lbl" = "unique(df$case_lbl)")) |>
  # select only relevant columns
  select(id, item, resp) |>
  # sort df by id and item
  arrange(id, item)
  

# print response values
table(df$resp)

# Neutral_Smile_final_trans.sav is deliberately NOT loaded: it asks how
# genuine a smile is about *neutral* (non-smiling) photographs, where
# 0 = "N/A this person is not smiling" is the expected answer. Only 4,322
# of its 135,228 rows carry a real rating, so it would add a block that is
# ~97% missing by design.

# save df
save(df, file="american_multiracial_face.Rdata")
write.csv(df, "american_multiracial_face.csv", row.names=FALSE)
