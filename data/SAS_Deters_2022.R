# Paper: https://osf.io/ztycp/
# Data: https://osf.io/ztycp/
#
# `id` IS NOT A PERSON. `SAmb_R.csv` pools twenty semesters of a university
# subject pool, and the participant number restarts within each: 1,526 numbers
# across 7,096 rows, one number used up to 14 times (#1842).
#
# This is a collision, not repeated measurement, and the source proves it.
# Keyed on `id` alone, 456 numbers carry more than one `gender`, 1,095 more than
# one `age` and 1,003 more than one `ethnic`. Keyed on `id` + `semester`:
#
#            key            groups   ids w/ 2 genders   2 ages   2 ethnicities
#   id                       1,526              456      1,095          1,003
#   id + semester            7,088                0          1              2
#
# Zero. So the number identifies a person only within its semester, and the
# published table -- which used `id` alone -- merged up to fourteen students
# into one respondent. The block H prescription to dedupe it would have deleted
# them outright.
#
# Namespaced per the rule agreed 2026-09-02: prefix `id` with the sample label
# and keep the label as its own `cov_` column.
#
# Seven (id, semester) groups still hold more than one row, and those are
# collisions too rather than duplicates -- every one has distinct responses, and
# two are unambiguous (id 2319 in semester 59 is aged 18.28 and 24.86 with two
# different ethnicities; id 2553 likewise differs on ethnicity). They take an
# occurrence suffix, as PEPABAS2C's did.
#
# Not shipped, but available in the source if wanted later: gender, age and
# ethnic, which are what identify these as separate people.
library(dplyr)
library(tidyr)
library(haven)

df <- read.csv("SAmb_R.csv")

stopifnot(all(c("id", "semester") %in% names(df)))
stopifnot(anyDuplicated(df$id) > 0)   # the collision this file exists to fix

df <- df |>
  mutate(cov_semester = as.integer(semester),
         .person      = paste0("s", cov_semester, "_", as.integer(id)))

## Within-semester repeats: distinct people sharing a number. Suffix by
## occurrence -- the order is arbitrary and they are anonymous; the point is
## only that they stop being one person. "." cannot occur in the source id,
## which is an integer.
rep_person <- df$.person %in% df$.person[duplicated(df$.person)]
if (any(rep_person)) {
  df$.person[rep_person] <- paste0(df$.person[rep_person], ".",
                                   ave(seq_len(sum(rep_person)),
                                       df$.person[rep_person], FUN = seq_along))
  message(sprintf("SAS_Deters_2022: %d number(s) repeated within a semester; suffixed %d row(s)",
                  length(unique(sub("\\..$", "", df$.person[rep_person]))),
                  sum(rep_person)))
}
df$id <- df$.person
stopifnot(!anyDuplicated(df$id))

df <- df |>
  select(id, cov_semester, starts_with("samb"), -SAmb_tot) |>
  pivot_longer(cols = c(-id, -cov_semester), names_to = "item", values_to = "resp") |>
  filter(!is.na(resp)) |>
  select(id, item, resp, cov_semester)

## No id+item pair may repeat once the semesters are namespaced. This is the
## measure #1842 is closed on.
stopifnot(!anyDuplicated(df[, c("id", "item")]))

save(df, file="SAS_Deters_2022.Rdata")
write.csv(df, "SAS_Deters_2022.csv", row.names=FALSE)
