# verify_agn_kay_2025.R -- Step 5b re-runnable check (batch_449)
#
# CLAIM. agn_xxx_01_x..08_x carry the eight Agnew anomie statements in the order shipped
# (01 "I don't blame anyone for trying to grab", 02 "It's no use worrying my head about
# public affairs", 03 "Most people make friends because", 04 "more than my fair share of
# worries", 05 "doesn't know who they can trust", 06 "Success is more dependent on luck",
# 07 "little use writing to public officials", 08 "so many ideas about what is right and
# wrong"), and live resp = deposit raw + 4, so 1 = Strongly disagree (-3) ... 7 = Strongly
# agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("agn_xxx_")) + pivot_longer, single administration, no wave) and ends
# with mutate(resp = resp + 4). Unlike sibling gcb5_2025, the live table DOES carry the +4
# (checked in (0)). The only link to establish is column -> wording: the study's own
# Qualtrics Time 1 printout (OSF uzrgk, au83k) prints each statement immediately followed by
# its export tag. AGN is not in the Time 2 survey.
#
# ROUTE. Explicit code labels in the study's own survey (label match), plus (0) tying the
# deposit CSV to the live table by per-item n/mean/floor/ceiling so the deposit's column
# names are shown to BE the live codes. Deposit, not irw_fetch(), to stay off the export
# cap; live numbers hard-coded from item_stats.R run 2026-09-25.

V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- sprintf("agn_xxx_%02d_x", 1:8)

# (0) deposit (raw + 4) reproduces the live table
LIVE <- list(n = rep(492, 8), m = c(3.70, 3.76, 3.52, 5.18, 4.35, 3.49, 4.44, 3.18),
             fl = c(16.1, 13.6, 15.9, 4.5, 9.8, 14.8, 9.3, 27.6),
             ce = c(5.7, 6.1, 4.3, 23.4, 13.0, 4.9, 17.3, 5.3))
cat("(0) deposit (raw+4) vs live\n")
for (k in 1:8) {
  x <- d[[codes[k]]]; x <- x[!is.na(x)] + 4
  n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7)
  cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f  levels used %d\n",
              codes[k], n, LIVE$n[k], m, LIVE$m[k], fl, LIVE$fl[k], ce, LIVE$ce[k], length(unique(x))))
  if (n != LIVE$n[k] || abs(m - LIVE$m[k]) > 0.006 || abs(fl - LIVE$fl[k]) > 0.06 || abs(ce - LIVE$ce[k]) > 0.06) ok <- FALSE
}

# (1) survey printout: text between the previous export tag and each agn tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(agn_xxx_01_x = "I don’t blame anyone for trying to grab all they can get in this world.",
           agn_xxx_02_x = "It’s no use worrying my head about public affairs; I can’t do anything about them anyway.",
           agn_xxx_03_x = "Most people make friends because friends are likely to be useful to them.",
           agn_xxx_04_x = "I have had more than my fair share of worries.",
           agn_xxx_05_x = "These days a person really doesn’t know who they can trust.",
           agn_xxx_06_x = "Success is more dependent on luck than on real ability.",
           agn_xxx_07_x = "There’s little use writing to public officials because they aren’t really interested in the problems of the average person.",
           agn_xxx_08_x = "There are so many ideas about what is right and wrong these days that it is hard to figure out how to live your life.")
csvp <- "itemtables/batch_449/agn_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- nrow(sh) == 8 && all(sh$item_text == CLAIM[sh$item])
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 8 items: %s\n", same)); if (!same) ok <- FALSE
  op <- unique(read.csv(csvp, stringsAsFactors = FALSE)[, c("resp", "option_text")])
  op <- op[order(op$resp), ]
  want <- c("Strongly disagree","Moderately disagree","Slightly disagree","Neither agree nor disagree",
            "Slightly agree","Moderately agree","Strongly agree")
  okop <- nrow(op) == 7 && all(op$resp == 1:7) && all(op$option_text == want)
  cat(sprintf("(2a) shipped option_text: resp 1..7 == printed anchors (-3)..(3) in order: %s\n", okop)); if (!okop) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  txt <- trimws(system2("pdftotext", c("-raw", dl("au83k", "kay_t1.pdf"), "-"), stdout = TRUE))
  tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)
  junk <- grepl("^o( o)+$", txt) | grepl("Page [0-9]+ of [0-9]+$", txt)
  cat("(1) t1.pdf: statement printed between the previous export tag and each agn tag\n")
  for (k in 1:8) {
    hit <- grep(sprintf("^\\(%s\\)$", codes[k]), txt)
    if (length(hit) != 1) { cat("  tag not found once:", codes[k], "\n"); ok <- FALSE; next }
    prev <- max(tagi[tagi < hit]); idx <- (prev + 1):(hit - 1); idx <- idx[!junk[idx]]
    stmt <- norm(paste(txt[idx], collapse = " "))
    match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
    cat(sprintf("  %-16s -> %s\n", txt[hit], if (length(match)) names(CLAIM)[match] else paste("NO MATCH:", stmt)))
    if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
  }
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: survey prints Strongly disagree (-3) ... Strongly agree (3); deposit agn
# columns span -3..3, none is an _r column; live 1..7 = raw + 4.
rng <- range(unlist(d[, codes]), na.rm = TRUE)
nr <- length(grep("^agn_.*_r$", names(d)))
cat(sprintf("(2) deposit raw range %d..%d (+4 -> 1..7 == live resp set); agn _r columns: %d\n", rng[1], rng[2], nr))
if (!all(rng == c(-3, 3)) || nr != 0) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own export tag, distinguishing all 8;\n",
    "(0) only shows the deposit IS the live table (with +4), it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
