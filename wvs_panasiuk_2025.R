setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
rm(list = ls ())
library(tidyverse)
library(haven)

df <- read_csv("WVS_TimeSeries_4_0.csv")
df <- df %>%
  mutate(
    # Set NA date
    date = ifelse(S012 %in% c(-3, -4, -5), NA, S012),
    # Convert to Unix timestamps
    date = as.numeric(as.POSIXct(as.character(date), format = "%Y%m%d", tz = "UTC")),
  )

# -------- Perceptions of life (206 items, beginning with 'A') --------
percep_life <- names(df)[startsWith(names(df), "A")]
item_family_A <- tibble(item = percep_life) %>%
  mutate(item_family = case_when(
    item %in% c("A001", "A002", "A003", "A004", "A005", "A006") ~ "Important in life",
    item %in% c("A027", "A029", "A030", "A032", "A034", "A035", "A038", "A039", "A040", 
                "A041", "A042", "A043B") ~ "Important child qualities",
    item %in% c("A044", "A045") ~ "What child should learn",
    item %in% c("A046", "A047", "A048", "A049") ~ "Abortion",
    item %in% c("A057", "A058", "A059", "A060", "A061") ~ "Spend time with",
    item %in% c("A064", "A065", "A066", "A080_02", "A067", "A068", "A069","A080_01",
                "A070", "A071", "A071B", "A071C", "A072", "A073", "A074", "A075", "A076", "A077", "A079", "A080") ~ "Member",
    item %in% c("A081", "A082", "A083", "A084", "A085", "A086", "A087", "A088", 
                "A088B", "A088C", "A089", "A090", "A091", "A092", "A093", "A094", "A096", "A097") ~ "Voluntary work",
    item %in% c("A098", "A099", "A100", "A101", "A102", "A103", "A104", "A105", "A106", "A106B", "A106C", "A106D") ~ "Active/Inactive membership",
    item %in% c("A107", "A108", "A109", "A110", "A111", "A112", "A113", 
                "A114", "A115", "A116", "A117", "A118", "A119", "A120") ~ "Reasons voluntary work",
    str_detect(item, "^A124_") ~ "neighbours",
    item %in% c("A168", "A168A") ~ "Take advantage",
    item %in% c("A189", "A190", "A191", "A192", "A193", "A194", "A195", 
                "A196", "A197", "A198", "A199") ~ "Schwartz",
    item %in% c("A200", "A201", "A202") ~ "Social position",
    item %in% c("A204", "A205", "A206") ~ "Peolple over 70",
    item %in% c("A213", "A214", "A215", "A216", "A217", "A218", "A219", "A220", "A221", "A222") ~ "Myself",
    TRUE ~ NA_character_
  ))

df_items_A <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(percep_life))

df_long_A <- df_items_A %>%
  pivot_longer(
    cols = all_of(percep_life),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_A, by = "item")

# Set NAs of resp
df_long_A <- df_long_A %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))
# Drop items with categorical values
items_drop_A <- c("A044", "A045", "A169")
df_long_A <- df_long_A %>%
  filter(!item %in% items_drop_A)

write_csv(df_long_A, "wvs_panasiuk_perception_of_life.csv")

#----------------- Environment (25 items, beginning with B) -------------------
env <- names(df)[startsWith(names(df), "B")]
item_family_B <- tibble(item = env) %>%
  mutate(item_family = case_when(
    item %in% c("B011", "B012", "B013", "B014", "B015") ~ "Environmental action",
    item %in% c("B018", "B019", "B020") ~ "Env problems(community)",
    item %in% c("B021", "B022", "B023") ~ "Env problems(world)",
    item %in% c("B030", "B031") ~ "Past two years",
    TRUE ~ NA_character_
  ))
df_items_B <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(env))

df_long_B <- df_items_B %>%
  pivot_longer(
    cols = all_of(env),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_B, by = "item")
# Set NAs of resp
df_long_B <- df_long_B %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_B <- c("B008", "B009", "B016", "B017")
df_long_B <- df_long_B %>%
  filter(!item %in% items_drop_B)

write_csv(df_long_B, "wvs_panasiuk_environment.csv")

#--------------------- Work (48 items, beginning with C) -----------------------
work <- setdiff(
  names(df)[startsWith(names(df), "C")],
  c("COUNTRY_ALPHA", "COW_NUM", "COW_ALPHA")
)
item_family_C <- tibble(item = work) %>%
  mutate(item_family = case_when(
    item %in% c("C001", "C001_01", "C002", "C002_01", "C004") ~ "Jobs scarce",
    item %in% c("C011", "C012", "C013", "C014", "C015", "C016", 
                "C017", "C018", "C019", "C020", "C021", "C022", 
                "C023", "C024", "C025", "C027_90") ~ "Improtant in a job",
    item %in% c("C042B1", "C042B2", "C042B3", "C042B4", "C042B5", "C042B6",
                "C042B7") ~ "Why people work",
    item %in% c("C062", "C063", "C064") ~ "Work",
    TRUE ~ NA_character_
  ))
df_items_C <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(work))

df_long_C <- df_items_C %>%
  pivot_longer(
    cols = all_of(work),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_C, by = "item")
# Set NAs of resp
df_long_C <- df_long_C %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_C <- c("C009", "C010")
df_long_C <- df_long_C %>%
  filter(!item %in% items_drop_C)

write_csv(df_long_C, "wvs_panasiuk_work.csv")
#-------------------- Family (68 items, beginning with D) ----------------------
fam <- names(df)[startsWith(names(df), "D")]
item_family_D <- tibble(item = fam) %>%
  mutate(item_family = case_when(
    item %in% c("D001", "D001_B") ~ "Trust",
    item %in% c("D003", "D004", "D005", "D006", "D007", "D008", "D009", "D010", 
                "D011", "D012", "D013", "D014", "D015", "D016") ~ "Sharing with partner",
    item %in% c("D026_03", "D026_05") ~ "Duty",
    item %in% c("D027", "D028", "D029", "D030", "D031", "D032", "D033", "D034", 
                "D035", "D036", "D037", "D038", "D043") ~ "Important for marriage",
    item %in% c("D063", "D063_B") ~ "Women independent",
    item %in% c("D066", "D066_B", "D066_01") ~ "Women more income",
    item %in% c("D067", "D068", "D069", "D070", "D071", "D072", "D073", "D074", 
                "D075") ~ "Traits in women",
    TRUE ~ NA_character_
  ))
df_items_D <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(fam))

df_long_D <- df_items_D %>%
  pivot_longer(
    cols = all_of(fam),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_D, by = "item")
# Set NAs of resp
df_long_D <- df_long_D %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_D <- c("D025")
df_long_D <- df_long_D %>%
  filter(!item %in% items_drop_D)

write_csv(df_long_D, "wvs_panasiuk_family.csv")
#----------- Politics and Society (295 items, beginning with E) ----------------
library(data.table)
politics_society <- names(df)[startsWith(names(df), "E")]
item_family_E <- tibble(item = politics_society) %>%
  mutate(item_family = case_when(
    item %in% c("E001", "E002") ~ "Aims of country",
    item %in% c("E003", "E004") ~ "Aims of respondent",
    item %in% c("E005", "E006") ~ "Most important",
    item %in% c("E007", "E008", "E009", "E010") ~ "National goals",
    item %in% c("E014", "E015", "E016", "E017", "E018", "E019", "E020") ~ "Future changes",
    item %in% c("E025", "E025B", "E026", "E026B", "E027", "E028", "E028B", "E029",
                "E221B", "E222", "E222B") ~ "Political action",
    item %in% c("E047", "E048", "E049", "E050", "E051", "E052", "E053", "E054",
                "E055", "E056") ~ "Personal characteristics",
    item %in% c("E063", "E064", "E065") ~ "Current society",
    item %in% c("E066", "E067", "E068") ~ "Society aimed",
    str_detect(item, "^E69_") ~ "Confidence", 
    item %in% c("E104", "E105", "E106", "E107", "E108", "E109") ~ "Approval",
    item %in% c("E114", "E115", "E116", "E117", "E117B") ~ "Political system",
    item %in% c("E129", "E129A", "E129B", "E129C", "E129D") ~ "Economic aid",
    item %in% c("E135", "E136", "E137", "E138", "E139") ~ "Decide",
    item %in% c("E179WVS", "E179_WVS7LOC", "E180WVS", "E182") ~ "Party voted",
    item %in% c("E190", "E191") ~ "Reason living in need",
    item %in% c("E193", "E194", "E195") ~ "Least liked allow",
    item %in% c("E224", "E225", "E226", "E227", "E228", "E229", "E230", "E231",
                "E232", "E233", "E233A", "E233B") ~ "Democracy",
    item %in% c("E238", "E239") ~ "Serious problem (world)",
    item %in% c("E240", "E241") ~ "Serious problem (country)",
    item %in% c("E242", "E243", "E244", "E245", "E246") ~ "MDG",
    item %in% c("E248", "E248B", "E249", "E250", "E250B", "E251", "E252", "E253",
                "E253B", "E254", "E254B", "E258", "E258B", "E259", "E259B", "E260",
                "E260B", "E261", "E261B", "E262", "E262B") ~ "Information source",
    item %in% c("E263", "E264") ~ "Vote in elections",
    str_detect(item, "^E265_") ~ "Frequency in elections", 
    item %in% c("E269", "E270", "E271", "E272", "E273") ~ "Corruption",
    item %in% c("E282", "E283", "E284", "E285") ~ "Internet political actions",
    item %in% c("E286", "E287", "E288") ~ "Social activism",
    TRUE ~ NA_character_
  ))
setDT(item_family_E)
df_items_E <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(politics_society))
setDT(df_items_E)

# Melt in chunks 
block_size  <- 50
col_blocks  <- split(politics_society,
                     ceiling(seq_along(politics_society) / block_size))

out_list <- vector("list", length(col_blocks))

for (i in seq_along(col_blocks)) {
  out_list[[i]] <- melt(
    df_items_E,
    id.vars        = c("id", "wave", "date", "cov_gender", "cov_age"),
    measure.vars   = col_blocks[[i]],
    variable.name  = "item",
    value.name     = "resp",
    variable.factor = FALSE
  )
}

df_long_E <- rbindlist(out_list, use.names = TRUE)
df_long_E <- merge(
  df_long_E,
  item_family_E,
  by = "item",
  all.x = TRUE,
  sort = FALSE
)
# Set NAs of resp
df_long_E <- df_long_E %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_E <- c("E001", "E002", "E003", "E004", "E005", "E006", "E032", "E062", "E118", "E119",
                  "E135", "E136", "E137", "E138", "E139", "E179WVS", "E179_WVS7LOC", "E180WVS",
                  "E182", "E190", "E191", "E192", "E238", "E239", "E240", "E241", "E256", "E279",
                  "E280", "E281")
df_long_E <- df_long_E[!item %in% items_drop_E]

data.table::fwrite(df_long_E, "wvs_panasiuk_politics_society.csv")

#--------------- Religion and Morale (127 items, beginning with F) -------------
religion_morality <- names(df)[startsWith(names(df), "F")]
item_family_F <- tibble(item = religion_morality) %>%
  mutate(item_family = case_when(
    item %in% c("F004", "F005", "F006", "F007", "F008", "F009", "F010") ~ "Meaning of life",
    item %in% c("F031", "F032", "F033") ~ "Important religious",
    item %in% c("F035", "F036", "F037", "F038") ~ "Churches give answers",
    item %in% c("F040", "F041", "F042", "F043", "F044", "F045", "F046", "F047", 
                "F048", "F049") ~ "Churches speak out",
    item %in% c("F050", "F051", "F052", "F053", "F054", "F055", "F057", "F059", "F060") ~ "Believe",
    item %in% c("F066", "F067") ~ "Pray to God",
    item %in% c("F108", "F109") ~ "Government",
    item %in% c("F114A", "F114E", "F114B", "F114C", "F114D", "F115", "F116", "F117",
                "F118", "F119", "F120", "F121", "F122", "F123", "F124", "F125", 
                "F126", "F127", "F128", "F129", "F130", "F132", "F135", "F135A",
                "F136", "F139", "F140", "F141", "F142", "F143", "F144", "F144_02",
                "F199") ~ "Justifiable",
    item %in% c("F164", "F165", "F166", "F167", "F168", "F169", "F170", "F171", 
                "F172", "F173", "F174") ~ "Islam",
    item %in% c("F194", "F195", "F196", "F197") ~ "Important",
    item %in% c("F200", "F201") ~ "Meaning of religion",
    TRUE ~ NA_character_
  ))
df_items_F <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(religion_morality))

df_long_F <- df_items_F %>%
  pivot_longer(
    cols = all_of(religion_morality),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_F, by = "item")
# Set NAs of resp
df_long_F <- df_long_F %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_F <- c("F022", "F025", "F025_WVS", "F027", "F188", "F189", "F192", "F200", "F201")
df_long_F <- df_long_F %>%
  filter(!item %in% items_drop_F)

write_csv(df_long_F, "wvs_panasiuk_religion_morality.csv")
#-------------- National Identity (116 items, beginning with G) ----------------
national_identity <- names(df)[startsWith(names(df), "G")]
item_family_G <- tibble(item = national_identity) %>%
  mutate(item_family = case_when(
    str_detect(item, "^G007_") ~ "Trust", 
    item %in% c("G015", "G015B") ~ "Describe you",
    item %in% c("G019", "G020", "G021", "G023") ~ "Citizen idendity",
    str_detect(item, "^G022") ~ "Citizen idendity",
    item %in% c("G024", "G025") ~ "Proud of country",
    item %in% c("G028", "G029", "G030", "G031") ~ "Requirements for citizenship",
    item %in% c("G053", "G054", "G055", "G056", "G057", "G058", "G059", "G060") ~ "Eﬀects of immigrants",
    item %in% c("G062", "G063", "G255") ~ "Close feel",
    TRUE ~ NA_character_
  ))
df_items_G <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(national_identity))

df_long_G <- df_items_G %>%
  pivot_longer(
    cols = all_of(national_identity),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_G, by = "item")
# Set NAs of resp
df_long_G <- df_long_G %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_G <- c("G001", "G001CS", "G002", "G002CS", "G003CS", "G005", "G015", "G015B", "G016", "G017",
                  "G024", "G025", "G026", "G026_01", "G027", "G027_01", "G027A", "G027B")
df_long_G <- df_long_G %>%
  filter(!item %in% items_drop_G)

write_csv(df_long_G, "wvs_panasiuk_national_identity.csv")
#-------------- Security (30 items, beginning with H) -------------------------
security <- names(df)[startsWith(names(df), "H")]
item_family_H <- tibble(item = security) %>%
  mutate(item_family = case_when(
    item %in% c("H002_01", "H002_02", "H002_03", "H002_04", "H002_05") ~ "Frequency in neighborhood",
    item %in% c("H003_01", "H003_02", "H003_03") ~ "Security",
    item %in% c("H006_01", "H006_02", "H006_03", "H006_04", "H006_05", "H006_06") ~ "Worries",
    item %in% c("H008_01", "H008_02", "H008_03", "H008_04", "H008_05", "H008_06",
                "H008_07", "H008_08", "H008_09") ~ "Frequency in family",
    item %in% c("H009", "H010", "H011") ~ "Government right",
    TRUE ~ NA_character_
  ))
df_items_H <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(security))

df_long_H <- df_items_H %>%
  pivot_longer(
    cols = all_of(security),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_H, by = "item")
# Set NAs of resp
df_long_H <- df_long_H %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

# Drop items with categorical values
items_drop_H <- c("H008_07", "H008_08")
df_long_H <- df_long_H %>%
  filter(!item %in% items_drop_H)

write_csv(df_long_H, "wvs_panasiuk_security.csv")
#-------------------- Science (2 items, beginning with I) ----------------------
science <- names(df)[startsWith(names(df), "I")]
item_family_I <- tibble(item = science) %>%
  mutate(item_family = case_when(
    TRUE ~ NA_character_
  ))
df_items_I <- df %>%
  select(id = S006,
         wave = S002VS,
         date,
         cov_gender = X001,
         cov_age = X003,
         all_of(science))

df_long_I <- df_items_I %>%
  pivot_longer(
    cols = all_of(science),
    names_to = "item",
    values_to = "resp"
  ) %>%
  left_join(item_family_I, by = "item")
# Set NAs of resp
df_long_I <- df_long_I %>%
  mutate(resp = ifelse(resp %in% c(-1, -2, -3, -4, -5), NA, resp))

write_csv(df_long_I, "wvs_panasiuk_science.csv")
