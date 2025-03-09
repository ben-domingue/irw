# Data: https://osf.io/4b85w/
# Paper: http://link.springer.com/article/10.3758/s13428-023-02121-5#Abs1
library(haven)
library(dplyr)
library(tidyr)
library(stringr)

cov_list <- c("age", "gender", "ethnicity", "relationship_status", "education", "trans", "sexual_orientation", "country", "employment")
arc_df <- read.csv("ARC_raw_data.csv")

convert_timepoint <- function(x) {
  if (str_detect(x, "baseline")) {
    return(0)
  } else if (str_detect(x, "week")) {
    return(as.numeric(str_extract(x, "\\d+"))-1)  # Extract week number
  } else if (str_detect(x, "month")) {
    return(as.numeric(str_extract(x, "\\d+")) + 11)  # Continue numbering after weeks
  } else {
    return(NA)  # Exclude all other values
  }
}

arc_df <- arc_df %>%
  mutate(wave = sapply(redcap_event_name, convert_timepoint)) %>%
  filter(!is.na(wave)) %>%
  rename(id=record_id)
arc_df <- arc_df %>%
  rename_with(~ paste0("cov_", .), all_of(cov_list))

# ---------- Mental Health Questionnaire ----------
mh_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("mental_health"), -starts_with("covid"))
mh_df <- mh_df |>
  select(-mental_health_other, -mental_health_recovery, -mental_health_undiagnosed)
mh_df <- pivot_longer(mh_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
mh_df <- mh_df %>%
  filter(!is.na(resp))

save(mh_df, file="oxfordcovid_xue_2024_mh.Rdata")
write.csv(mh_df, "oxfordcovid_xue_2024_mh.csv", row.names=FALSE)

# ---------- BFI Questionnaire ----------
bf_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("big_5"), -starts_with("covid"))
bf_df <- pivot_longer(bf_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
bf_df <- bf_df %>%
  filter(!is.na(resp))

save(bf_df, file="oxfordcovid_xue_2024_bfi.Rdata")
write.csv(bf_df, "oxfordcovid_xue_2024_bfi.csv", row.names=FALSE)

# ---------- University Admission Questionnaire ----------
ua_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("university"), -starts_with("covid"))
ua_df <- pivot_longer(ua_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
ua_df <- ua_df %>%
  filter(!is.na(resp))

save(ua_df, file="oxfordcovid_xue_2024_ua.Rdata")
write.csv(ua_df, "oxfordcovid_xue_2024_ua.csv", row.names=FALSE)

# ---------- PSWQ Questionnaire ----------
pswq_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("pswq"), -starts_with("covid"), -pswq_timestamp, -pswq_complete)
pswq_df  <- pivot_longer(pswq_df , -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
pswq_df  <- pswq_df  %>%
  filter(!is.na(resp))

split_df <- function(df) {
  pswq_a_df <- df[grepl("^edeq_a_\\d+$", df$item), ]
  pswq_c_df <- df[!grepl("^edeq_a_\\d+$", df$item), ]
  return(list(pswq_a_df = pswq_a_df, pswq_c_df = pswq_c_df))
}

# Execute function
split_data <- split_df(pswq_df)

# Extracting split dataframes
pswq_a_df <- split_data$pswq_a_df
pswq_c_df <- split_data$pswq_c_df

save(pswq_a_df , file="oxfordcovid_xue_2024_pswq_a.Rdata")
write.csv(pswq_a_df , "oxfordcovid_xue_2024_pswq_a.csv", row.names=FALSE)

save(pswq_c_df , file="oxfordcovid_xue_2024_pswq_c.Rdata")
write.csv(pswq_c_df , "oxfordcovid_xue_2024_pswq_c.csv", row.names=FALSE)

# ---------- IUSC Questionnaire ----------
iusc_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("iou"), -starts_with("covid"),-iou12_complete, -iou12_timestamp)
iusc_df  <- pivot_longer(iusc_df , -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
iusc_df  <- iusc_df  %>%
  filter(!is.na(resp))

save(iusc_df , file="oxfordcovid_xue_2024_iusc.Rdata")
write.csv(iusc_df , "oxfordcovid_xue_2024_iusc.csv", row.names=FALSE)

# ---------- MFQ Questionnaire ----------
mfq_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("mfq"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"), -starts_with("mfq_state"))
mfq_df  <- pivot_longer(mfq_df , -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
mfq_df  <- mfq_df  %>%
  filter(!is.na(resp))

save(mfq_df, file="oxfordcovid_xue_2024_mfq.Rdata")
write.csv(mfq_df, "oxfordcovid_xue_2024_mfq.csv", row.names=FALSE)

# ---------- RSE Questionnaire ----------
rse_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("rse"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
rse_df  <- pivot_longer(rse_df , -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
rse_df  <- rse_df  %>%
  filter(!is.na(resp))

save(rse_df, file="oxfordcovid_xue_2024_rse.Rdata")
write.csv(rse_df, "oxfordcovid_xue_2024_rse.csv", row.names=FALSE)

# ---------- School Questionnaire ----------
s_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("school"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
s_df  <- pivot_longer(s_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
s_df  <- s_df  %>%
  filter(!is.na(resp))

save(s_df, file="oxfordcovid_xue_2024_school.Rdata")
write.csv(s_df, "oxfordcovid_xue_2024_school.csv", row.names=FALSE)

# ---------- PAS Questionnaire ----------
pas_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("pas"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
pas_df  <- pivot_longer(pas_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
pas_df  <- pas_df  %>%
  filter(!is.na(resp))

save(pas_df, file="oxfordcovid_xue_2024_pas.Rdata")
write.csv(pas_df, "oxfordcovid_xue_2024_pas.csv", row.names=FALSE)

# ---------- PSS Questionnaire ----------
pss_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("pss"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
pss_df  <- pivot_longer(pss_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
pss_df  <- pss_df  %>%
  filter(!is.na(resp))

save(pss_df, file="oxfordcovid_xue_2024_pss.Rdata")
write.csv(pss_df, "oxfordcovid_xue_2024_pss.csv", row.names=FALSE)

# ---------- PHQ Questionnaire ----------
phq_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("phq"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
phq_df  <- pivot_longer(phq_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
phq_df  <- phq_df  %>%
  filter(!is.na(resp))

save(phq_df, file="oxfordcovid_xue_2024_phq.Rdata")
write.csv(phq_df, "oxfordcovid_xue_2024_phq.csv", row.names=FALSE)

# ---------- GAD Questionnaire ----------
gad_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("gad"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
gad_df  <- pivot_longer(gad_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
gad_df  <-gad_df  %>%
  filter(!is.na(resp))

save(gad_df, file="oxfordcovid_xue_2024_gad.Rdata")
write.csv(gad_df, "oxfordcovid_xue_2024_gad.csv", row.names=FALSE)

# ---------- EDEQ Questionnaire ----------
edeq_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("edeq"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
edeq_df <- pivot_longer(edeq_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
edeq_df  <-edeq_df  %>%
  filter(!is.na(resp))

save(edeq_df, file="oxfordcovid_xue_2024_edeq.Rdata")
write.csv(edeq_df, "oxfordcovid_xue_2024_edeq.csv", row.names=FALSE)

# ---------- BRS Questionnaire ----------
brs_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("brs"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
brs_df <- pivot_longer(brs_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
brs_df  <- brs_df  %>%
  filter(!is.na(resp))

save(brs_df, file="oxfordcovid_xue_2024_brs.Rdata")
write.csv(brs_df, "oxfordcovid_xue_2024_brs.csv", row.names=FALSE)

# ---------- swemws Questionnaire ----------
swemws_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("swemws"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"))
swemws_df <- pivot_longer(swemws_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
swemws_df  <- swemws_df  %>%
  filter(!is.na(resp))

save(swemws_df, file="oxfordcovid_xue_2024_swemws.Rdata")
write.csv(swemws_df, "oxfordcovid_xue_2024_swemws.csv", row.names=FALSE)

# ---------- Activitiy and Technology Questionnaire ----------
at_df <- arc_df |>
  select(id, wave, starts_with("cov"), starts_with("media"), starts_with("activity"), -starts_with("covid"), -ends_with("complete"), -ends_with("timestamp"), -media_tv)
at_df <- pivot_longer(at_df, -c(id, wave, starts_with("cov")), names_to="item", values_to="resp")
at_df <- at_df %>%
  filter(!is.na(resp) & resp == floor(resp) & resp <= 5)

save(at_df, file="oxfordcovid_xue_2024_at.Rdata")
write.csv(at_df, "oxfordcovid_xue_2024_at.csv", row.names=FALSE)
