# verify_gcb5_2025.R -- Step 5b re-runnable check (batch_406)
#
# CLAIM. gcb_xxx_01_x..05_x carry the five GCB-5 statements in the order shipped
# (01 "permits or perpetrates acts of terrorism", 02 "Evidence of alien contact",
# 03 "New and advanced technology", 04 "Certain significant events", 05 "Experiments
# involving new drugs"), and resp is the RAW deposit value, -3 = Strongly disagree ...
# 3 = Strongly agree.
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("gcb_xxx_")) + pivot_longer; t2_ prefix stripped for wave 2).
# The script's final mutate(resp = resp + 4) is NOT reflected in the live table: the live
# resp set is -3..3 and the deposit's raw columns reproduce it unshifted (checked in (0)).
# So the only link to establish is column -> wording, and the study's own Qualtrics
# printouts (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k and '(Time 2).pdf' q9m27)
# print each statement immediately followed by its export tag.
#
# ROUTE. Explicit code labels in the study's own survey (label match, both waves), with
# (0) tying the deposit CSV to the live table by per-wave per-item n/mean/floor/ceiling so
# the deposit's column names are shown to BE the live codes. Uses the deposit, not
# irw_fetch(), to stay off the Redivis export cap; live numbers hard-coded from
# item_stats.R run 2026-09-24.

V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- sprintf("gcb_xxx_%02d_x", 1:5)

# (0) deposit reproduces the live table (resp = raw, no shift)
LIVE <- list(`1` = list(n = rep(492, 5), m = c(-0.54, -0.25, -0.07, -0.48, -0.57),
                        fl = c(24.8, 20.7, 11.2, 25.4, 23.2), ce = c(8.7, 9.6, 6.7, 6.1, 6.3)),
             `2` = list(n = rep(389, 5), m = c(-0.69, -0.19, 0.09, -0.55, -0.67),
                        fl = c(27.0, 19.3, 9.3, 25.4, 23.4), ce = c(7.2, 11.3, 8.7, 6.7, 5.9)))
for (w in c("1", "2")) {
  cols <- if (w == "1") codes else paste0("t2_", codes)
  cat(sprintf("(0) wave %s: deposit (raw) vs live\n", w))
  for (k in 1:5) {
    x <- d[[cols[k]]]; x <- x[!is.na(x)]
    n <- length(x); m <- mean(x); fl <- 100 * mean(x == -3); ce <- 100 * mean(x == 3)
    L <- LIVE[[w]]
    cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f\n",
                codes[k], n, L$n[k], m, L$m[k], fl, L$fl[k], ce, L$ce[k]))
    if (n != L$n[k] || abs(m - L$m[k]) > 0.006 || abs(fl - L$fl[k]) > 0.06 || abs(ce - L$ce[k]) > 0.06) ok <- FALSE
  }
}

# (1) survey printouts: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(gcb_xxx_01_x = "The government permits or perpetrates acts of terrorism on its own soil, disguising its involvement.",
           gcb_xxx_02_x = "Evidence of alien contact is being concealed from the public.",
           gcb_xxx_03_x = "New and advanced technology which would harm current industry is being suppressed.",
           gcb_xxx_04_x = "Certain significant events have been the result of the activity of a small group who secretly manipulate world events.",
           gcb_xxx_05_x = "Experiments involving new drugs or technologies are routinely carried out on the public without their knowledge or consent.")
# If run from itemtext/, also confirm the shipped CSV carries exactly this claim.
csvp <- "itemtables/batch_406/gcb5_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- all(sh$item_text == CLAIM[sh$item]) && nrow(sh) == 5
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 5 items: %s\n", same)); if (!same) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  for (sv in list(c("au83k", "t1.pdf", ""), c("q9m27", "t2.pdf", "t2_"))) {
    txt <- trimws(system2("pdftotext", c("-raw", dl(sv[1], paste0("kay_", sv[2])), "-"), stdout = TRUE))
    tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)   # every export tag line
    bubl <- grep("^o( o)+$", txt)                               # radio-button rows
    stem <- grep("^Please indicate your level of agreement", txt) # block stem (first item in a block)
    cat(sprintf("(1) %s: statement printed immediately before each tag\n", sv[2]))
    for (k in 1:5) {
      pat <- sprintf("^\\(%sgcb_xxx_%02d_x\\)$", sv[3], k)
      hit <- grep(pat, txt); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); ok <- FALSE; next }
      prev <- max(c(tagi[tagi < hit], bubl[bubl < hit], stem[stem < hit]))
      stmt <- norm(paste(txt[(prev + 1):(hit - 1)], collapse = " "))
      stmt <- sub("^.*?\\(3\\) ", "", stmt)   # strip anchor header on a block's first item
      match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
      cat(sprintf("  %-18s -> %s\n", txt[hit], if (length(match)) names(CLAIM)[match] else paste("NO MATCH:", stmt)))
      if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
    }
  }
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: survey prints Strongly disagree (-3) ... Strongly agree (3); deposit gcb
# columns span -3..3, none is an _r column, and the live table stores them unshifted.
rng <- range(unlist(d[, c(codes, paste0("t2_", codes))]), na.rm = TRUE)
cat(sprintf("(2) deposit raw range %d..%d == live resp set -3..3 (printed anchor values)\n", rng[1], rng[2]))
if (!all(rng == c(-3, 3))) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own tag, distinguishing all 5;\n",
    "(0) only shows the deposit IS the live table, it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
