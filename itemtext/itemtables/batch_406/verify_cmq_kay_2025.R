# verify_cmq_kay_2025.R -- Step 5b re-runnable check (batch_406)
#
# CLAIM. cmq_xxx_01_x..05_x carry the five CMQ statements in the order shipped
# (01 "Many very important things happen...", 02 "Politicians usually do not tell us...",
# 03 "Government agencies closely monitor...", 04 "Events which superficially seem...",
# 05 "There are secret organizations..."), and resp = raw + 4, so
# 1 = Strongly disagree (-3) ... 7 = Strongly agree (3).
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("cmq_xxx_")) + pivot_longer with names_to="item"; t2_ prefix stripped
# for wave 2) and adds 4 to resp. So the only link to establish is column -> wording, and the
# study's own Qualtrics printouts (OSF uzrgk, 'Qualtrics Survey (Time 1).pdf' au83k and
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
codes <- sprintf("cmq_xxx_%02d_x", 1:5)

# (0) deposit reproduces the live table (resp = raw + 4)
LIVE <- list(`1` = list(n = rep(492, 5), m = c(5.02, 5.26, 4.10, 3.18, 4.20),
                        fl = c(5.1, 2.2, 13.2, 25.6, 16.5), ce = c(23.2, 21.3, 11.6, 2.6, 14.4)),
             `2` = list(n = rep(389, 5), m = c(4.87, 5.37, 4.20, 3.31, 4.14),
                        fl = c(5.9, 1.8, 11.6, 22.1, 14.9), ce = c(19.3, 24.2, 11.8, 3.6, 13.1)))
for (w in c("1", "2")) {
  cols <- if (w == "1") codes else paste0("t2_", codes)
  cat(sprintf("(0) wave %s: deposit vs live\n", w))
  for (k in 1:5) {
    x <- d[[cols[k]]] + 4; x <- x[!is.na(x)]
    n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7)
    L <- LIVE[[w]]
    cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f\n",
                codes[k], n, L$n[k], m, L$m[k], fl, L$fl[k], ce, L$ce[k]))
    if (n != L$n[k] || abs(m - L$m[k]) > 0.006 || abs(fl - L$fl[k]) > 0.06 || abs(ce - L$ce[k]) > 0.06) ok <- FALSE
  }
}
cat(sprintf("  min pairwise gap in live wave-1 means: %.2f (03 vs 05; floor%% 13.2 vs 16.5 also separates them)\n",
            min(dist(LIVE$`1`$m))))

# (1) survey printouts: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(cmq_xxx_01_x = "Many very important things happen in the world, which the public is never informed about.",
           cmq_xxx_02_x = "Politicians usually do not tell us the true motives for their decisions.",
           cmq_xxx_03_x = "Government agencies closely monitor all citizens.",
           cmq_xxx_04_x = "Events which superficially seem to lack a connection are often the result of secret activities.",
           cmq_xxx_05_x = "There are secret organizations that greatly influence political decisions.")
csvp <- "itemtables/batch_406/cmq_kay_2025__items.csv"
if (file.exists(csvp)) {
  sh <- unique(read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")[, c("item", "item_text")])
  same <- all(sh$item_text == CLAIM[sh$item]) && nrow(sh) == 5
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 5 items: %s\n", same)); if (!same) ok <- FALSE
}
if (nzchar(Sys.which("pdftotext"))) {
  for (sv in list(c("au83k", "t1.pdf", ""), c("q9m27", "t2.pdf", "t2_"))) {
    txt <- trimws(gsub("\\f", "", system2("pdftotext", c("-raw", dl(sv[1], paste0("kay_", sv[2])), "-"), stdout = TRUE)))
    tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)   # every export tag line
    oln  <- grep("^o( o)+$", txt)                              # radio-button rows
    cat(sprintf("(1) %s: statement printed immediately before each tag\n", sv[2]))
    for (k in 1:5) {
      pat <- sprintf("^\\(%scmq_xxx_%02d_x\\)$", sv[3], k)
      hit <- grep(pat, txt); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); ok <- FALSE; next }
      prev <- max(c(tagi[tagi < hit], oln[oln < hit]))
      seg <- txt[(prev + 1):(hit - 1)]
      seg <- seg[!grepl("^Page [0-9]+ of [0-9]+$", trimws(seg))]      # page-break footer
      seg <- sub("( o){7}$", "", seg)                          # radio row wrapped onto a text line
      stmt <- norm(paste(seg, collapse = " "))
      stmt <- sub("^.*?\\(3\\) ", "", stmt)                    # anchor header on a block's first item
      match <- which(sapply(CLAIM, function(c) norm(c) == stmt))
      cat(sprintf("  %-18s -> %s\n", txt[hit], if (length(match)) names(CLAIM)[match] else paste("NO MATCH:", stmt)))
      if (!identical(unname(names(CLAIM)[match]), codes[k])) ok <- FALSE
    }
  }
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction: 1 = Strongly disagree. Survey prints Strongly disagree (-3) ... Strongly agree (3);
# deposit cmq columns span -3..3, none is an _r column (authors' Rmd reverses only _r$), script adds 4.
rng <- range(unlist(d[, c(codes, paste0("t2_", codes))]), na.rm = TRUE)
cat(sprintf("(2) deposit raw range %d..%d -> live 1..7 after +4\n", rng[1], rng[2]))
if (!all(rng == c(-3, 3))) ok <- FALSE

cat("Scope: (1) ties each code to one statement by the study's own tag, distinguishing all 5;\n",
    "(0) only shows the deposit IS the live table, it does not order items by itself.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
