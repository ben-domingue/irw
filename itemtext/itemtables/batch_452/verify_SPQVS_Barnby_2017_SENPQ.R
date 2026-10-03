# verify_SPQVS_Barnby_2017_SENPQ.R -- Step 5b check for SPQVS_Barnby_2017_SENPQ.
#
# Claim being verified (both mapping axes):
#   item axis   : SENPQn (n = 1..16) is the SenPQ item printed as number n, i.e. Opinio
#                 raw-export column Q(75+n), whose variable label is that item's wording.
#   option axis : resp 1..5 = Never, Occasionally, Sometimes, Very Often, Almost Always.
#
# Route 9 at the finest grain available: the study's RAW Opinio export
# (OSF j9ewt, SPEXCELrawdataR.xlsx) stores each answer as its label string, keyed by
# RespondentId, and the live IRW table keeps RespondentId as `id`. So every live
# (id, item, resp) cell can be compared with the raw label for the same respondent
# and question. A swap of any two items, or any permutation/flip of the resp levels,
# breaks cell-level agreement. A second check reads the question wording from the raw
# .sav variable labels and confirms it equals the shipped item_text for the same code.
# Also printed: the paper's own marker (PeerJ 10.7717/peerj.3149, p.11) that nobody
# answered '5' on items 3 and 7.

suppressMessages({library(irw); library(readxl); library(haven)})

TABLE <- "SPQVS_Barnby_2017_SENPQ"
tmp <- tempfile(); dir.create(tmp)
xl  <- file.path(tmp, "SPEXCELrawdataR.xlsx")
sv  <- file.path(tmp, "SPSPSSrawdataR.sav")
download.file("https://osf.io/download/4kgm7/", xl, mode = "wb", quiet = TRUE)
download.file("https://osf.io/download/q2d43/", sv, mode = "wb", quiet = TRUE)

KEY <- c("Never" = 1, "Occasionally" = 2, "Sometimes" = 3, "Very Often" = 4,
         "Almost Always" = 5)

live <- irw::irw_fetch(TABLE)
raw  <- read_excel(xl)
ok_all <- TRUE

# ---- item x option axis: per-respondent cell agreement --------------------------
long <- do.call(rbind, lapply(1:16, function(n) {
  data.frame(id = raw$RespondentId, item = paste0("SENPQ", n),
             lab = trimws(raw[[paste0("Q", 75 + n)]]), stringsAsFactors = FALSE)
}))
long$raw_resp <- unname(KEY[long$lab])
m <- merge(live[, c("id", "item", "resp")], long, by = c("id", "item"), all.x = TRUE)
cat(sprintf("live cells: %d ; matched to a raw respondent/question: %d\n",
            nrow(m), sum(!is.na(m$lab))))
agree <- tapply(m$resp == m$raw_resp, m$item, function(v) sum(v, na.rm = TRUE))
nn    <- tapply(m$resp, m$item, length)
ord <- paste0("SENPQ", 1:16)
cat(sprintf("%-8s %6s %6s\n", "item", "n", "agree"))
for (i in ord) cat(sprintf("%-8s %6d %6d\n", i, nn[i], agree[i]))
cat(sprintf("TOTAL    %6d %6d\n", sum(nn), sum(agree)))
if (sum(agree) != nrow(live)) ok_all <- FALSE

# The alternative mappings must do worse: next-item shift and flipped key.
# Pair each live item n with the raw answers to question n+1 (mod 16).
sl <- long
sl$item <- paste0("SENPQ", ((as.integer(sub("SENPQ", "", sl$item)) - 2) %% 16) + 1)
sh <- merge(live[, c("id", "item", "resp")], sl[, c("id", "item", "raw_resp")],
            by = c("id", "item"))
cat(sprintf("counter-check, items shifted by one: %d / %d cells agree\n",
            sum(sh$resp == sh$raw_resp, na.rm = TRUE), nrow(sh)))
# Every item against every OTHER raw question: the best off-diagonal pairing must
# fall short of full agreement, or the route would not separate that pair.
A <- sapply(ord, function(j) sapply(ord, function(i) {
  a <- merge(live[live$item == i, c("id", "resp")],
             long[long$item == j, c("id", "raw_resp")], by = "id")
  sum(a$resp == a$raw_resp, na.rm = TRUE)
}))
off <- A; diag(off) <- NA
cat(sprintf("diagonal agreement: min %d of 191; best off-diagonal pairing: %d of 191\n",
            min(diag(A)), max(off, na.rm = TRUE)))
if (max(off, na.rm = TRUE) >= min(diag(A))) ok_all <- FALSE
cat(sprintf("counter-check, resp key flipped (6 - k): %d / %d cells agree\n",
            sum(m$resp == 6 - m$raw_resp, na.rm = TRUE), nrow(m)))

# ---- words: raw .sav variable labels vs shipped item_text -----------------------
lbl <- sapply(1:16, function(n) attr(read_sav(sv)[[paste0("Q", 75 + n)]], "label"))
lbl <- gsub("â€™", "’", lbl)   # UTF-8 read as cp1252 mojibake
here <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) NULL)
if (is.null(here)) {
  a <- grep("^--file=", commandArgs(FALSE), value = TRUE)
  here <- if (length(a)) dirname(sub("^--file=", "", a[1])) else "."
}
it <- read.csv(file.path(here, paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
it <- unique(it[, c("item", "item_text")])
txt <- it$item_text[match(ord, it$item)]
same <- txt == lbl
cat(sprintf("shipped item_text == raw .sav label of Q(75+n): %d / 16\n", sum(same)))
if (!all(same)) { print(ord[!same]); ok_all <- FALSE }

# ---- paper marker ---------------------------------------------------------------
z <- table(live$item, live$resp)
cat(sprintf("count of resp=5 on SENPQ3: %d, SENPQ7: %d (paper: nobody answered 5 on items 3 and 7)\n",
            z["SENPQ3", "5"], z["SENPQ7", "5"]))
if (z["SENPQ3", "5"] != 0 || z["SENPQ7", "5"] != 0) ok_all <- FALSE

cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
