library(tidyr)
library(dplyr)

df <- read.csv("Data_total.csv", sep = ";")

df$id <- seq(1, nrow(df))

df <- df %>%
  rename(cov_age = Age, cov_sex = Sex, cov_education = Education,
         cov_neurologist = Neurologist, cov_ophthalmologist = Ophthalmologist,
         cov_psychiatrist = Psychiatrist)

svk <- df %>%
  select(id, starts_with("cov"), starts_with("SVK"), -ends_with("CAT"), -c("SVK_Total", "SVK_limitations", "SVK_Factor1", "SVK_Factor2", "SVK_Factor3")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

cvs <- df %>%
  select(id, starts_with("cov"), starts_with("CVS"), -CVS_Total) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

vfq <- df %>%
  select(id, starts_with("cov"), starts_with("VFQ"), -c("VFQ.A1":"VFQ.A13"), -starts_with("VFQ_")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

feda <- df %>%
  select(id, starts_with("cov"), starts_with("FEDA"), -FEDA_total) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

brief <- df %>%
  select(id, starts_with("cov"), starts_with("BRIEF.")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

user <- df %>%
  select(id, starts_with("cov"), starts_with("USER.")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

dass <- df %>%
  select(id, starts_with("cov"), starts_with("DASS.")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))

sims <- df %>%
  select(id, starts_with("cov"), starts_with("SIMS.")) %>%
  pivot_longer(-c(id, starts_with("cov")),
               names_to = "item",
               values_to = "resp") %>%
  mutate(resp = ifelse(resp == "#NULL!", NA, resp))


write.csv(svk, "neurodegenerative_huizinga_2019_svc.csv", row.names = FALSE)
write.csv(cvs, "neurodegenerative_huizinga_2019_cvc.csv", row.names = FALSE)
write.csv(vfq, "neurodegenerative_huizinga_2019_vfq.csv", row.names = FALSE)
write.csv(feda, "neurodegenerative_huizinga_2019_feda.csv", row.names = FALSE)
write.csv(brief, "neurodegenerative_huizinga_2019_brief.csv", row.names = FALSE)
write.csv(user, "neurodegenerative_huizinga_2019_user.csv", row.names = FALSE)
write.csv(dass, "neurodegenerative_huizinga_2019_dass.csv", row.names = FALSE)
write.csv(sims, "neurodegenerative_huizinga_2019_sims.csv", row.names = FALSE)



