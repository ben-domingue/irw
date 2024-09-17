# Paper: https://osf.io/preprints/osf/vq3ty
# Data: https://osf.io/4xzr8/
library(dplyr)
library(tidyr)
library(haven)

common_cols <- c("id")
# ------ Helper Function ------
encode_scale <- function(df, resp) {
  df[setdiff(names(df), common_cols)] <- lapply(df[setdiff(names(df), common_cols)], function(x) {
    # Loop through each value in 'resp' and assign its index + 1
    for (i in seq_along(resp)) {
      x[x == resp[i]] <- i
    }
    return(as.numeric(x))
  })
  return(df)
}

df <- read.csv("HEARD BFS Baseline Psychometrics Limited Dataset.csv")
df <- df |> # Deletion of demographic data
  select(-MotherAge_T1, -YearsInCamp_T1, -Education_T1, -Marital_T1, 
         -RespChildren_T1, -Employment_T1, -Employment_Oth_T1,
         -MeatFreq_T1, -ChildSex_T1, -ChildAge_T1, -Pregnant_T1, -newsort)

# ------ Process IDSS Dataset ------
idss_df <- df |>
  select(id, starts_with("IDSS"))

idss_scale <- c("None of the time", "A little of the time", 
                "Some of the time", "Most of the time", "Almost all of the time")
idss_df <- encode_scale(idss_df, idss_scale)
idss_df <- pivot_longer(idss_df, cols=-id, names_to="item", values_to="resp")

save(idss_df, file="HEARD_Roch_2022_IDSS.Rdata")
write.csv(idss_df, "HEARD_Roch_2022_IDSS.csv", row.names=FALSE)

# ------ Process K6 Dataset ------
k6_df <- df |>
  select(id, starts_with("KESS"))

k6_scale <- c("None of the time", "A little of the time", 
              "Some of the time", "Most of the time", "All of the time")
k6_df <- encode_scale(k6_df, k6_scale)
k6_df <- pivot_longer(k6_df, cols=-id, names_to="item", values_to="resp")

save(k6_df, file="HEARD_Roch_2022_K6.Rdata")
write.csv(k6_df, "HEARD_Roch_2022_K6.csv", row.names=FALSE)

# ------ Process WHODAS Dataset ------ 
whodas_df <- df |>
  select(id, starts_with("WHODAS"))

whodas_scale <- c("None", "Mild", "Moderate", "Severe", "Extreme or cannot do")
whodas_df <- encode_scale(whodas_df, whodas_scale)
whodas_df <- pivot_longer(whodas_df, cols=-id, names_to="item", values_to="resp")

save(whodas_df, file="HEARD_Roch_2022_WHODAS.Rdata")
write.csv(whodas_df, "HEARD_Roch_2022_WHODAS.csv", row.names=FALSE)

# ------ Process SWL & PWI Dataset ------
swlpwi_df <- df |>
  select(id, starts_with("PWI"), starts_with("SWL"))
swlpwi_df <- pivot_longer(swlpwi_df, cols=-id, names_to="item", values_to = "resp")

save(swlpwi_df, file="HEARD_Roch_2022_SWLPWI.Rdata")
write.csv(swlpwi_df, "HEARD_Roch_2022_SWLPWI.csv", row.names=FALSE)

# ------ Process COPE Dataset ------
cope_df <- df |>
  select(id, starts_with("COPE"))

cope_scale <- c("Not at all", "A little bit", "A medium amount", "A lot")
cope_df <- encode_scale(cope_df, cope_scale)
cope_df <- pivot_longer(cope_df, cols=-id, names_to="item", values_to = "resp")

save(cope_df, file="HEARD_Roch_2022_COPE.Rdata")
write.csv(cope_df, "HEARD_Roch_2022_COPE.csv", row.names=FALSE)
