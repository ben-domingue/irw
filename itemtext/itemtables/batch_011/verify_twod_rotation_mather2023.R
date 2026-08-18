# verify_twod_rotation_mather2023.R
#
# What is being verified
# ----------------------
# This table's items are FIGURE stimuli, not prose, so `item_text` ships blank.
# The per-item claim the extraction makes is the one in the public_note:
# **the stimulus image `R2Dfigures/fig<NNNNN>.png` in the "Item Stimuli" archive on
# the study's OSF page is the stimulus for live item `q_<NNNNN>`** -- plus one
# shared instruction line, transcribed off the images themselves, and the
# Incorrect/Correct scoring labels on resp 0/1.
#
# Two independent routes test that.
#
# ROUTE A (image -> data).  Each stimulus PNG shows a 4x4 reference array on the
# left and a rotated copy of it on the right with one piece missing.  The target's
# rotation (0/90/180/270 deg) is recovered mechanically from the PNG by comparing
# the white (hexomino) pixels of the right panel against the four rotations of the
# left panel.  The study's own analysis code (OSF R2D_Code_May18.Rmd) names 12
# items that "do not appear to require mental rotation" and drops them from the
# unidimensional IRT model.  Those 12 must therefore be 0-degree figures, and
# 0-degree items must be markedly easier than rotated ones.  Both are falsifiable
# predictions about the fig<->item pairing.
#
# ROUTE B (published per-item statistics -> data).  Supplementary Table S7 of the
# paper (J Intell 2023;11(10):191) publishes mean, SD and N for the 58 retained
# items, keyed by the same q_16NNN codes the live table uses.  Matching published
# mean against live proportion of resp==1, and published N against live row count,
# pins those 58 item codes and fixes the option axis (resp==1 = correct).
#
# What this does NOT establish: the images come in identical-panel families -- the
# 304 figures contain only 111 distinct stimulus:target panels, because many items
# reuse a panel and differ only in their answer-option set.  Route A therefore
# cannot separate two items that share a panel, and Route B covers 58 of 304 items.
# The fig<->item pairing rests on the filename convention, corroborated item-wise
# only for q_16104 (the Rmd displays fig16104.png as that item).  Status: PARTIAL.

suppressMessages(library(png))

TABLE <- "twod_rotation_mather2023"

## ---- published values (hard-coded; from the paper, they will not change) ----

# The 12 items the study's own code removes as not requiring mental rotation
# (OSF R2D_Code_May18.Rmd, "Sub-setting the data for unidimensional IRT scoring").
NOROT <- c("q_16009","q_16053","q_16061","q_16065","q_16069","q_16105",
           "q_16125","q_16193","q_16232","q_16265","q_16281","q_16285")

# Supplementary Table S7: item, published mean (proportion correct), published N.
S7 <- read.csv(text = "item,mean,N
q_16104,0.12,23106
q_16204,0.17,22651
q_16202,0.23,22677
q_16112,0.24,23107
q_16253,0.26,23627
q_16004,0.17,23241
q_16021,0.27,23590
q_16211,0.20,22808
q_16001,0.35,22795
q_16230,0.14,23406
q_16099,0.13,22517
q_16101,0.18,23557
q_16102,0.13,23438
q_16138,0.20,22822
q_16147,0.20,22899
q_16269,0.29,22863
q_16109,0.21,23388
q_16057,0.40,23617
q_16247,0.33,22769
q_16035,0.34,22640
q_16249,0.38,22922
q_16146,0.22,22798
q_16047,0.38,22995
q_16283,0.41,22759
q_16023,0.52,23502
q_16225,0.26,23584
q_16287,0.47,22760
q_16294,0.33,23399
q_16086,0.30,23741
q_16016,0.52,23053
q_16063,0.45,23024
q_16235,0.43,23713
q_16056,0.51,23619
q_16050,0.37,23318
q_16118,0.31,22962
q_16292,0.48,23370
q_16082,0.48,23507
q_16240,0.71,22785
q_16195,0.32,23344
q_16279,0.68,23165
q_16048,0.54,23388
q_16085,0.45,22692
q_16026,0.68,23839
q_16223,0.44,22971
q_16258,0.65,23095
q_16150,0.63,23032
q_16144,0.13,23155
q_16055,0.54,23180
q_16008,0.63,22537
q_16203,0.66,22938
q_16087,0.65,22953
q_16221,0.64,23157
q_16298,0.59,23283
q_16220,0.61,22901
q_16171,0.51,23063
q_16042,0.60,23208
q_16140,0.60,23143
q_16272,0.58,23048
", stringsAsFactors = FALSE)

## ---- live data ------------------------------------------------------------
# The table is 1.9M rows.  Pulling it whole through irw::irw_fetch() counts
# against the Redivis 200GB/30-day export cap (which was already exhausted on
# 2026-08-18, giving a misleading "table does not exist in IRW" message), so the
# per-item aggregate is computed server-side and only 304 rows come back.
# irw_fetch is kept as a fallback so the script still works without redivis.

live <- NULL
live <- tryCatch({
  suppressMessages(library(redivis))
  q <- redivis::query(paste(
    "select item, count(*) as n, avg(resp) as pcorr",
    "from `datapages.item_response_warehouse.twod_rotation_mather2023`",
    "group by item order by item"))
  as.data.frame(q$to_data_frame())
}, error = function(e) { message("redivis query failed: ", conditionMessage(e)); NULL })

if (is.null(live)) {
  suppressMessages(library(irw))
  d <- as.data.frame(irw::irw_fetch(TABLE))
  r <- as.numeric(d$resp); it <- as.character(d$item)
  live <- data.frame(item = sort(unique(it)), stringsAsFactors = FALSE)
  live$n     <- as.integer(tapply(r, it, length))[live$item]
  live$pcorr <- as.numeric(tapply(r, it, mean))[live$item]
}
stopifnot(nrow(live) == 304)

## ---- ROUTE A: recover target rotation from the stimulus images -------------

figdir <- NULL
for (p in c(file.path(".cache", TABLE, "stim", "R2Dfigures"),
            file.path("itemtext", ".cache", TABLE, "stim", "R2Dfigures"),
            file.path("..", "..", ".cache", TABLE, "stim", "R2Dfigures")))
  if (dir.exists(p)) { figdir <- p; break }
if (is.null(figdir)) {
  tmp <- tempfile(); dir.create(tmp); z <- file.path(tmp, "stim.zip")
  ok <- tryCatch({
    download.file("https://osf.io/download/65135e5e43df32018ab6268b/",
                  z, quiet = TRUE, mode = "wb")
    unzip(z, exdir = tmp); TRUE }, error = function(e) FALSE)
  if (ok && dir.exists(file.path(tmp, "R2Dfigures"))) figdir <- file.path(tmp, "R2Dfigures")
}

rot90 <- function(M) t(M[nrow(M):1, , drop = FALSE])
runs  <- function(v) { rr <- rle(v); e <- cumsum(rr$lengths); s <- e - rr$lengths + 1
                       data.frame(s = s[rr$values], e = e[rr$values], w = rr$lengths[rr$values]) }
angle_of <- function(path) {
  im <- readPNG(path)
  g  <- if (length(dim(im)) == 3) (im[, , 1] + im[, , 2] + im[, , 3]) / 3 else im
  dark <- g < 0.5
  top  <- dark[1:round(0.55 * nrow(dark)), , drop = FALSE]
  bl <- runs(colSums(top) > 20); bl <- bl[bl$w > 80, ]
  if (nrow(bl) != 2) return(c(NA, NA))
  rl <- runs(rowSums(top[, bl$s[1]:bl$e[1], drop = FALSE]) > 50); rl <- rl[rl$w > 80, ]
  if (nrow(rl) < 1) return(c(NA, NA))
  r0 <- rl$s[1]; n <- rl$e[1] - r0
  L <- dark[r0:(r0 + n), bl$s[1]:(bl$s[1] + n)]
  R <- dark[r0:(r0 + n), bl$s[2]:(bl$s[2] + n)]
  wR <- !R; sc <- numeric(4); A <- L
  for (k in 0:3) { if (k > 0) A <- rot90(A); wA <- !A
                   sc[k + 1] <- sum(wA & wR) / sum(wA | wR) }
  o <- order(sc, decreasing = TRUE)
  c((o[1] - 1) * 90, sc[o[1]] - sc[o[2]])
}

routeA <- NA
if (!is.null(figdir)) {
  cat("=== ROUTE A: target rotation recovered from the 304 stimulus PNGs ===\n")
  ang <- data.frame(item = live$item, angle = NA_real_, margin = NA_real_,
                    stringsAsFactors = FALSE)
  for (i in seq_len(nrow(ang))) {
    f <- file.path(figdir, paste0(sub("^q_", "fig", ang$item[i]), ".png"))
    if (file.exists(f)) { a <- angle_of(f); ang$angle[i] <- a[1]; ang$margin[i] <- a[2] }
  }
  m <- merge(live, ang, by = "item")
  cat("figures found:", sum(!is.na(m$angle)), "of", nrow(m), "\n")
  cat("rotation distribution:\n"); print(table(m$angle, useNA = "ifany"))
  cat("distinct stimulus:target panels (by match margin):",
      length(unique(round(m$margin, 9))), "\n")

  hit <- m$angle[match(NOROT, m$item)]
  cat("\nThe 12 items the study's code drops as 'not requiring mental rotation':\n")
  for (i in seq_along(NOROT))
    cat(sprintf("  %-9s detected rotation %3s deg   p(correct) = %.3f\n",
                NOROT[i], hit[i], m$pcorr[match(NOROT[i], m$item)]))
  n0 <- sum(hit == 0, na.rm = TRUE)
  p0 <- mean(m$angle == 0, na.rm = TRUE)
  cat(sprintf("\n%d of 12 are 0-degree figures; 0-degree figures are %.1f%% of the pool,\n",
              n0, 100 * p0))
  cat(sprintf("  so under a permuted fig<->item pairing this costs p = %.2g\n", p0^12))

  e0 <- mean(m$pcorr[m$angle == 0], na.rm = TRUE)
  e1 <- mean(m$pcorr[m$angle != 0], na.rm = TRUE)
  cat(sprintf("\nmean p(correct): 0-degree items %.3f (n=%d) vs rotated items %.3f (n=%d)\n",
              e0, sum(m$angle == 0, na.rm = TRUE), e1, sum(m$angle != 0, na.rm = TRUE)))
  tt <- suppressWarnings(t.test(m$pcorr[m$angle == 0], m$pcorr[m$angle != 0]))
  cat(sprintf("difference %.3f, Welch t = %.1f, p = %.2g\n",
              e0 - e1, unname(tt$statistic), tt$p.value))
  routeA <- (n0 == 12) && ((e0 - e1) > 0.05)
} else {
  cat("=== ROUTE A: SKIPPED (stimulus archive could not be fetched from OSF) ===\n")
}

## ---- ROUTE B: published Table S7 vs live data ------------------------------

cat("\n=== ROUTE B: paper Supplementary Table S7 vs live data ===\n")
b <- merge(S7, live, by = "item"); b <- b[order(b$mean), ]
cat(sprintf("%-9s %9s %9s %8s %10s %10s\n",
            "item", "S7 mean", "live p", "diff", "S7 N", "live n"))
for (i in seq_len(nrow(b)))
  cat(sprintf("%-9s %9.2f %9.3f %8.3f %10d %10d\n",
              b$item[i], b$mean[i], b$pcorr[i], b$pcorr[i] - b$mean[i],
              b$N[i], b$n[i]))
worst <- max(abs(b$pcorr - b$mean))
nmatch <- sum(b$N == b$n)

# Structural check: the paper administered a 70-item final pool widely and the
# remaining 234 items only in piloting.  The live per-item n splits exactly there,
# and the 70 high-n items are exactly the 58 Table S7 items plus the 12 dropped
# no-rotation items.
hi <- live$item[live$n > 10000]
cat(sprintf("\nitems with n > 10000: %d (paper's final pool is 70)\n", length(hi)))
cat(sprintf("that set == Table S7's 58 items + the 12 no-rotation items: %s\n",
            setequal(hi, union(S7$item, NOROT))))
cat(sprintf("median n over the other %d (pilot-only) items: %d\n",
            sum(live$n <= 10000), as.integer(median(live$n[live$n <= 10000]))))
structural <- length(hi) == 70 && setequal(hi, union(S7$item, NOROT))
cat(sprintf("\n%d of %d items match the published N exactly\n", nmatch, nrow(b)))
cat(sprintf("largest |published - live| proportion correct: %.4f (S7 is rounded to 2dp)\n", worst))
cat(sprintf("correlation of published mean with live p(correct): %.4f\n",
            cor(b$mean, b$pcorr)))
routeB <- (nmatch == nrow(b)) && (worst <= 0.01) &&
          (cor(b$mean, b$pcorr) > 0.99) && isTRUE(structural)

cat("\nLimits: Route A cannot separate items sharing a stimulus:target panel\n",
    "(304 figures, 111 distinct panels); Route B covers 58 of 304 items.\n",
    "Route B also fixes the option axis: resp==1 is the correct response.\n", sep = "")

pass <- isTRUE(routeB) && !identical(routeA, FALSE)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
