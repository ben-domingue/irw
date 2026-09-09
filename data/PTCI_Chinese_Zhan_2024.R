# Paper: https://psycnet.apa.org/record/2024-52701-001
# Data: https://osf.io/tj8rh/
library(haven)
library(dplyr)
library(tidyr)
library(foreign)

# ------ Process Dataset 1 ------
#
# `ID` IS NOT A PERSON. `PTCI_data.sav` holds 2,375 respondents under 1,206
# distinct `ID` values -- 1,866 rows share a number with another row (#1842).
# It is a collision, not repeated measurement, and three things in the source
# say so together:
#
#   * `sex` differs within an ID for 461 numbers and `age` for 687;
#   * `T_ptci` equals that row's own item sum on all 2,375 rows, so every row is
#     a complete, self-consistent respondent record;
#   * not one whole row is byte-identical to another.
#
# The published table used `ID` alone and so merged up to four respondents into
# one. The block H prescription -- dedupe 17,394 rows, chase 21,183 -- would
# have deleted roughly 1,169 people.
#
# `C2` is the sample stratum (senior / high / adult; `C1` is its adolescent-adult
# collapse, and nests inside it), and numbering restarts within each. Namespacing
# by it, per the rule agreed 2026-09-02, resolves most of the collision; 125
# numbers still carry two sexes within one stratum, so a finer unit the file does
# not carry -- school or class -- is also in play, and those take an occurrence
# suffix. Every row ends up its own respondent, which is what the T_ptci identity
# says it is.
PTCI_SAMPLE <- c("1" = "senior", "2" = "high", "3" = "adult")

df <- read_sav("PTCI_data.sav")

stopifnot(all(c("ID", "C2") %in% names(df)))
stopifnot(anyDuplicated(df$ID) > 0)   # the collision this file exists to fix

df$cov_sample <- unname(PTCI_SAMPLE[as.character(as.integer(df$C2))])
stopifnot(!any(is.na(df$cov_sample)))
df$id <- paste0(df$cov_sample, "_", as.integer(df$ID))
rep_id <- df$id %in% df$id[duplicated(df$id)]
if (any(rep_id)) {
  df$id[rep_id] <- paste0(df$id[rep_id], ".",
                          ave(seq_len(sum(rep_id)), df$id[rep_id], FUN = seq_along))
  message(sprintf("PTCI: %d number(s) repeated within a stratum; suffixed %d row(s)",
                  length(unique(sub("\\..$", "", df$id[rep_id]))), sum(rep_id)))
}
stopifnot(!anyDuplicated(df$id))

df <- df |>
  select(id, cov_sample, starts_with("PTCI"))
df[] <- lapply(df, function(col) { # Remove column labels for each column
  attr(col, "label") <- NULL
  return(col)
})
df <- pivot_longer(df, cols=c(-id, -cov_sample), names_to = "item", values_to = "resp")

# ------ Process Dataset 2 ------
# A separate retest sample, numbered 3001-3117, with no overlap against dataset
# 1's numbers and no repeats of its own. Labelled so the two are distinguishable
# once they are stacked.
#
# Note for later: this file also carries the ptci*_retest columns -- a real
# second occasion, 61 respondents -- which this script drops. Adding them needs
# a `wave` column and is a change of shape, so it is not done here.
df_retest <- read.spss("./PTCI_retest.sav", to.data.frame = TRUE, use.value.labels = FALSE)
df_retest <- df_retest |>
  rename(id=ID_retest) |>
  select(-YN_lec, -YN, -grade, -class, -sex, -age, -location, -fedu, -medu, 
         -TE_YN, -TE_Rest_YN, -filter_., -PCTI_Total_test, -PCTI_Total_rtest, -B_PCTI_Total_test,
         -B_PCTI_Total_rtest, -blame_test, -blame_retest, -self_retest, -word_test,
         -word_retest, -self_test, -starts_with("B_"))

# ---- Process PTCI Dataset ----
ptci_df <- df_retest |>
  select(id, starts_with("ptci"))

ptci_test_df <- ptci_df |>
  select(id, ends_with("_test"))
colnames(ptci_test_df) <- gsub('_test$', '', colnames(ptci_test_df))
ptci_test_df$cov_sample <- "retest"
ptci_test_df$id <- paste0("retest_", as.integer(ptci_test_df$id))
stopifnot(!anyDuplicated(ptci_test_df$id))
ptci_test_df <- pivot_longer(ptci_test_df, cols=c(-id, -cov_sample),
                             names_to = "item", values_to = "resp")

df <- rbind(df, ptci_test_df)
df <- df[!is.na(df$resp), c("id", "item", "resp", "cov_sample")]

## No id+item pair may repeat once the strata are namespaced. This is the
## measure #1842 is closed on.
stopifnot(!anyDuplicated(df[, c("id", "item")]))
save(df, file="PTCI_Chinese_Zhan_2024.Rdata")
write.csv(df, "PTCI_Chinese_Zhan_2024.csv", row.names=FALSE)
