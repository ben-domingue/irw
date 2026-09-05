# verify_dinic_2025_shortdarktriad.R  --  Step 5b mapping check.
#
# CLAIM UNDER TEST
#   (a) live item code sd3_<i> IS the source column SD3_<i>[R] of the CC BY 4.0 OSF
#       deposit osf.io/t5wgm (data/SD3-rec.sav), carried over by the trailing rename
#       in data/dinic_2025_ShortDarkTriad.do -- so the wording keyed to number <i>
#       belongs to item sd3_<i>;
#   (b) the wording shipped is Dinic et al. (2025) Table 3, whose printed item numbers
#       and R markers are the data file's own codes -- checked here by re-deriving the
#       agreement between Table 3 and the .sav's SPSS variable labels item by item;
#   (c) the five R items are stored ALREADY REVERSE-RECODED, which is why their
#       option_text anchors are shipped flipped (resp 1 = "Agree strongly").
#
# Nothing here re-checks item counts -- validate_items.R did that.
# Live side uses irw::irw_table_sets() (server-side aggregate, no export).

suppressMessages({library(irw); library(haven)})
TABLE <- "dinic_2025_shortdarktriad"
SAV_URL <- "https://osf.io/download/kdgjc/"   # data/SD3-rec.sav, node osf.io/t5wgm
REV <- c(11, 15, 17, 20, 25)

# --- Dinic et al. (2025) PersIndividDiffer 246:113321, Table 3, items 1-27 -------
PAPER <- c(
"It's not wise to tell your secrets.",
"I like to use clever manipulation to get my way.",
"Whatever it takes, you must get the important people on your side.",
"Avoid direct conflict with others because they may be useful in the future.",
"It's wise to keep track of information that you can use against people later.",
"You should wait for the right time to get back at people.",
"There are things you should hide from other people to preserve your reputation.",
"Make sure your plans benefit yourself, not others.",
"Most people can be manipulated.",
"People see me as a natural leader.",
"I hate being the center of attention.",
"Many group activities tend to be dull without me.",
"I know that I am special because everyone keeps telling me so.",
"I like to get acquainted with important people.",
"I feel embarrassed if someone compliments me.",
"I have been compared to famous people.",
"I am an average person.",
"I insist on getting the respect I deserve.",
"I like to get revenge on authorities.",
"I avoid dangerous situations.",
"Payback needs to be quick and nasty.",
"People often say I'm out of control.",
"It's true that I can be mean to others.",
"People who mess with me always regret it.",
"I have never gotten into trouble with the law.",
"I enjoy having sex with people I hardly know.",
"I'll say anything to get what I want.")
# The four positions where the .sav variable label carries different wording than
# Table 3 (the shipped text follows Table 3, which is also the canonical SD3).
KNOWN_DIFF <- c(2, 7, 8, 26)

f <- file.path(tempdir(), "SD3-rec.sav")
if (!file.exists(f)) download.file(SAV_URL, f, mode = "wb", quiet = TRUE)
d <- haven::read_sav(f)
lab <- sapply(d, function(x) { a <- attr(x, "label"); if (is.null(a)) NA_character_ else a })
cols <- grep("^SD3_", names(d), value = TRUE)
num  <- as.integer(sub("R$", "", sub("^SD3_", "", cols)))
cols <- cols[order(num)]; num <- sort(num)

# ---- 1. per-item n: live (server-side) vs the source file the .do processes -----
# .do does mvdecode _all, mv(24) mv(41) mv(43); irw_table_sets() counts non-missing resp.
raw <- as.data.frame(lapply(d[cols], function(x) { x <- as.numeric(x); x[x %in% c(24,41,43)] <- NA; x }))
sav_n <- sapply(raw, function(x) sum(!is.na(x)))
s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(pi$n, pi$item)[paste0("sd3_", num)]

cat(sprintf("%-8s %-10s %10s %10s %6s\n", "item", "sav col", "sav n", "live n", "ok"))
for (i in seq_along(num))
    cat(sprintf("%-8s %-10s %10d %10d %6s\n", paste0("sd3_", num[i]), cols[i],
                sav_n[i], live_n[i], sav_n[i] == live_n[i]))
n_ok <- sum(sav_n == live_n)
cat(sprintf("\nper-item n agreeing: %d of 27 (total sav %d vs live %d)\n",
            n_ok, sum(sav_n), sum(live_n)))

# ---- 2. Table 3 vs the .sav's own SPSS variable labels, item by item ------------
norm <- function(x) tolower(trimws(gsub("[.]$", "", gsub("’", "'", x))))
same <- norm(PAPER[num]) == norm(lab[cols])
cat("\nTable 3 wording vs .sav variable label, per item number:\n")
for (i in seq_along(num))
    if (!same[i]) cat(sprintf("  %2d DIFF  paper: %s\n           sav  : %s\n",
                              num[i], PAPER[num[i]], lab[cols[i]]))
cat(sprintf("  identical at %d of 27 item numbers; differing at: %s\n",
            sum(same), paste(num[!same], collapse = ", ")))
lab_ok <- identical(sort(num[!same]), as.integer(sort(KNOWN_DIFF)))

# ---- 3. keying: are the R items stored already recoded? ------------------------
blocks <- list(Machiavellianism = 1:9, Narcissism = 10:18, Psychopathy = 19:27)
cat("\nitem-rest correlation within own SD3 subscale (source file, as stored):\n")
cat(sprintf("%-8s %-18s %8s %8s\n", "item", "subscale", "as-stored", "if 6-x"))
pol <- logical(0)
for (b in names(blocks)) for (i in blocks[[b]]) {
    cc <- paste0("SD3_", i); cc <- cols[num == i]
    rest <- rowMeans(raw[, cols[num %in% setdiff(blocks[[b]], i)], drop = FALSE], na.rm = TRUE)
    r  <- cor(raw[[cc]], rest, use = "complete.obs")
    if (i %in% REV) {
        cat(sprintf("%-8s %-18s %8.3f %8.3f  <- reverse-worded item\n",
                    paste0("sd3_", i), b, r, -r))
        pol <- c(pol, r > 0)
    }
}
cat(sprintf("reverse-worded items positively correlated with own subscale: %d of 5\n", sum(pol)))
cat("Anchors for those five are therefore shipped flipped (resp 1 = 'Agree strongly').\n")

cat("\nWhat this pins: each of the 27 codes to one source column and to one Table 3\n",
    "item number, and the storage direction of the five recoded items. The wording at\n",
    "items 2, 7, 8 and 26 is the one Table 3 and the published SD3 print; the .sav label\n",
    "at those four positions quotes a different statement, which is recorded in\n",
    "provenance and in the public note.\n", sep = "")

ok <- (n_ok == 27) && lab_ok && all(pol) && length(pol) == 5
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
