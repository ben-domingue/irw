# Paper: https://www.inderscienceonline.com/doi/abs/10.1504/IJHD.2023.131527
# Data: https://osf.io/psgk8/
#
# `Aspirations_CFA.sav` is TWO INDEPENDENT SAMPLES STACKED: Study 1 (265
# respondents) on top of Study 2 (208), with `StudyNo` separating them and
# `ParticipantNo` restarting at 1 in each. So participant 1 of Study 1 and
# participant 1 of Study 2 are different people, and every one of Study 2's 208
# numbers collides with a Study 1 number.
#
# This script used `ParticipantNo` as `id` unchanged, which is why the published
# table carries 208 x 35 = 7,280 id+item pairs appearing twice and 57 x 35 =
# 1,995 appearing once (#1842, block H). Those were read as two waves or as
# duplication; they are neither, and deduping them would have deleted 208
# people. The source settles it: for the 208 colliding numbers, `Age` agrees on
# 22 and `Gender` on 106 -- chance, for a binary variable -- and only 31.9% of
# item responses match.
#
# Fixed the way the other id collisions in #1842 were (agreed 2026-09-02):
# namespace `id` with the sample label, and keep the label as its own `cov_`
# column. The separator "_" cannot occur in a source id, which is an integer.
library(haven)
library(dplyr)
library(tidyr)

df <- read_sav('Aspirations_CFA.sav')

stopifnot(all(c("StudyNo", "ParticipantNo") %in% names(df)))
## The collision this file exists to fix must actually be there: if a future
## revision of the source numbers participants uniquely, namespacing would be
## wrong rather than merely unnecessary.
stopifnot(anyDuplicated(df$ParticipantNo) > 0)

df <- df |>
  mutate(cov_study = paste0("s", as.integer(StudyNo)),
         id        = paste0(cov_study, "_", as.integer(ParticipantNo))) |>
  select(id, cov_study, starts_with("Asp"))

stopifnot(!anyDuplicated(df$id))

df <- pivot_longer(df, cols = c(-id, -cov_study),
                   values_to = "resp", names_to = "item") |>
  filter(!is.na(resp)) |>
  select(id, item, resp, cov_study)

## No id+item pair may repeat once the samples are namespaced. This is the
## measure #1842 is closed on.
stopifnot(!anyDuplicated(df[, c("id", "item")]))

save(df, file = "Aspirations_Sonmez_2022.Rdata")
write.csv(df, "Aspirations_Sonmez_2022.csv", row.names = FALSE)
