#!/usr/bin/env Rscript
# duckmayr_2023_immigration -- ten immigration-policy statements, Lucid sample
#
# Fielded February-March 2020 (Lucid, US adults).
# Source paper: Duck-Mayr, J., & Montgomery, J. (2023). Ends against the middle:
#   Measuring latent traits when opposites respond the same way for antithetical
#   reasons. Political Analysis, 31(4), 606-625. doi:10.1017/pan.2022.33
# Data: Harvard Dataverse doi:10.7910/DVN/HXORK9 (V1, 2022-11-01), file
#   lucid_data.tab (file id 6573383), fetched in its original CSV format.
# License: CC0 1.0 (deposit). The article itself is not open; nothing from it is
#   stored here.
#
# Usage:
#   Rscript data/duckmayr_2023_immigration.R
#
# UNFOLDING DATA -- DO NOT REVERSE-KEY. The ten statements were written to sit
# at different points on a liberal-conservative immigration dimension, and the
# paper's point is that agreement is NOT monotone in the trait: a middle
# statement (IMM_2, "stay legally ... only if certain requirements are met") is
# rejected by respondents at both ends for opposite reasons. "Reverse keying"
# assumes a monotone item, so it does not apply; every item keeps its recorded
# direction (higher resp = more agreement). Fit an ideal-point model (GGUM,
# e.g. the authors' bggum package), not a dominance model, if unfolding is the
# question. Reproduced here: share agreeing with IMM_2 is 0.44 among the very
# liberal, 0.59 slightly conservative, 0.51 very conservative, and IMM_2
# correlates ~0 with the end statements (IMM_1 -0.09, IMM_3 0.04, IMM_7 0.00)
# while the ends correlate -0.62 with each other (IMM_1 x IMM_3).
#
# resp: 0 Strongly disagree, 1 Somewhat disagree, 2 Neither disagree nor agree,
#   3 Somewhat agree, 4 Strongly agree -- the authors' own 0-4 coding
#   (04-immigration-application.R). 8 blank item responses are dropped.
#
# Respondents: the authors' analysis sample, 2,621 people, reproduced exactly
# from their replication script 04-immigration-application.R:
#   1. Attention checks -- keep only respondents who passed all three screeners:
#      SCREENER_FEELINGS == "Proud,None of the above",
#      SCREENER_INTEREST == "Extremely interested,Not interested at all",
#      SCREENER_COLORS   == "Red,Green".            3,282 -> 2,801
#   2. The authors' "straight-lining" rule -- drop anyone whose ten answers all
#      lie in {0,1,2} or all lie in {2,3,4} (never agreed with anything, or
#      never disagreed with anything). Note this is broader than identical
#      answers. A blank answer makes the test FALSE, as in their code.
#                                                    2,801 -> 2,621
#
# Covariates:
#   cov_ideology  7-point self-placement (IDEO): 1 Very liberal ... 4 Moderate;
#                 middle of the road ... 7 Very conservative. Blank -> NA.
#   cov_party_id  7-point party ID built ANES-style from PID, R_STRENGTH,
#                 D_STRENGTH and LEANERS: 1 strong Democrat, 2 not very strong
#                 Democrat, 3 Independent/Other leaning Democratic, 4
#                 Independent/Other with no leaner answer, 5 leaning Republican,
#                 6 not very strong Republican, 7 strong Republican. The leaner
#                 item offered only Democratic/Republican, so 4 is people who
#                 skipped it. Blank PID -> NA. (The authors' own party_id is a
#                 coarser -2..2 version of this; it is not reproduced.)
#   cov_age_band  AGE as asked, in bands: 18-29, 30-39, ..., 70-79, 80+.
#   cov_gender    GENDER: Female / Male / Other. The "Other" free text is dropped.
#
# Privacy -- dropped, never read into the output: IPAddress, LocationLatitude,
# LocationLongitude, StartDate, EndDate, RecordedDate, ResponseId, rid (the
# Lucid platform respondent id), Recipient*/ExternalReference/ContactId,
# Duration, all free-text fields (GENDER_3_TEXT, ETHNICITY_8_TEXT), and
# STATE_1. id is a new sequential integer in source row order, not any source
# identifier.
#
# Not carried (could be separate tables or covariates later): ETHNICITY and
# EDUCATION; the adaptive Big Five batteries (*_CAT, *_FINISH, q1-q100) and
# TIPI in the same file; and the deposit's House/Senate roll calls and Mexican
# IFE council votes, which are classic unfolding data in their own right.

suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(tidyr))

# ---------------------------------------------------------------- paths -----

script_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- grep("^--file=", a, value = TRUE)
  if (length(f)) return(dirname(normalizePath(sub("^--file=", "", f[1]))))
  getwd()
}

OUT_DIR <- file.path(script_dir(), "..", "automated_finding", "irw_output")
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
OUT_DIR <- normalizePath(OUT_DIR)

SRC_URL <- "https://dataverse.harvard.edu/api/access/datafile/6573383?format=original"
SRC <- file.path(tempdir(), "lucid_data.csv")
if (!file.exists(SRC)) download.file(SRC_URL, SRC, mode = "wb", quiet = TRUE)

# ----------------------------------------------------------------- read -----

# Qualtrics export: row 1 is question wording, row 2 is ImportId JSON. Both fail
# the screeners, so step 1 removes them, as it does in the authors' code.
keep_cols <- c("SCREENER_FEELINGS", "SCREENER_INTEREST", "SCREENER_COLORS",
               "AGE", "GENDER", "PID", "R_STRENGTH", "D_STRENGTH", "LEANERS",
               "IDEO", paste0("IMM_", 1:10))
raw <- read.csv(SRC, stringsAsFactors = FALSE, check.names = FALSE)
raw <- raw[, keep_cols]            # every identifier column is dropped here
n_raw <- nrow(raw) - 1L            # excluding the wording row

# --------------------------------------------------------------- filters -----

attentive <- raw$SCREENER_FEELINGS == "Proud,None of the above" &
             raw$SCREENER_INTEREST == "Extremely interested,Not interested at all" &
             raw$SCREENER_COLORS   == "Red,Green"
d <- raw[attentive, ]
n_att <- nrow(d)

opts <- c("Strongly disagree", "Somewhat disagree", "Neither disagree nor agree",
          "Somewhat agree", "Strongly agree")
R <- sapply(d[, paste0("IMM_", 1:10)], match, opts) - 1L
str8 <- apply(R, 1, function(x) all(x %in% 0:2) | all(x %in% 2:4))
d <- d[!str8, ]
R <- R[!str8, ]
stopifnot(nrow(d) == 2621L)

# ------------------------------------------------------------ covariates -----

ideo_levs <- c("Very liberal", "Somewhat liberal", "Slightly liberal",
               "Moderate; middle of the road", "Slightly conservative",
               "Somewhat conservative", "Very conservative")
pid7 <- with(d, case_when(
  PID == "Democrat"   & D_STRENGTH == "A strong Democrat"          ~ 1L,
  PID == "Democrat"   & D_STRENGTH == "Not a very strong Democrat" ~ 2L,
  PID %in% c("Independent", "Other") & LEANERS == "Democratic"     ~ 3L,
  PID %in% c("Independent", "Other") & LEANERS == "Republican"     ~ 5L,
  PID %in% c("Independent", "Other")                               ~ 4L,
  PID == "Republican" & R_STRENGTH == "Not a very strong Republican" ~ 6L,
  PID == "Republican" & R_STRENGTH == "A strong Republican"        ~ 7L,
  TRUE ~ NA_integer_))

wide <- data.frame(
  id           = seq_len(nrow(d)),
  R,
  cov_ideology = match(d$IDEO, ideo_levs),
  cov_party_id = pid7,
  cov_age_band = na_if(d$AGE, ""),
  cov_gender   = na_if(d$GENDER, ""),
  check.names  = FALSE
)

df <- wide |>
  pivot_longer(starts_with("IMM_"), names_to = "item", values_to = "resp") |>
  filter(!is.na(resp)) |>
  select(id, item, resp, cov_ideology, cov_party_id, cov_age_band, cov_gender) |>
  arrange(id, factor(item, levels = paste0("IMM_", 1:10)))

# ---------------------------------------------------------------- checks -----

stopifnot(n_distinct(df$id) == 2621L, n_distinct(df$item) == 10L,
          all(df$resp %in% 0:4), !anyDuplicated(df[, c("id", "item")]))
cat(sprintf("filters: %d raw -> %d attentive -> %d after straight-lining\n",
            n_raw, n_att, nrow(d)))

agree2 <- tapply(R[, "IMM_2"] >= 3, wide$cov_ideology, mean, na.rm = TRUE)
cat("IMM_2 share agreeing by ideology 1..7:", sprintf("%.2f", agree2), "\n")
cr <- cor(R, use = "pairwise")
cat(sprintf("cor IMM_2 x IMM_1/IMM_3/IMM_7: %.2f %.2f %.2f; IMM_1 x IMM_3: %.2f\n",
            cr["IMM_2", "IMM_1"], cr["IMM_2", "IMM_3"], cr["IMM_2", "IMM_7"],
            cr["IMM_1", "IMM_3"]))

out <- file.path(OUT_DIR, "duckmayr_2023_immigration.csv")
write.csv(df, out, row.names = FALSE, na = "")
cat(sprintf("duckmayr_2023_immigration: rows=%d ids=%d items=%d resp=%d-%d\n",
            nrow(df), n_distinct(df$id), n_distinct(df$item),
            min(df$resp), max(df$resp)))
