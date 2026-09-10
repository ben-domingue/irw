# verify_morales_2021_erq.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: the canonical Gross & John (2003) ERQ item i is the wording
# behind live item code erq<i>, i = 1..10.
#
# Two links, tested separately:
#
#   (A) deposit column ERQ_i  ->  live item erq<i>
#       data/morales_2021_asmr.py assigns these POSITIONALLY
#       (long.columns = [f"erq{i+1}" ...] over ERQ_COLS = ERQ_1..ERQ_10), so it
#       is checked, not assumed: per-item n and per-item mean from the PeerJ
#       supplement must reproduce the live table's exactly.
#
#   (B) ERQ_i  ->  canonical instrument item i
#       Route 3 (published subscale totals). The paper's Table S.5 publishes
#       ERQ subscale mean/median/SD by ASMR group for the full sample. Under
#       the canonical scoring key (reappraisal = 1,3,5,7,8,10; suppression =
#       2,4,6,9) those 12 published numbers must reproduce from the deposit --
#       and the subset must be the ONLY six-item subset of the ten that does.
#
# WHAT THIS DOES NOT ESTABLISH: order WITHIN a subscale. (B) pins which four
# items carry suppression wording and which six carry reappraisal wording; it
# cannot separate e.g. items 1, 3, 7 and 10 from one another (near-parallel
# "more positive"/"less negative" x "change what I'm thinking about"/"change the
# way I'm thinking about the situation"). Hence the verification row is PARTIAL.

suppressMessages(library(irw))

TABLE  <- "morales_2021_erq"
SUPPL  <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8164417/supplementaryFiles"
MEMBER <- "peerj-09-11474-s002.csv"

REAPPRAISAL <- c(1, 3, 5, 7, 8, 10)
SUPPRESSION <- c(2, 4, 6, 9)

# Morales, Ramirez-Benavides & Villena-Gonzalez (2021) PeerJ 9:e11474,
# Supplemental Information Table S.5 ("ASMR and Non-ASMR scores in the Emotion
# Regulation Questionnaire", full sample, n = 108 ASMR / 68 non-ASMR).
PUB <- data.frame(
    scale = c("Cognitive reappraisal", "Cognitive reappraisal",
              "Expressive suppression", "Expressive suppression"),
    group = c("ASMR", "non-ASMR", "ASMR", "non-ASMR"),
    mean  = c(4.59, 4.19, 3.46, 3.73),
    median= c(4.67, 4.17, 3.75, 3.50),
    sd    = c(1.08, 1.16, 1.34, 1.51),
    n     = c(108, 68, 108, 68)
)

## ---- fetch the deposit ------------------------------------------------------
tmp <- tempfile(fileext = ".zip")
utils::download.file(SUPPL, tmp, quiet = TRUE, mode = "wb")
raw <- read.csv(unz(tmp, MEMBER), check.names = FALSE)
E <- paste0("ERQ_", 1:10)
raw <- raw[stats::complete.cases(raw[, E]), ]

## ---- (A) deposit column -> live item code -----------------------------------
d <- irw::irw_fetch(TABLE)
live_n <- tapply(d$resp, d$item, length)[paste0("erq", 1:10)]
live_m <- tapply(d$resp, d$item, mean)  [paste0("erq", 1:10)]
dep_n  <- sapply(E, function(k) sum(!is.na(raw[[k]])))
dep_m  <- sapply(E, function(k) mean(raw[[k]]))

cat("(A) deposit column ERQ_i vs live item erq_i\n")
cat(sprintf("%-8s %-8s %6s %6s %12s %12s %12s\n",
            "deposit", "live", "n_dep", "n_live", "mean_dep", "mean_live", "diff"))
for (i in 1:10)
    cat(sprintf("%-8s %-8s %6d %6d %12.8f %12.8f %12.2e\n",
                E[i], paste0("erq", i), dep_n[i], live_n[i],
                dep_m[i], live_m[i], live_m[i] - dep_m[i]))
a_maxdiff <- max(abs(live_m - dep_m))
a_nok     <- all(dep_n == live_n)
cat(sprintf("largest per-item mean deviation: %.3e ; per-item n identical: %s\n\n",
            a_maxdiff, a_nok))

## ---- (B) canonical subscale key vs published Table S.5 ----------------------
# The paper excludes "one subject who respond[ed] the same value in both emotion
# regulation subscales" -- the single respondent with no variance across all ten
# items (group = non-ASMR), which reproduces the published 108 / 68 split.
flat <- apply(raw[, E], 1, function(x) length(unique(x)) == 1)
cat(sprintf("(B) flat responders excluded: %d (published n: 108 + 68 = 176; here: %d)\n",
            sum(flat), sum(!flat)))
dd <- raw[!flat, ]
grp <- ifelse(tolower(trimws(dd[[grep("would you define yourself", names(dd))[1]]])) == "yes",
              "ASMR", "non-ASMR")

score <- function(idx, rows) rowMeans(dd[rows, paste0("ERQ_", idx), drop = FALSE])
obs <- data.frame(
    scale = PUB$scale, group = PUB$group,
    mean = NA_real_, median = NA_real_, sd = NA_real_, n = NA_integer_)
for (r in 1:4) {
    idx  <- if (PUB$scale[r] == "Cognitive reappraisal") REAPPRAISAL else SUPPRESSION
    rows <- grp == PUB$group[r]
    v <- score(idx, rows)
    obs[r, c("mean", "median", "sd", "n")] <- c(mean(v), median(v), sd(v), length(v))
}
cat(sprintf("%-23s %-9s %14s %14s %14s %6s\n",
            "scale", "group", "mean pub/obs", "median pub/obs", "sd pub/obs", "n"))
for (r in 1:4)
    cat(sprintf("%-23s %-9s %6.2f /%6.2f %6.2f /%7.2f %6.2f /%6.2f %3d/%3d\n",
                PUB$scale[r], PUB$group[r], PUB$mean[r], obs$mean[r],
                PUB$median[r], obs$median[r], PUB$sd[r], obs$sd[r],
                PUB$n[r], obs$n[r]))
b_maxdiff <- max(abs(round(obs$mean, 2) - PUB$mean),
                 abs(round(obs$median, 2) - PUB$median),
                 abs(round(obs$sd, 2) - PUB$sd))
b_nok <- all(obs$n == PUB$n)
cat(sprintf("largest deviation across the 12 published statistics: %.3f ; group ns match: %s\n\n",
            b_maxdiff, b_nok))

## ---- (B2) is the canonical subset the ONLY one that reproduces it? ----------
combos <- utils::combn(10, 6, simplify = FALSE)
dev <- sapply(combos, function(cm) {
    sp <- setdiff(1:10, cm)
    R <- rowMeans(dd[, paste0("ERQ_", cm), drop = FALSE])
    S <- rowMeans(dd[, paste0("ERQ_", sp), drop = FALSE])
    v <- c(mean(R[grp == "ASMR"]), mean(R[grp == "non-ASMR"]),
           mean(S[grp == "ASMR"]), mean(S[grp == "non-ASMR"]))
    max(abs(round(v, 2) - PUB$mean))
})
o <- order(dev)
cat(sprintf("(B2) all %d six-item subsets, ranked by worst deviation from the four published means:\n",
            length(combos)))
for (k in 1:3)
    cat(sprintf("   #%d  {%s}  worst dev %.3f\n", k,
                paste(combos[[o[k]]], collapse = ","), dev[o[k]]))
n_exact <- sum(dev < 0.005)
cat(sprintf("   subsets reproducing all four means to 2 dp: %d\n", n_exact))
canonical_rank <- which(sapply(combos[o], function(cm) identical(as.integer(cm), as.integer(REAPPRAISAL))))
cat(sprintf("   canonical reappraisal set {1,3,5,7,8,10} ranks: %d of %d\n\n",
            canonical_rank, length(combos)))

cat("Establishes: ERQ_i -> erq<i> item by item (A), and the reappraisal/suppression\n")
cat("partition of the ten items (B, uniquely among 210 candidate partitions).\n")
cat("Does NOT establish: order within either subscale.\n")

ok <- a_nok && a_maxdiff < 1e-9 && b_nok && b_maxdiff < 0.005 &&
      n_exact == 1 && canonical_rank == 1
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
