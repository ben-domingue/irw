# verify_gmc_kay_2025.R -- Step 5b re-runnable check (batch_449)
#
# CLAIM. gmc_xxx_01_x..05_x carry the five GMC statements in the order shipped
# (01 "accurately depict real life events", 02 "information ... is generally true",
# 03_r "I feel they are untrue", 04_r "proved to be false", 05 "several ... believe to be
# true"); resp = deposit value + 4, so for 01/02/05 resp 1 = Strongly disagree ... 7 =
# Strongly agree, and for the two _r items resp 1 = Strongly agree ... 7 = Strongly
# disagree, because the deposit's _r columns were already multiplied by -1.
#
# DERIVATION. data/kay_2025.R keeps the deposit's own column names as `item`
# (select(starts_with("gmc_xxx_")) + pivot_longer; t2_ prefix stripped for wave 2) and
# applies resp + 4. So the links to establish are (a) column -> wording, from the study's
# own Qualtrics printouts (OSF uzrgk, au83k T1 / q9m27 T2), which print each statement
# immediately followed by its export tag; (b) deposit == live; (c) the direction of the
# stored _r columns, from the authors' processing Rmd (5a3gc) and the correlation signs.
#
# Uses the deposit, not irw_fetch(), to stay off the Redivis export cap; live numbers are
# hard-coded from item_stats.R run 2026-09-25.

V <- "view_only=aca403a5146240bda740e1e6d640751f"
dl <- function(id, f) { p <- file.path(tempdir(), f)
  if (!file.exists(p)) download.file(sprintf("https://osf.io/download/%s/?%s", id, V), p, quiet = TRUE, mode = "wb"); p }
d  <- read.csv(dl("z28r4", "kay_data.csv"))
ok <- TRUE
codes <- c("gmc_xxx_01_x", "gmc_xxx_02_x", "gmc_xxx_03_r", "gmc_xxx_04_r", "gmc_xxx_05_x")

# (0) deposit + 4 reproduces the live table, per wave per item
LIVE <- list(`1` = list(n = rep(492, 5), m = c(2.97, 3.00, 3.19, 3.05, 3.48),
                        fl = c(26.8, 25.6, 18.5, 19.5, 25.0), ce = c(1.6, 1.8, 3.0, 3.9, 6.7)),
             `2` = list(n = rep(389, 5), m = c(3.11, 3.01, 3.13, 2.93, 3.65),
                        fl = c(22.6, 25.2, 21.1, 21.6, 21.3), ce = c(1.5, 1.0, 1.3, 1.5, 8.5)))
for (w in c("1", "2")) {
  cols <- if (w == "1") codes else paste0("t2_", codes)
  cat(sprintf("(0) wave %s: deposit+4 vs live\n", w))
  for (k in 1:5) {
    x <- d[[cols[k]]]; x <- x[!is.na(x)] + 4
    n <- length(x); m <- mean(x); fl <- 100 * mean(x == 1); ce <- 100 * mean(x == 7)
    L <- LIVE[[w]]
    cat(sprintf("  %-14s n %d/%d  mean %.4f/%.2f  floor%% %.1f/%.1f  ceil%% %.1f/%.1f  levels used %d\n",
                codes[k], n, L$n[k], m, L$m[k], fl, L$fl[k], ce, L$ce[k], length(unique(x))))
    if (n != L$n[k] || abs(m - L$m[k]) > 0.006 || abs(fl - L$fl[k]) > 0.06 || abs(ce - L$ce[k]) > 0.06) ok <- FALSE
  }
}

# (1) survey printouts: text immediately preceding each export tag == shipped item_text
norm <- function(s) gsub("\\s+", " ", trimws(s))
CLAIM <- c(gmc_xxx_01_x = "Conspiracy theories accurately depict real life events.",
           gmc_xxx_02_x = "The information contained within conspiracy theories is generally true.",
           gmc_xxx_03_r = "When I hear conspiracy theories, I feel they are untrue.",
           gmc_xxx_04_r = "Conspiracy theories contain information, which has proved to be false.",
           gmc_xxx_05_x = "I have heard several conspiracy theories, which I believe to be true.")
csvp <- "itemtables/batch_449/gmc_kay_2025__items.csv"
sh <- NULL
if (file.exists(csvp)) {
  sh <- read.csv(csvp, stringsAsFactors = FALSE, encoding = "UTF-8")
  u <- unique(sh[, c("item", "item_text")])
  same <- nrow(u) == 5 && all(u$item_text == CLAIM[u$item])
  cat(sprintf("(1a) shipped CSV item_text == CLAIM for all 5 items: %s\n", same)); if (!same) ok <- FALSE
}
label_match <- function(claim, verbose) {
  good <- TRUE
  for (sv in list(c("au83k", "t1.pdf", ""), c("q9m27", "t2.pdf", "t2_"))) {
    txt <- trimws(system2("pdftotext", c("-raw", dl(sv[1], paste0("kay_", sv[2])), "-"), stdout = TRUE))
    txt <- gsub("\\f", "", txt)
    txt <- txt[!grepl("^Page [0-9]+ of [0-9]+$", trimws(txt))]    # drop page footers
    txt <- sub("( o)+$| ?o( o)+$", "", txt)                       # drop radio rows glued to a line
    tagi <- grep("^\\((t2_)?[a-z0-9]+_[a-z0-9_]+\\)$", txt)
    bubl <- grep("^(o( o)+)?$", txt)
    stem <- grep("^\\(3\\)$", txt)                                 # end of an anchor header
    if (verbose) cat(sprintf("(1) %s: statement printed immediately before each tag\n", sv[2]))
    for (k in 1:5) {
      pat <- sprintf("^\\(%s%s\\)$", sv[3], codes[k])
      hit <- grep(pat, txt); if (length(hit) != 1) { cat("  tag not found once:", pat, "\n"); good <- FALSE; next }
      prev <- max(c(tagi[tagi < hit], bubl[bubl < hit], stem[stem < hit]))
      stmt <- norm(paste(txt[(prev + 1):(hit - 1)], collapse = " "))
      m <- which(sapply(claim, function(c) norm(c) == stmt))
      if (verbose) cat(sprintf("  %-20s -> %s\n", txt[hit], if (length(m)) names(claim)[m] else paste("NO MATCH:", stmt)))
      if (!identical(unname(names(claim)[m]), codes[k])) good <- FALSE
    }
  }
  good
}
if (nzchar(Sys.which("pdftotext"))) {
  if (!label_match(CLAIM, TRUE)) ok <- FALSE
  sw <- CLAIM; sw[c(1, 2)] <- CLAIM[c(2, 1)]; names(sw) <- names(CLAIM)
  ctl <- label_match(sw, FALSE)
  cat(sprintf("  control (01/02 text swapped) passes label route: %s (must be FALSE)\n", ctl)); if (ctl) ok <- FALSE
} else { cat("pdftotext unavailable -- cannot run the label route\n"); ok <- FALSE }

# (2) direction of the _r columns. (a) authors' Rmd multiplies _r$ by -1 BEFORE exporting
# data_deidentified.csv; (b) the stored _r columns correlate POSITIVELY with the three
# forward belief items (raw "they are untrue"/"proved to be false" would be negative).
rmd <- readLines(dl("5a3gc", "kay_analysis.Rmd"), warn = FALSE)
rev_ln <- grep('mutate_at\\(vars\\(matches\\("_r\\$"\\)\\), ~\\.x \\* -1\\)', rmd)
exp_ln <- grep('rio::export\\(data, "data/data_deidentified.csv"\\)', rmd)
cat(sprintf("(2a) Rmd: _r reversal at line %s, deidentified export at line %s\n",
            paste(rev_ln, collapse = ","), paste(exp_ln, collapse = ",")))
if (!(length(rev_ln) == 1 && length(exp_ln) == 1 && rev_ln < exp_ln)) ok <- FALSE
for (p in c("", "t2_")) {
  r <- cor(d[paste0(p, codes)], use = "pairwise")
  rr <- r[paste0(p, codes[3:4]), paste0(p, codes[c(1, 2, 5)])]
  cat(sprintf("(2b) %swave: r(_r items, forward items) %s\n", if (p == "") "T1 " else "T2 ",
              paste(sprintf("%.2f", rr), collapse = " ")))
  if (any(rr <= 0.2)) ok <- FALSE
}
rng <- range(unlist(d[, c(codes, paste0("t2_", codes))]), na.rm = TRUE)
cat(sprintf("(2c) deposit range %d..%d (+4 = live 1..7; printed anchors (-3)..(3))\n", rng[1], rng[2]))
if (!all(rng == c(-3, 3))) ok <- FALSE
if (!is.null(sh)) {
  lab <- function(it, r) sh$option_text[sh$item == it & sh$resp == r]
  dirok <- lab("gmc_xxx_01_x", 1) == "Strongly disagree" && lab("gmc_xxx_01_x", 7) == "Strongly agree" &&
           lab("gmc_xxx_03_r", 1) == "Strongly agree" && lab("gmc_xxx_03_r", 7) == "Strongly disagree" &&
           lab("gmc_xxx_04_r", 1) == "Strongly agree" && lab("gmc_xxx_04_r", 7) == "Strongly disagree"
  cat(sprintf("(2d) shipped option_text runs disagree->agree for forward items, agree->disagree for _r: %s\n", dirok))
  if (!dirok) ok <- FALSE
}

cat("Scope: (1) ties each code to one statement by the study's own tag, distinguishing all 5;\n",
    "(0) only shows the deposit IS the live table; (2) fixes the stored direction of the _r items.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
