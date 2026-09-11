# verify_shi_2025_rrs.R -- Step 5b check for shi_2025_rrs (batch_172).
#
# CLAIM: IRW item codes item1..item22 carry the canonical 22-item Ruminative
# Responses Scale numbering (Nolen-Hoeksema's distribution copy / Treynor,
# Gonzalez & Nolen-Hoeksema 2003), so item_text = canonical RRS item N for itemN.
#
# DERIVATION: data/shi_2025_mindfulness.py is a number-preserving rename
# ({pre,post,third}RRS<N> -> item<N>, wave 0/1/2). The source .sav (PLOS ONE
# 10.1371/journal.pone.0331084.s001) has NO variable labels and NO value labels,
# so the number->wording tie is not stated anywhere in the study's materials.
#
# ROUTE 3 (stored/published subscale totals): the same .sav stores the study's
# OWN RRS subscale scores per wave -- <wave>RRS症状反刍 (symptom rumination),
# 强迫思考 (obsessive thinking = brooding), 反省深思 (reflective pondering). The
# canonical RRS key (Treynor et al. 2003; Han & Yang 2009 use the same 12/5/5
# split) must reproduce them for every person x wave from the LIVE items:
#   Symptom rumination = 1,2,3,4,6,8,9,14,17,18,19,22
#   Brooding           = 5,10,13,15,16
#   Reflection         = 7,11,12,20,21
# Discrimination: all 145 single cross-subscale swaps of the key must FAIL.
# Tie to the paper: Table 3 baseline M +/- SD per arm (MT / PS) must reproduce
# (means within 0.011, SDs within 0.02 -- the PS total SD computes to 10.856
# against a printed 10.87, the only cell off by more than rounding).
#
# DOES NOT ESTABLISH: order of items WITHIN a subscale (e.g. that item1 is
# "how alone you feel" rather than symptom item 2); that rests on the canonical
# numbering carried through the column suffixes -- no per-item statistics are
# published. Nothing about option_text<->resp beyond the paper's endpoint
# statement (1 = almost never, 4 = almost always).

suppressMessages({ library(irw); library(haven) })

TABLE <- "shi_2025_rrs"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0331084.s001"
KEY <- list(SR = c(1, 2, 3, 4, 6, 8, 9, 14, 17, 18, 19, 22), BR = c(5, 10, 13, 15, 16), RE = c(7, 11, 12, 20, 21))
SUBCOL <- c(SR = "症状反刍", BR = "强迫思考", RE = "反省深思")
WAVES <- c("pre", "post", "third")
# Paper Table 3 (baseline), M and SD: MT then PS
PUB <- rbind(
  MT = c(total = 46.02, total_sd = 14.46, SR = 24.02, SR_sd = 8.35, BR = 11.48, BR_sd = 3.73, RE = 10.52, RE_sd = 3.75),
  PS = c(total = 45.33, total_sd = 10.87, SR = 23.33, SR_sd = 6.53, BR = 11.26, BR_sd = 2.90, RE = 10.74, RE_sd = 2.63))

d <- as.data.frame(irw::irw_fetch(TABLE))
tf <- tempfile(fileext = ".sav")
download.file(URL, tf, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "IRW-Finder/1.0 (ben.domingue@gmail.com)"))
src <- as.data.frame(haven::read_sav(tf))
names(src)[names(src) == "编号"] <- "id"
cat(sprintf("live rows %d, live ids %d, source persons %d\n", nrow(d), length(unique(d$id)), nrow(src)))

ok <- TRUE

# (a) live resp == source column, cell for cell
agree <- 0; total <- 0
for (w in 0:2) for (i in 1:22) {
  lv <- d[d$wave == w & d$item == paste0("item", i), c("id", "resp")]
  mm <- merge(lv, src[, c("id", paste0(WAVES[w + 1], "RRS", i))], by = "id")
  total <- total + nrow(mm); agree <- agree + sum(mm$resp == mm[[3]])
}
cat(sprintf("(a) live resp vs source <wave>RRS<N>: %d / %d cells agree (source cells %d; the 2 absent are post RRS9/RRS16 = 5, out of range)\n",
            agree, total, 196 * 3 * 22))
if (agree != total || total != nrow(d)) ok <- FALSE

wide <- function(w) {
  x <- d[d$wave == w, c("id", "item", "resp")]
  r <- reshape(x, idvar = "id", timevar = "item", direction = "wide")
  names(r) <- sub("^resp\\.", "", names(r))
  r <- merge(r, src[, c("id", "组别", paste0(WAVES[w + 1], "RRS", SUBCOL))], by = "id")
  r[complete.cases(r), ]
}
Ws <- lapply(0:2, wide)
score <- function(W, key, w) sapply(names(key), function(k)
  sum(rowSums(W[, paste0("item", key[[k]]), drop = FALSE]) == W[[paste0(WAVES[w + 1], "RRS", SUBCOL[[k]])]]))

cat("\n(b) canonical key vs study's stored subscale scores (exact matches / complete persons)\n")
full <- 0; target <- 0
for (w in 0:2) {
  s <- score(Ws[[w + 1]], KEY, w); n <- nrow(Ws[[w + 1]])
  cat(sprintf("  wave %d (%s): symptom %d/%d  brooding %d/%d  reflection %d/%d\n", w, WAVES[w + 1], s["SR"], n, s["BR"], n, s["RE"], n))
  full <- full + sum(s); target <- target + 3 * n
  if (any(s != n)) ok <- FALSE
}
cat(sprintf("  total %d/%d\n", full, target))
if (target != 3 * (196 + 194 + 196)) ok <- FALSE

n_sw <- 0; n_surv <- 0; best <- 0
for (a in names(KEY)) for (b in names(KEY)) if (a < b) for (p in KEY[[a]]) for (q in KEY[[b]]) {
  k2 <- KEY; k2[[a]][k2[[a]] == p] <- q; k2[[b]][k2[[b]] == q] <- p
  m <- sum(sapply(0:2, function(w) sum(score(Ws[[w + 1]], k2, w))))
  n_sw <- n_sw + 1; best <- max(best, m); if (m == target) n_surv <- n_surv + 1
}
cat(sprintf("\n(c) single cross-subscale swaps: %d tested, %d still reproduce all %d stored scores; best rival %d/%d\n",
            n_sw, n_surv, target, best, target))
if (n_sw != 145 || n_surv != 0) ok <- FALSE

cat("\n(d) paper Table 3 baseline, computed from LIVE wave-0 items under the key (group 1 = MT, 2 = PS)\n")
W0 <- Ws[[1]]
for (g in 1:2) {
  x <- W0[W0[["组别"]] == g, ]
  sc <- cbind(total = rowSums(x[, paste0("item", 1:22)]),
              SR = rowSums(x[, paste0("item", KEY$SR)]), BR = rowSums(x[, paste0("item", KEY$BR)]),
              RE = rowSums(x[, paste0("item", KEY$RE)]))
  obs <- c(colMeans(sc), apply(sc, 2, sd))
  lab <- rownames(PUB)[g]
  for (k in c("total", "SR", "BR", "RE")) {
    cat(sprintf("  %s %-5s published %6.2f (%5.2f)  observed %6.2f (%5.2f)\n", lab, k, PUB[g, k], PUB[g, paste0(k, "_sd")],
                obs[k], obs[length(obs) / 2 + match(k, colnames(sc))]))
    if (abs(obs[k] - PUB[g, k]) > 0.011 ||
        abs(obs[length(obs) / 2 + match(k, colnames(sc))] - PUB[g, paste0(k, "_sd")]) > 0.02) ok <- FALSE
  }
}

cat("\nNOT ESTABLISHED: order of items within each subscale (rests on canonical numbering carried by the",
    "column suffix); (d) pins subscale membership and the published totals, not item positions.\n")
cat("RESP-CODING NOTE (not a mapping check): live resp by wave --\n")
print(table(wave = d$wave, resp = d$resp))

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
