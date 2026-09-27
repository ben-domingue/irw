# verify_estrella_2023_psq18.R -- item axis for estrella_2023_psq18 (batch_ingest_0927).
#
# data/estrella_2023_hypermobility.py renames psq18_<b>_<j> -> psq18_<6(b-1)+j>
# (three Qualtrics blocks of six -> PSQ-18 items 1-18). Checks:
#   1. route 9: each source column's response counts (1-5) reproduce the table's
#      counts for its assigned code and no other code's;
#   2. the key-file statement shipped for psq18_n opens with the words RAND's
#      printed PSQ-18 form gives item n (psq18_survey.pdf, deposited as OSF 5pkwn),
#      so the numbering is RAND's, not just the deposit's.
# Response data: $IRW_RESP_DIR/<table>.csv while the table is only in a draft.
TABLE <- "estrella_2023_psq18"
here <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))))
it <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
src <- file.path(here, "..", "..", ".cache", "estrella_2023", "data.csv")
if (!file.exists(src)) download.file("https://osf.io/download/xenyq/", src, mode = "wb", quiet = TRUE)
s <- read.csv(src, colClasses = "character")
rd <- Sys.getenv("IRW_RESP_DIR")
d <- if (nzchar(rd)) read.csv(file.path(rd, paste0(TABLE, ".csv"))) else irw::irw_fetch(TABLE)

cols <- paste0("psq18_", rep(1:3, each = 6), "_", rep(1:6, 3))
codes <- paste0("psq18_", 1:18)
tab_live <- sapply(codes, function(i) tabulate(d$resp[d$item == i], 5))
tab_src <- sapply(cols, function(c) tabulate(suppressWarnings(as.integer(trimws(s[[c]]))), 5))
hit <- lapply(1:18, function(k) which(apply(tab_live, 2, function(x) all(x == tab_src[, k]))))
cat("1. response counts, source column vs table code\n")
for (k in 1:18) cat(sprintf("  %-10s %-26s -> %s\n", cols[k], paste(tab_src[, k], collapse = "/"),
                            paste(codes[hit[[k]]], collapse = ",")))
r1 <- all(lengths(hit) == 1) && all(unlist(hit) == 1:18)

# RAND PSQ-18 form, items 1-18, opening words (read from psq18_survey.pdf)
RAND <- c("Doctors are good about explaining", "I think my doctor", "The medical care I have been",
          "Sometimes doctors make me wonder", "I feel confident that I can get", "When I go for medical care",
          "I have to pay for more", "I have easy access", "Where I get medical care",
          "Doctors act too businesslike", "My doctors treat me", "Those who provide my medical care",
          "Doctors sometimes ignore", "I have some doubts", "Doctors usually spend plenty",
          "I find it hard to get an appointment", "I am dissatisfied with some things", "I am able to get medical care")
txt <- sapply(codes, function(i) unique(it$item_text[it$item == i]))
r2v <- mapply(function(t, p) startsWith(t, p), txt, RAND)
cat("2. shipped wording vs RAND item numbering:", sum(r2v), "/ 18 open with RAND's item-n words\n")
if (!all(r2v)) print(txt[!r2v])
cat(if (r1 && all(r2v)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
