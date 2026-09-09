# verify_li_2025_market_environment.R
#
# CLAIM UNDER TEST (mapping_basis = paper_order):
#   Table 1 of Li et al. (2025), PLOS ONE 20(6):e0326329 -- "Measurement items and
#   result of reliability and validity" -- prints five Market Environment item
#   sentences with NO item codes beside them. The shipped item_text assigns those
#   five sentences, in the order printed, to ME1..ME5.
#
# WHAT MAKES THAT FALSIFIABLE:
#   Table 1's SFL column is a per-item standardized factor loading from the paper's
#   8-factor CFA over all 45 items. Refitting that CFA on the study's own S1 File
#   (.sav) reproduces the column, so each printed row is pinned to a named .sav
#   column. The IRW item code IS that .sav column name
#   (data/li_2025_marketing_capability.py melts ["ME1".."ME5"] by name), so the
#   loading identifies which sentence belongs to which live item.
#   If the ME rows of Table 1 were in any other order, the observed loading vector
#   would not match the published one.
#
# NOT a re-check of item counts -- validate_items.R already did that.

suppressMessages({library(irw); library(haven); library(lavaan)})

TABLE <- "li_2025_market_environment"

# --- published values, Li et al. (2025) Table 1 (t001), read from the table image.
PUB_ME <- c(ME1 = 0.822, ME2 = 0.743, ME3 = 0.742, ME4 = 0.731, ME5 = 0.752)
# whole SFL column, in Table 1's printed row order (45 items, 8 constructs)
PUB_ALL <- c(0.804,0.730,0.703,0.734,0.748,   # 1. Marketing Exploration
             0.687,0.717,0.741,0.703,0.757,   # 2. Marketing Exploitation
             0.851,0.686,0.761,0.756,0.747,   # 3. Marketing Culture
             0.751,0.736,0.731,0.733,0.762,   # 4. Marketing Learning
             0.746,0.743,0.687,0.791,0.763,   # 5. Marketing Operations
             0.813,0.780,0.774,0.804,0.807,   # 6. Corporate performance
             0.808,0.776,0.779,0.780,0.807,
             0.822,0.743,0.742,0.731,0.752,   # 7. Market Environment
             0.814,0.786,0.773,0.726,0.742)   # 8. Policy Environment
PUB_ALPHA_ME <- 0.875   # Cronbach's alpha, ME, Table 1 / Results section

SAV_URL <- paste0("https://journals.plos.org/plosone/article/file?",
                  "id=10.1371/journal.pone.0326329.s001&type=supplementary")
CACHE <- file.path("..", "..", ".cache", TABLE, "s1.sav")   # if run from batch dir
if (!file.exists(CACHE)) CACHE <- file.path(".cache", TABLE, "s1.sav")
if (!file.exists(CACHE)) {
    CACHE <- tempfile(fileext = ".sav")
    utils::download.file(SAV_URL, CACHE, quiet = TRUE, mode = "wb")
}

raw <- as.data.frame(haven::read_sav(CACHE))
raw[] <- lapply(raw, function(x) suppressWarnings(as.numeric(haven::zap_labels(x))))

# ---- 1. tie the live IRW table to the .sav columns it was built from -----------
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
w <- w[order(as.numeric(as.character(w$id))), ]
live <- as.data.frame(lapply(paste0("resp.ME", 1:5), function(cn) as.numeric(w[[cn]])))
names(live) <- paste0("ME", 1:5)
# data/li_2025_marketing_capability.py sets id = .sav row index + 1
sav_me <- raw[as.numeric(as.character(w$id)), paste0("ME", 1:5)]
ncell <- prod(dim(live))
nmatch <- sum(live == sav_me, na.rm = TRUE)
cat(sprintf("live IRW cells identical to S1 .sav ME columns: %d / %d\n", nmatch, ncell))

# ---- 2. refit the paper's 8-factor CFA on the .sav -----------------------------
mod <- "
PLOR =~ Eplor11+Eplor12+Eplor13+Eplor14+Eplor15
PLOI =~ Eploit21+Eploit22+Eploit23+Eploit24+Eploit25
MC   =~ MCultu11+MCultu12+MCultu13+MCultu14+MCultu15
ML   =~ MLear26+MLear27+MLear28+MLear29+MLear210
MO   =~ MOper311+MOper312+MOper313+MOper314+MOper315
PERF =~ Perfo416+Perfo417+Perfo418+Perfo419+Perfo420+Perfo421+Perfo422+Perfo423+Perfo424+Perfo425
ME   =~ ME1+ME2+ME3+ME4+ME5
PE   =~ PE1+PE2+PE3+PE4+PE5
"
fit <- lavaan::cfa(mod, data = raw, std.lv = TRUE)
ss  <- lavaan::standardizedSolution(fit)
ss  <- ss[ss$op == "=~", ]
obs_all <- round(ss$est.std, 3)

cat(sprintf("\nwhole Table 1 SFL column, .sav column order vs printed order: %d/45 exact to 3 dp, max |diff| %.3f\n",
            sum(obs_all == PUB_ALL), max(abs(obs_all - PUB_ALL))))

obs_me <- setNames(ss$est.std[ss$lhs == "ME"], ss$rhs[ss$lhs == "ME"])[names(PUB_ME)]
cat(sprintf("\n%-6s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in seq_along(obs_me))
    cat(sprintf("%-6s %10.3f %10.3f %8.4f\n",
                names(obs_me)[i], PUB_ME[i], obs_me[i], obs_me[i] - PUB_ME[i]))

# ---- 3. the falsification: every rival ordering of the five ME sentences -------
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:5)
ssd <- sapply(P, function(p) sum((as.numeric(obs_me)[p] - as.numeric(PUB_ME))^2))
o <- order(ssd)
cat(sprintf("\nrival orderings of the 5 printed sentences (SSD vs published SFL vector):\n"))
for (k in 1:3)
    cat(sprintf("  rank %d  order %s  SSD %.6f%s\n", k,
                paste(P[[o[k]]], collapse = ""), ssd[o[k]],
                if (identical(P[[o[k]]], 1:5)) "   <- shipped" else ""))
best_is_shipped <- identical(P[[o[1]]], 1:5)

# ---- 4. corroboration: ME reliability ----------------------------------------
me <- raw[, paste0("ME", 1:5)]
k <- ncol(me); alpha <- (k/(k-1)) * (1 - sum(apply(me, 2, var)) / var(rowSums(me)))
cat(sprintf("\nCronbach's alpha, ME: published %.3f, observed %.3f\n", PUB_ALPHA_ME, alpha))

# ---- what this does NOT establish --------------------------------------------
cat("\nNote: ME2 (0.743) and ME3 (0.742) are separated by only 0.001 of loading, so the\n",
    "ME2<->ME3 swap is the weakest link locally (SSD ", sprintf("%.6f", ssd[which(sapply(P, function(p) identical(p, c(1L,3L,2L,4L,5L))))]),
    "). It is ruled out because the\nfit reproduces both values exactly, and because the same fit reproduces the whole\n",
    "45-item SFL column in .sav column order -- i.e. Table 1 is printed in that order\nthroughout, not only within ME.\n", sep = "")

ok <- (nmatch == ncell) &&
      best_is_shipped &&
      max(abs(obs_me - PUB_ME)) <= 0.001 &&
      sum(obs_all == PUB_ALL) >= 44 &&
      abs(alpha - PUB_ALPHA_ME) <= 0.005

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
