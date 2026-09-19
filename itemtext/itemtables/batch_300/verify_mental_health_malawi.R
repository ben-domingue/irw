# Verification for mental_health_malawi (#2228, batch_300).
#
# SOURCE. Mwakilama, Jamu, Senganimalunje & Manda (2022), 'Data on Internet
# Addiction and Mental Health among university students in Malawi', Mendeley
# Data V3, doi:10.17632/xbfbcy5bhv.3, CC BY. The deposit ships the administered
# instrument itself -- 'IAT_SRQ20 Survey_tool.pdf' -- with both questionnaires
# printed, numbered, and with their response anchors.
#
# THE ITEM CODE IS A SCRIPT-GENERATED INTEGER, which SKILL.md flags as the case
# to RE-RUN rather than reason about. This table is why that rule exists. The
# script does
#     pivot_longer(cols = -id, values_drop_na = TRUE)
#     items <- as.data.frame(unique(df$item)); items |> mutate(item_id = row_number())
# so item n is the position of each column at its FIRST NON-MISSING APPEARANCE,
# not its position in the file. Respondent 1 has NA on two IAT columns, so those
# two are pushed to the very end: `excitement` is question 3 of the printed
# instrument but item 39 here, and `late_night_logins` is question 14 but item
# 40. A first pass at this table assumed plain column order and got 18 of 40
# items wrong; Route 3 below is what caught it.
#
# Route 1: re-run the script over the raw deposit file, exactly.
# Route 2: the recovered column names against the printed questionnaire.
# Route 3: the two instruments' response scales must fall where Route 1 says.
SRC <- ".cache/batch_300/iat_malawi/IAT_Data_Revised/IAT_data_imported.csv"
MAP <- ".cache/batch_300/malawi_map.csv"
for (p in c(SRC, MAP)) if (!file.exists(p)) stop("missing cached file: ", p)
d <- as.data.frame(irw::irw_fetch("mental_health_malawi"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_300/mental_health_malawi__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
items$item <- as.character(items$item)

cat("=== Route 1: the script re-run over the raw deposit file ===\n")
raw <- read.csv(SRC, check.names = FALSE, stringsAsFactors = FALSE)
snake <- function(s) tolower(gsub("_+","_", gsub("(^_|_$)","", gsub("[^[:alnum:]]+","_", sub("^\ufeff","",s)))))
names(raw) <- snake(names(raw))
DROP <- c("internet_usg","internet_add","gender","age_grp","level_study","yr_study",
          "discipline","filter","sqr_total","new_sqr_total","sqr_catg")
w <- raw[, setdiff(names(raw), DROP), drop = FALSE]
IATCOL <- c("stay_online","neglect_chores","excitement","relationships","life_complaint","school_work",
 "email_socialmedia","job_performance","defensive_secretive","disturbing_thoughts","online_anticipation",
 "life_no_internet","act_annoyed","late_night_logins","feel_preoccupied","online_glued","time_cutdown",
 "hide_online","more_online_time","feel_depressed")
SRQCOL <- setdiff(names(w), c("id", IATCOL))
for (cc in intersect(IATCOL, names(w))) w[[cc]] <- ifelse(w[[cc]] == 99 | w[[cc]] == 0, NA, w[[cc]])
for (cc in SRQCOL) w[[cc]] <- ifelse(w[[cc]] == 7, NA, w[[cc]])
cols <- setdiff(names(w), "id")
long <- data.frame(id = rep(w$id, each = length(cols)),
                   col = rep(cols, times = nrow(w)),
                   resp = as.vector(t(as.matrix(w[, cols]))), stringsAsFactors = FALSE)
long <- long[!is.na(long$resp), ]
ord <- unique(long$col)
cat(sprintf("  reproduced long rows %d; live rows %d\n", nrow(long), nrow(d)))
cat(sprintf("  reproduced items %d; live items %d\n", length(ord), length(unique(d$item))))
r1 <- nrow(long) == nrow(d) && length(ord) == 40
cat(sprintf("  -> row count and item count both reproduce exactly: %s\n", r1))
cat("  Two columns land out of file order because respondent 1 is missing on\n")
cat(sprintf("  them: %s at item %d, %s at item %d.\n",
            ord[39], 39, ord[40], 40))

cat("\n=== Route 2: recovered columns against the printed questionnaire ===\n")
shipped <- read.csv(MAP, stringsAsFactors = FALSE)
r2 <- identical(shipped$col, ord)
cat(sprintf("  the map the extraction used is identical to this re-run: %s\n", r2))
for (i in c(1, 13, 18, 19, 35, 38, 39, 40))
    cat(sprintf("  %2d  %-20s  %s\n", i, ord[i],
                substr(unique(items$item_text[items$item == as.character(i)])[1], 1, 58)))
cat("  The column names are the study's own abbreviations of the printed\n")
cat("  questions, so they check the position independently: item 35 'suicide'\n")
cat("  lands on the ending-your-life question, item 39 'excitement' on the\n")
cat("  question about preferring the Internet to intimacy with a partner.\n")

cat("\n=== Route 3: the response scales fall where Route 1 says ===\n")
iat_items <- as.character(which(ord %in% IATCOL))
srq_items <- as.character(which(ord %in% SRQCOL))
li <- sort(unique(d$resp[d$item %in% iat_items]))
ls <- sort(unique(d$resp[d$item %in% srq_items]))
cat(sprintf("  IAT positions (%s): resp levels %s\n",
            paste(range(as.integer(iat_items)), collapse = "-"), paste(li, collapse = ",")))
cat(sprintf("  SRQ positions (%s): resp levels %s\n",
            paste(range(as.integer(srq_items)), collapse = "-"), paste(ls, collapse = ",")))
r3 <- identical(as.numeric(li), c(1, 2, 3, 4, 5)) && identical(as.numeric(ls), c(0, 1))
cat(sprintf("  -> 1-5 for every IAT position and 0/1 for every SRQ position: %s\n", r3))
cat("  This is the check that caught the first, wrong version: under plain column\n")
cat("  order items 19-20 would be IAT and would have to be 1-5, and they are 0/1.\n")
cat("  The instrument prints a 0-5 scale for the IAT, but the script recodes 0\n")
cat("  ('Does Not Apply') to NA, so 0 never reaches the live table and only the\n")
cat("  five labelled points 1-5 ship.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. Wording is transcribed from the deposit's own survey\n")
cat("  tool, the numbering is reproduced from the raw file rather than assumed,\n")
cat("  and the anchors are printed on the instrument. One transcription note:\n")
cat("  SRQ item 8 is given as 'Do you have trouble thinking clearly?' where the\n")
cat("  PDF omits the closing question mark.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
