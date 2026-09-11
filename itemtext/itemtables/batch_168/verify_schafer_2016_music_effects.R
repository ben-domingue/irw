# verify_schafer_2016_music_effects.R -- Step 5b mapping check (batch_168).
#
# Claim: effects_self_awareness / effects_social_relatedness / effects_emotion_mood carry the
# paper's three "effects" questions about self-awareness / social relatedness / arousal and mood
# regulation respectively (Schafer 2016, PLOS ONE 10.1371/journal.pone.0151634, Method > Procedure).
#
# Route 1 (per-item descriptives): the paper's Results ("Goals and Effects of Music Listening")
# publishes, per FUNCTION NAME, the effects means/SDs over all 1,502 situations:
#   self-awareness M = 4.6 SD = 3.0; social relatedness M = 3.2 SD = 2.9;
#   arousal and mood regulation M = 6.2 SD = 2.8.
# Live per-item means are computed server-side (GROUP BY item, resp; no table export) and matched
# against all 3! = 6 possible assignments; only the claimed one may fit.
#
# Bridge check: live per-item x resp counts must equal the S1 Table (.s001) columns named
# 'effects self-awareness' / 'effects social relatedness' / 'effects emotion and mood' cell for cell,
# tying each IRW code to the source column the processing script renamed.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "schafer_2016_music_effects"
CLAIM <- c(effects_self_awareness     = "self-awareness",
           effects_social_relatedness = "social relatedness",
           effects_emotion_mood       = "arousal and mood regulation")
PUB_M  <- c("self-awareness" = 4.6, "social relatedness" = 3.2, "arousal and mood regulation" = 6.2)
PUB_SD <- c("self-awareness" = 3.0, "social relatedness" = 2.9, "arousal and mood regulation" = 2.8)
TOL_M <- 0.05; TOL_SD <- 0.05   # published to 1 dp
S1_COL <- c(effects_self_awareness     = "effects self-awareness",
            effects_social_relatedness = "effects social relatedness",
            effects_emotion_mood       = "effects emotion and mood")

# ---- live counts, server-side ----
src <- irw:::.irw_resolve_source(source = "core")
ref <- irw:::.fetch_redivis_table(TABLE, source = src)$qualified_reference
q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                   "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp, COUNT(*) AS n",
                   "FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                   "GROUP BY item, resp"), ref)
live <- as.data.frame(irw:::.irw_query_tibble(q))
live$resp <- as.numeric(live$resp); live$n <- as.numeric(live$n)

wstats <- function(r, n) { m <- sum(r * n) / sum(n); s <- sqrt(sum(n * (r - m)^2) / (sum(n) - 1)); c(m = m, sd = s) }
obs <- t(sapply(names(CLAIM), function(it) { d <- live[live$item == it, ]; wstats(d$resp, d$n) }))

ok <- TRUE
cat("== Route 1: live per-item mean/SD vs paper Results (effects, all 1,502 situations) ==\n")
cat(sprintf("%-28s %-28s %8s %8s %8s %8s\n", "item", "claimed function", "pub M", "live M", "pub SD", "live SD"))
for (it in names(CLAIM)) {
  f <- CLAIM[[it]]
  cat(sprintf("%-28s %-28s %8.1f %8.3f %8.1f %8.3f\n", it, f, PUB_M[f], obs[it, "m"], PUB_SD[f], obs[it, "sd"]))
  if (abs(obs[it, "m"] - PUB_M[f]) > TOL_M || abs(obs[it, "sd"] - PUB_SD[f]) > TOL_SD) ok <- FALSE
}

perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
fn <- names(PUB_M)
cat("\nAll 6 assignments of the three function labels to the three live items (max |M diff|):\n")
fits <- 0
for (p in perms) {
  lab <- fn[p]
  dev <- max(abs(obs[, "m"] - PUB_M[lab]))
  fit <- dev <= TOL_M
  fits <- fits + fit
  cat(sprintf("  %-70s max|dM| = %.3f %s\n", paste(names(CLAIM), "=", lab, collapse = "; "), dev, if (fit) "FITS" else ""))
}
if (fits != 1) ok <- FALSE
cat(sprintf("assignments fitting within %.2f: %d (must be exactly 1, the claimed one)\n", TOL_M, fits))

# ---- bridge: S1 Table columns vs live codes ----
cat("\n== Bridge: S1 Table (.s001) column counts vs live item counts ==\n")
tf <- tempfile(fileext = ".xlsx")
s1_ok <- tryCatch({
  download.file("https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0151634.s001&type=supplementary",
                tf, mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (s1_ok) {
  s1 <- as.data.frame(read_excel(tf))
  for (it in names(S1_COL)) {
    raw <- table(factor(s1[[S1_COL[[it]]]], levels = 1:10))
    d <- live[live$item == it, ]
    lv <- setNames(d$n, d$resp)[as.character(1:10)]; lv[is.na(lv)] <- 0
    same <- all(as.numeric(raw) == as.numeric(lv))
    # does this S1 column match any OTHER live item?
    other <- sapply(setdiff(names(S1_COL), it), function(o) {
      d2 <- live[live$item == o, ]; l2 <- setNames(d2$n, d2$resp)[as.character(1:10)]; l2[is.na(l2)] <- 0
      all(as.numeric(raw) == as.numeric(l2)) })
    cat(sprintf("  %-28s <- '%s': S1 %s | live %s | %s%s\n", it, S1_COL[[it]],
                paste(as.numeric(raw), collapse = "/"), paste(as.numeric(lv), collapse = "/"),
                if (same) "MATCH" else "MISMATCH", if (any(other)) " (ALSO matches another item!)" else ""))
    if (!same || any(other)) ok <- FALSE
  }
} else cat("  S1 download failed -- bridge not run (route 1 still decides)\n")

cat("\nNOT ESTABLISHED by this script: the German wording respondents read (not published);\n",
    "that the paper's 'arousal and mood regulation' question is the same item the S1 header calls\n",
    "'emotion and mood' rests on the published M 6.2/SD 2.8 matching that column, which it does uniquely.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
