# verify_act_kay_2025.R -- Step 5b re-runnable check (batch_405)
#
# CLAIM. act_xxx_01_x..04_x carry the four ACTS statements in the order shipped
# (01 "few people will always run things", 02 "people who really run the country",
# 03 "Big events like wars...", 04 "plots hatched in secret places"), and resp = raw + 4,
# so 1 = Strongly disagree (-3) ... 7 = Strongly agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("act_xxx_")) + pivot_longer; t2_ prefix stripped for wave 2) and
# adds 4 to resp. So the only link to establish is column -> wording, and the study's own
# Qualtrics printouts (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k and
# '(Time 2).pdf' q9m27) print each statement immediately followed by its export tag.
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
codes <- sprintf("act_xxx_%02d_x", 1:4)

# (0) deposit reproduces the live table (resp = raw + 4)
LIVE <- list(`1` = list(n = rep(492, 4), m = c(4.93, 3.96, 3.36, 2.88), fl = c(5.3, 17.1, 26.0, 34.3), ce = c(17.7, 10.4, 6.9, 3.5)),
             `2` = list(n = rep(389, 4), m = c(4.59, 3.83, 3.26, 3.03), fl = c(8.2, 18.3, 26.5, 30.3), ce = c(13.6, 11.6, 6.4, 4.9)))
for (w in c("1", "2")) {
  cols <- if (w == "1") codes else paste0("t2_", codes)
  cat(sprintf("(0) wave %s: deposit vs live\n", w))
  for (k in 1:4) {
    x <- d[[cols[k]]] + 4; x <- x[!is.na(x)]
    n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7)
    L <- LIVE[[w]]
    cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f\n",
                codes[k], n, L$n[k], m, L$m[k], fl, L$fl[k], ce, L$ce[k]))
    if (n != L$n[k] || abs(m - L$m[k]) > 0.006 || abs(fl - L$fl[k]) > 0.06 || abs(ce - L$ce[k]) > 0.06) ok <- FALSE
  }
}
# the four live means are well separated (min gap across items within each wave)
cat(sprintf("  min pairwise gap in live wave-1 means: %.2f\n", min(dist(LIVE$`1`$m))))

# (1) survey printouts: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(act_xxx_01_x = "Even though we live in a democracy, a few people will always run things anyway.",
           act_xxx_02_x = "The people who really \u201crun\u201d the country are not known to the voters.",
           act_xxx_03_x = "Big events like wars, the recent recession, and the outcomes of elections are controlled by small groups of people who are working in secret against the rest of us.",
           act_xxx_04_x = "Much of our lives are being controlled by plots hatched in secret places.")
# If run from itemtext/, also confirm the shipped CSV carries exactly this claim.
csvp <- "itemtables/batch_405/act_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- all(sh$item_text == CLAIM[sh$item]) && nrow(sh) == 4
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 4 items: %s\n", same)); if (!same) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  for (sv in list(c("au83k", "t1.pdf", ""), c("q9m27", "t2.pdf", "t2_"))) {
    txt <- system2("pdftotext", c("-raw", dl(sv[1], paste0("kay_", sv[2])), "-"), stdout = TRUE)
    tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", trimws(txt))   # every export tag line
    cat(sprintf("(1) %s: statement printed immediately before each tag\n", sv[2]))
    for (k in 1:4) {
      pat <- sprintf("^\\(%sacts?_xxx_%02d_x\\)$", sv[3], k)   # T1 prints items 3-4 as 'acts_'
      hit <- grep(pat, trimws(txt)); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); ok <- FALSE; next }
      prev <- max(c(tagi[tagi < hit], grep("^o( o)+$", trimws(txt))[grep("^o( o)+$", trimws(txt)) < hit]))
      stmt <- norm(paste(txt[(prev + 1):(hit - 1)], collapse = " "))
      stmt <- sub("^.*?\\(3\\) ", "", stmt)   # strip anchor header on a block's first item
      match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
      cat(sprintf("  %-18s -> %s\n", trimws(txt[hit]), if (length(match)) names(CLAIM)[match] else paste("NO MATCH:", stmt)))
      if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
    }
  }
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: 1 = Strongly disagree. Survey prints Strongly disagree (-3) ... Strongly agree (3);
# deposit act columns span -3..3 and none is an _r column, and the script adds 4.
rng <- range(unlist(d[, c(codes, paste0("t2_", codes))]), na.rm = TRUE)
cat(sprintf("(2) deposit raw range %d..%d -> live 1..7 after +4\n", rng[1], rng[2]))
if (!all(rng == c(-3, 3))) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own tag, distinguishing all 4;\n",
    "(0) only shows the deposit IS the live table, it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
