# verify_personalitychange_kramer_2025_rses.R
#
# Claim: item codes rs01_01..rs01_10 are the study's own SoSci variable names
# (the processing script melts the .rda columns unchanged), and the study's
# codebook ("Codebook Personality Change Intervention Study.pdf", OSF zevcs,
# p.13) prints RS01_01..RS01_10 against the ten RSES statements in canonical
# Rosenberg order. mapping_basis = paper_explicit.
#
# What this checks, against numbers:
#   (1) the live table IS the deposited rs01_* columns (per-item n and mean of
#       live vs. the three OSF .rda files pooled) -- so the codebook's codes are
#       the live codes;
#   (2) keying polarity: codebook positive items {01,03,04,07,10} vs negative
#       items {02,05,06,08,09} must show the sign pattern of a raw (un-reversed)
#       RSES -- every within-class correlation > 0, every cross-class < 0;
#   (4) the Study 3 published scale M/SD (Supp. Table S11) reproduce only with
#       the NEG class reverse-scored -- pins polarity class and raw storage;
#   (3) response direction: the codebook prints 5 = "strongly disagree" (a
#       typo; 1 is also "Strongly disagree"). In the same respondents, the
#       positive-item mean must correlate POSITIVELY with the SWLS mean
#       (sw06_*, coded 1 = Strongly disagree .. 7 = Strongly agree) and the
#       negative-item mean NEGATIVELY, which is only possible if 5 = agree.
#
# What this does NOT establish: order WITHIN a polarity class. Swapping, say,
# rs01_03 and rs01_07 text would pass. No per-item statistics are published.
# Hence PARTIAL.

suppressMessages({ library(irw) })

TABLE <- "personalitychange_kramer_2025_rses"
POS <- sprintf("rs01_%02d", c(1, 3, 4, 7, 10))
NEG <- sprintf("rs01_%02d", c(2, 5, 6, 8, 9))
ok <- TRUE

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

# ---- (1) live vs source ----
tmp <- tempfile(fileext = ".zip")
download.file("https://osf.io/download/6xv7f/", tmp, quiet = TRUE, mode = "wb")
ex <- tempfile(); dir.create(ex)
unzip(tmp, files = paste0("reproduce/data/", c("df_sbsa.rda", "df_sbsa2.rda", "df_sbsa3.rda")), exdir = ex)
src <- lapply(c("df_sbsa.rda", "df_sbsa2.rda", "df_sbsa3.rda"), function(f) {
  e <- new.env(); load(file.path(ex, "reproduce/data", f), envir = e); get(ls(e)[1], e)
})
items <- sprintf("rs01_%02d", 1:10)
srcvals <- lapply(items, function(v) { x <- unlist(lapply(src, function(s) s[[v]])); x[x == -9] <- NA; x[!is.na(x)] })
names(srcvals) <- items
cat("(1) live vs deposited rs01_* columns\n")
cat(sprintf("%-8s %7s %7s %8s %8s\n", "item", "n_live", "n_src", "m_live", "m_src"))
for (v in items) {
  lv <- d$resp[d$item == v]
  cat(sprintf("%-8s %7d %7d %8.4f %8.4f\n", v, length(lv), length(srcvals[[v]]), mean(lv), mean(srcvals[[v]])))
  if (length(lv) != length(srcvals[[v]]) || abs(mean(lv) - mean(srcvals[[v]])) > 1e-9) ok <- FALSE
}

# ---- (2) polarity sign pattern in live data ----
d$key <- paste(d$id, d$wave)
w <- reshape(d[, c("key", "item", "resp")], idvar = "key", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
R <- cor(w[, items], use = "pairwise.complete.obs")
within <- c(R[POS, POS][upper.tri(R[POS, POS])], R[NEG, NEG][upper.tri(R[NEG, NEG])])
cross <- as.vector(R[POS, NEG])
cat(sprintf("\n(2) within-class r: min %.3f max %.3f (n=%d); cross-class r: min %.3f max %.3f (n=%d)\n",
            min(within), max(within), length(within), min(cross), max(cross), length(cross)))
cat("    per-item mean r with positive class (excluding self):\n")
for (v in items) cat(sprintf("    %-8s %s %+.3f\n", v, ifelse(v %in% POS, "POS", "NEG"), mean(R[v, setdiff(POS, v)])))
if (min(within) <= 0 || max(cross) >= 0) ok <- FALSE

# ---- (3) direction vs SWLS in the same respondents (source data) ----
cat("\n(3) direction: correlation with SWLS mean (sw06_01..05, 1=Strongly disagree..7=Strongly agree)\n")
for (i in seq_along(src)) {
  s <- src[[i]]
  sw <- sapply(sprintf("sw06_%02d", 1:5), function(v) { x <- s[[v]]; x[x == -9] <- NA; x })
  rp <- sapply(POS, function(v) { x <- s[[v]]; x[x == -9] <- NA; x })
  rn <- sapply(NEG, function(v) { x <- s[[v]]; x[x == -9] <- NA; x })
  a <- cor(rowMeans(rp), rowMeans(sw), use = "complete.obs")
  b <- cor(rowMeans(rn), rowMeans(sw), use = "complete.obs")
  cat(sprintf("    study %d: r(pos RSES, SWLS) = %+.3f   r(neg RSES, SWLS) = %+.3f\n", i, a, b))
  if (a <= 0 || b >= 0) ok <- FALSE
}

# ---- (4) published scale means, Study 3 (Supplementary Table S11, OSF xek5z) ----
# Scale = mean of 10 items with NEG reverse-scored (6 - x), per the authors'
# keys_selfes. Study 3's live Ns equal the published Ns, so this is exact.
pub <- data.frame(group = rep(c("Group 1", "Group 2", "Group 3"), each = 2), wave = rep(1:2, 3),
                  N = c(174, 155, 179, 151, 176, 158), M = c(3.33, 3.44, 3.14, 3.33, 3.44, 3.45),
                  SD = c(0.88, 0.85, 0.83, 0.88, 0.93, 0.99))
d$rk <- ifelse(d$item %in% NEG, 6 - d$resp, d$resp)
s3 <- d[d$cov_study == "study3", ]
pm <- aggregate(cbind(rk, resp) ~ id + wave + cov_group, s3, mean)
cat("\n(4) Study 3 self-esteem scale vs Table S11 (keyed = NEG reversed; raw = no reversal)\n")
cat(sprintf("%-8s %4s %5s %5s %6s %6s %6s %6s %7s\n", "group", "wave", "N_pub", "N", "M_pub", "M_key", "SD_pub", "SD_key", "SD_raw"))
for (i in seq_len(nrow(pub))) {
  x <- pm[pm$cov_group == pub$group[i] & pm$wave == pub$wave[i], ]
  cat(sprintf("%-8s %4d %5d %5d %6.2f %6.2f %6.2f %6.2f %7.2f\n", pub$group[i], pub$wave[i], pub$N[i], nrow(x),
              pub$M[i], mean(x$rk), pub$SD[i], sd(x$rk), sd(x$resp)))
  if (abs(mean(x$rk) - pub$M[i]) > 0.006 || abs(sd(x$rk) - pub$SD[i]) > 0.006) ok <- FALSE
}

cat("\nNot established: order within each polarity class (no per-item statistics published).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
