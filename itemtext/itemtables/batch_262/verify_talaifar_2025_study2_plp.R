# verify_talaifar_2025_study2_plp.R -- Step 5b mapping check (batch_262).
#
# Claim: each live IRW item code (smsinnum, loc_home, maxdistance, ...) is the Qualtrics
# column of perceiver_ratings_raw_data.csv (OSF rf9k8, https://osf.io/download/zhynf/)
# that the processing script's STUDY2_ITEMS dict says it is, and therefore carries that
# column's own header-row label as item_text.
#
# The IRW code is NOT the source column name: data/talaifar_2025_lifestyle_polarization.py
# renames communication1_1 -> smsinnum etc. through a hand-written dict, so the code keeps
# no trace of the source column and a mis-keyed dict entry would be invisible from the
# output alone. Two independent checks:
#   (1) PER-RESPONDENT VECTOR MATCH. For every live item, compare its id -> resp vector
#       against EVERY one of the 61 rated Qualtrics columns (after the script's own
#       exclusions). A correct mapping matches exactly one column, and it is the dict's.
#       This distinguishes every item from every other item.
#   (2) The script's dict is compared, pair by pair, against the authors' own rename in
#       their deposited analysis code (OSF rf9k8, Study 2/Code/correlational_categorical_
#       accuracy.R, https://osf.io/download/quhw9/).
# What this does NOT establish: that the authors' choice of sensing-variable NAME for each
# question is semantically apt (e.g. "Who travels a further total distance?" is keyed to
# `maxdistance`, "...further distance between locations?" to `distance`). That naming is
# the authors' own and is reproduced, not adjudicated, here.

suppressMessages(library(irw))

TABLE <- "talaifar_2025_study2_plp"

DICT <- c(
  communication1_1 = "smsinnum", communication1_2 = "smsoutnum", communication1_3 = "smsinlen",
  communication1_4 = "smsoutlen", communication1_5 = "audioconvonum", communication1_6 = "audioconvodur",
  communication1_7 = "callinnum", communication1_8 = "calloutnum", communication1_9 = "callindur",
  communication1_10 = "calloutdur", communication2_1 = "ppl_friends", communication2_2 = "ppl_alone",
  communication2_3 = "ppl_family", communication2_4 = "ppl_roommates", communication2_5 = "ppl_sigother",
  communication2_6 = "ppl_strangers", communication2_11 = "act_talkingtextingsocializing",
  leisure1_9 = "loc_friendshouse", leisure1_1 = "timehome", leisure1_2 = "loc_home",
  leisure1_3 = "act_choreserrands", leisure1_4 = "act_restnap", leisure1_5 = "loc_bar",
  leisure1_6 = "loc_frat", leisure1_7 = "loc_religious", leisure1_8 = "loc_cafe", leisure1_10 = "loc_store",
  leisure2_1 = "audioampmean", leisure2_2 = "audiovoice", leisure2_3 = "unlockdur", leisure2_4 = "unlocknum",
  leisure2_5 = "act_browsinginternetsocialmedia", leisure2_6 = "act_watchtvmovies",
  work1_1 = "act_working", work1_2 = "act_studyingreading", work1_3 = "act_classmeeting",
  work1_4 = "loc_campus", work1_5 = "ppl_students", work1_6 = "ppl_coworkers", work1_7 = "loc_library",
  work1_8 = "loc_work", work1_9 = "act_commuting",
  movement1_1 = "activitywalk", movement1_2 = "activitystationary", movement1_3 = "activitybike",
  movement1_4 = "activityrun", movement1_5 = "act_exercising", movement1_6 = "loc_gym",
  movement1_8 = "routine_index", movement1_9 = "timeloc", movement1_10 = "locent", movement1_11 = "normlocent",
  movement2_1 = "actlevel", movement2_2 = "loc", movement2_3 = "locvis", movement2_4 = "maxdistance",
  movement2_5 = "distance", movement2_6 = "maxdistancehome", movement2_7 = "transitiontime",
  movement2_8 = "activityvehicle", movement2_9 = "loc_vehicle")

ok <- TRUE

# ---- source data -------------------------------------------------------------------
tmp <- tempfile(fileext = ".csv")
download.file("https://osf.io/download/zhynf/", tmp, quiet = TRUE, mode = "wb")
all <- read.csv(tmp, check.names = FALSE, stringsAsFactors = FALSE, colClasses = "character")
hdr <- all[1, ]                 # Qualtrics row 2: question labels
raw <- all[-(1:2), ]            # drop label row and ImportId row
# the processing script's exclusions, verbatim
raw <- raw[!(raw$id == "40607" | raw$Progress == "11"), ]
raw <- raw[raw$id != "41799", ]
raw <- raw[suppressWarnings(as.numeric(raw[["Duration (in seconds)"]])) > 120, ]
cat(sprintf("source respondents after exclusions: %d\n", nrow(raw)))

rated <- grep("^(communication|leisure|work|movement)[0-9]+_[0-9]+$", names(raw), value = TRUE)
rated <- setdiff(rated, "communication1_11")          # attention check, not an item
cat(sprintf("rated Qualtrics columns in source: %d\n", length(rated)))

# ---- live data ---------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$id <- as.character(d$id)
cat(sprintf("live rows: %d, live ids: %d, live items: %d\n\n",
            nrow(d), length(unique(d$id)), length(unique(d$item))))

key <- function(ids, v) {
  keep <- !is.na(v)
  s <- paste(ids[keep], sprintf("%.2f", v[keep]))
  paste(sort(s), collapse = ";")
}
src_keys <- vapply(rated, function(col)
  key(raw$id, suppressWarnings(as.numeric(raw[[col]]))), "")

cat(sprintf("%-32s %-18s %-18s %5s %7s  %s\n", "live item", "dict column", "matched column(s)", "n", "mean", "source label"))
nmatch <- 0
for (col in names(DICT)) {
  it <- DICT[[col]]
  sub <- d[d$item == it, ]
  lk <- key(sub$id, as.numeric(sub$resp))
  hit <- names(src_keys)[src_keys == lk]
  good <- length(hit) == 1 && hit == col
  if (good) nmatch <- nmatch + 1 else ok <- FALSE
  lab <- sub("^[a-z0-9]+ - ", "", hdr[[col]])
  cat(sprintf("%-32s %-18s %-18s %5d %7.3f  %s%s\n", it, col,
              if (length(hit)) paste(hit, collapse = ",") else "<none>",
              nrow(sub), mean(as.numeric(sub$resp)), lab, if (good) "" else "   <-- MISMATCH"))
}
cat(sprintf("\n(1) per-respondent vector match: %d / %d live items match exactly one source column, the dict's\n",
            nmatch, length(DICT)))
if (length(unique(src_keys)) != length(src_keys)) {
  cat("    WARNING: two source columns have identical response vectors -- route cannot separate them\n")
  ok <- FALSE
}
extra <- setdiff(unique(d$item), DICT)
if (length(extra)) { cat("    live items not in dict:", extra, "\n"); ok <- FALSE }

# ---- (2) authors' own rename ---------------------------------------------------------
rtmp <- tempfile(fileext = ".R")
download.file("https://osf.io/download/quhw9/", rtmp, quiet = TRUE, mode = "wb")
rl <- readLines(rtmp, warn = FALSE)
m <- regmatches(rl, regexec("'([A-Za-z_]+)_daily'\\s*=\\s*'([a-z]+[0-9]+_[0-9]+)'", rl))
m <- do.call(rbind, lapply(m[lengths(m) == 3], function(x) x[2:3]))
auth <- setNames(m[, 1], m[, 2])
agree <- sum(auth[names(DICT)] == DICT, na.rm = TRUE)
cat(sprintf("(2) authors' rename in correlational_categorical_accuracy.R: %d pairs parsed; %d / %d agree with the IRW dict\n",
            nrow(m), agree, length(DICT)))
if (agree != length(DICT) || nrow(m) != length(DICT)) ok <- FALSE

cat("\nNot established: whether each sensing-variable name the authors chose fits its question's wording.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
