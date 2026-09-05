# Step 5b verification for evans_2023_vaccination_norms (mapping_basis=paper_explicit).
#
# CLAIM UNDER TEST: each of the five live item codes (close, family, friends,
# healthc, nigerian) carries the wording the S2 File codebook assigns to the
# same-named source variable, and the 1-5 option labels run in the ascending
# order the paper states.
#
# FALSIFIABLE PREDICTION: S1 File, Supplemental Table 2b prints per-item means
# and SDs for each of the five norms indicators, separately by study arm
# (T = campaign state, C = comparison state) at baseline, first follow-up and
# second follow-up -- 30 mean cells in all. If any two items' texts were
# swapped, their six-cell mean/SD profiles would swap with them.
#
# Live table: item x wave x treat means, computed from irw_fetch (17,744 rows).

suppressMessages(library(irw))

TABLE <- "evans_2023_vaccination_norms"

# S1 File, Supplemental Table 2b. Column header in the paper -> live item code:
#   Friends -> friends, Family -> family, People Close to You -> close,
#   Nigerians -> nigerian, Health Workers -> healthc.
# Rows: wave 1 = Baseline (n=1933), 2 = First Follow-Up (1155), 3 = Second (462).
PUB <- data.frame(
  item = rep(c("friends","family","close","nigerian","healthc"), each = 6),
  wave = rep(rep(1:3, each = 2), 5),
  treat= rep(c(1,0), 15),
  mean = c(3.11,3.00, 3.16,3.19, 3.15,3.22,      # friends
           3.16,3.00, 3.17,3.20, 3.26,3.17,      # family
           2.51,2.20, 2.63,2.43, 2.67,2.62,      # close
           2.76,2.62, 2.80,2.84, 2.86,2.87,      # nigerian
           3.36,3.41, 3.50,3.50, 3.52,3.52),     # healthc
  sd   = c(1.03,1.05, 1.08,1.03, 1.11,1.08,
           1.02,1.00, 1.01,1.05, 1.11,1.09,
           1.24,1.63, 1.25,1.52, 1.30,1.50,
           1.04,1.01, 0.95,0.99, 1.08,0.99,
           1.18,1.17, 1.12,1.11, 1.17,1.08),
  stringsAsFactors = FALSE)

TOL <- 0.02

d <- irw::irw_fetch(TABLE)
d$treat <- as.numeric(d$treat); d$wave <- as.numeric(d$wave)
agg <- aggregate(resp ~ item + wave + treat, data = d,
                 FUN = function(x) c(m = mean(x), s = sd(x), n = length(x)))
obs <- data.frame(agg[, c("item","wave","treat")],
                  obs_mean = agg$resp[, "m"], obs_sd = agg$resp[, "s"],
                  n = agg$resp[, "n"])

m <- merge(PUB, obs, by = c("item","wave","treat"))
m <- m[order(m$item, m$wave, -m$treat), ]
m$dmean <- m$obs_mean - m$mean
m$dsd   <- m$obs_sd - m$sd

cat(sprintf("%-9s %4s %5s %6s %8s %8s %7s %7s %7s\n",
            "item","wave","arm","n","pub_mean","obs_mean","dmean","pub_sd","obs_sd"))
for (i in seq_len(nrow(m)))
  cat(sprintf("%-9s %4d %5s %6d %8.2f %8.2f %7.3f %7.2f %7.2f\n",
              m$item[i], m$wave[i], ifelse(m$treat[i]==1,"T","C"), m$n[i],
              m$mean[i], m$obs_mean[i], m$dmean[i], m$sd[i], m$obs_sd[i]))

worst <- max(abs(m$dmean))
cat(sprintf("\nn cells compared: %d | largest mean deviation: %.3f (tolerance %.2f)\n",
            nrow(m), worst, TOL))

# Rival-assignment check: is the published profile of each item closer to its own
# observed profile than to any other item's? This is what makes the route
# item-distinguishing rather than merely consistent.
items <- unique(PUB$item)
key <- function(df) paste(df$wave, df$treat)
dist <- matrix(NA_real_, length(items), length(items), dimnames = list(items, items))
for (a in items) for (b in items) {
  pa <- PUB[PUB$item == a, ]; ob <- obs[obs$item == b, ]
  ob <- ob[match(key(pa), key(ob)), ]
  dist[a, b] <- mean(abs(pa$mean - ob$obs_mean))
}
cat("\nmean |published(row item) - observed(column item)| over the 6 wave x arm cells:\n")
print(round(dist, 3))
best <- colnames(dist)[apply(dist, 1, which.min)]
cat("\nnearest observed item for each published item:",
    paste(rownames(dist), "->", best, collapse = "; "), "\n")
diag_ok <- all(best == rownames(dist))
margin <- min(apply(dist, 1, function(r) sort(r)[2] - min(r)))
cat(sprintf("all five published profiles match their own code: %s | smallest margin over the runner-up: %.3f\n",
            diag_ok, margin))

# What this does NOT establish: the option_text <-> resp direction. The 1-5
# ascending coding is stated in the paper's Measures section ("we coded these 1
# to 5, respectively") and in the S2 codebook's numbered value labels, not
# recovered from the data; means alone would not detect a reversed scale that
# was also reversed in the published table.
cat("Check 1 alone does not establish the option_text/resp direction, and two of\n",
    "its 30 cells miss (see the note at the end); check 2 below settles both.\n", sep = "")

# ---------------------------------------------------------------------------
# Check 2 (decisive). Cell-for-cell response-frequency match between the source
# spreadsheet's own columns and the live item codes. S1 Dataset (S3 file,
# Sheet1) stores columns <name><wave-1> holding integers 1-5 -- the same
# integers IRW ships -- so the whole mapping claim reduces to "live item
# `close` holds exactly the values of source columns close0/close1/close2".
# Counts below were read off the S1 Dataset directly (pandas, 2026-09-04) and
# are hard-coded so this script needs no network beyond irw_fetch.
# Format: item, wave, counts of resp = 1/2/3/4/5 in the SOURCE file.
SRC <- read.csv(text = "item,wave,c1,c2,c3,c4,c5
close,1,613,493,426,274,125
close,2,313,263,299,187,93
close,3,117,105,105,92,43
family,1,144,395,621,681,92
family,2,77,235,325,436,82
family,3,35,91,115,177,44
friends,1,176,382,602,693,80
friends,2,87,233,303,460,72
friends,3,39,91,117,180,35
healthc,1,131,332,519,567,382
healthc,2,42,185,309,355,264
healthc,3,18,72,107,146,119
nigerian,1,229,621,671,320,90
nigerian,2,99,333,438,249,36
nigerian,3,52,109,172,107,22", stringsAsFactors = FALSE)

live_tab <- table(d$item, d$wave, d$resp)
cat("\nsource-file vs live counts, per item x wave x resp level:\n")
cat(sprintf("%-9s %4s %25s %25s %6s\n", "item", "wave", "source 1/2/3/4/5", "live 1/2/3/4/5", "match"))
n_bad <- 0
for (i in seq_len(nrow(SRC))) {
  it <- SRC$item[i]; w <- as.character(SRC$wave[i])
  src <- as.integer(SRC[i, c("c1","c2","c3","c4","c5")])
  liv <- as.integer(live_tab[it, w, as.character(1:5)])
  ok <- identical(src, liv); if (!ok) n_bad <- n_bad + 1
  cat(sprintf("%-9s %4s %25s %25s %6s\n", it, w,
              paste(src, collapse = "/"), paste(liv, collapse = "/"), ok))
}
cat(sprintf("cells compared: %d (15 item x wave profiles, 75 counts) | mismatching profiles: %d\n",
            nrow(SRC), n_bad))
cat("A swap of any two items' text, or any permutation of the 1-5 option order,\n",
    "changes at least one of these 75 counts, so this check is decisive on both axes.\n", sep = "")

# ---------------------------------------------------------------------------
# Not established / known published-table defects:
#  - Two of the 30 Supplemental Table 2b mean cells disagree with the data, both
#    in the healthc comparison arm (FU1 3.50 published vs 3.58 observed; FU2 3.52
#    vs 3.71). The same table's own "crude difference at first follow-up" row for
#    Health Workers reads -0.08, which equals 3.50 - 3.58 and NOT 3.50 - 3.50 --
#    i.e. the paper's own difference row corroborates the observed value and
#    identifies the printed mean as the typo. The `close` comparison-arm SDs
#    (1.63/1.52/1.50 published vs 1.23/1.28/1.31 observed) are similarly off while
#    every close mean matches to <=0.004. Neither affects the mapping: check 2
#    reproduces all 75 raw counts exactly.
#  - The option_text <-> resp axis carried no inference to verify. The source
#    spreadsheet already stores integers 1-5, the S2 codebook numbers each value
#    label, and the paper states "we coded these 1 to 5, respectively".

verdict_ok <- diag_ok && n_bad == 0 && sum(abs(m$dmean) > TOL) <= 2
cat(if (verdict_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
