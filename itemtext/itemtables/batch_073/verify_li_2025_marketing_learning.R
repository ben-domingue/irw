# verify_li_2025_marketing_learning.R -- Step 5b, route 1 (per-item standardized
# factor loadings published in the source paper).
#
# CLAIM UNDER TEST: PLOS ONE 10.1371/journal.pone.0326329's measurement table
# (asset id t001; the article body calls it Table 3) prints the five "4. Marketing
# Learning (ML)" item sentences with NO item code beside them. The extraction ties
# them to the S1 File .sav columns MLear26, MLear27, MLear28, MLear29, MLear210 by
# printed order -- mapping_basis=paper_order. The processing script
# data/li_2025_marketing_capability.py melts those five columns BY NAME, so the
# .sav column name IS the IRW item code (core-model pattern 1); the only inference
# is the order of the five printed sentences.
#
# FALSIFIABLE PREDICTION: the same table prints a standardized factor loading (SFL)
# for every one of the study's 45 items. Re-fitting the paper's own eight-factor CFA
# on the S1 File must reproduce that column, and each ML column must land on the
# loading printed against the sentence shipped for it. Swap any two ML sentences and
# the printed loading no longer sits on that column.
#
# The script first re-links the .sav to the live IRW table cell for cell, so the
# loadings are demonstrably about the numbers a user fetches. That is a full export
# of a 1,760-row table -- deliberate, and negligible against the Redivis quota.

suppressMessages({library(irw); library(haven); library(lavaan)})

TABLE <- "li_2025_marketing_learning"
ITEMS <- c("MLear26","MLear27","MLear28","MLear29","MLear210")

# Table t001, block "4. Marketing Learning (ML)", in the printed order (= shipped).
PUBLISHED_SFL   <- c(0.751, 0.736, 0.731, 0.733, 0.762)
PUBLISHED_ALPHA <- 0.860
PUBLISHED_CR    <- 0.860
PUBLISHED_AVE   <- 0.552
TOL <- 0.001   # 3-dp rounding of the published column

# The whole 45-item SFL column, in .sav column order, for the noise-floor estimate.
PUB45 <- c(0.804,0.730,0.703,0.734,0.748,  0.687,0.717,0.741,0.703,0.757,
           0.851,0.686,0.761,0.756,0.747,  0.751,0.736,0.731,0.733,0.762,
           0.746,0.743,0.687,0.791,0.763,
           0.813,0.780,0.774,0.804,0.807,0.808,0.776,0.779,0.780,0.807,
           0.822,0.743,0.742,0.731,0.752,  0.814,0.786,0.773,0.726,0.742)

cache <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(cache)) cache <- file.path(".cache", TABLE)
if (!dir.exists(cache)) dir.create(cache, recursive = TRUE)
sav <- file.path(cache, "s1.sav")
if (!file.exists(sav))
    download.file(paste0("https://journals.plos.org/plosone/article/file?id=",
                         "10.1371/journal.pone.0326329.s001&type=supplementary"),
                  sav, quiet = TRUE, mode = "wb")

d <- read_sav(sav)
d <- as.data.frame(lapply(d, function(x)
        suppressWarnings(as.numeric(as.character(haven::zap_labels(x))))))

## ---- 1. link the .sav columns to the live IRW table --------------------------
live <- irw::irw_fetch(TABLE)
cat("=== .sav column vs live IRW item (n, mean, exact value match) ===\n")
cat(sprintf("%-10s %7s %7s %10s %10s %10s\n",
            "item", "n.sav", "n.live", "mean.sav", "mean.live", "cells eq"))
link_ok <- TRUE
for (it in ITEMS) {
    x  <- d[[it]]
    lv <- live[live$item == it, ]
    lv <- lv[order(as.numeric(lv$id)), ]
    eq <- if (nrow(lv) == sum(!is.na(x)))
              sum(as.numeric(lv$resp) == x[as.numeric(lv$id)]) else NA
    cat(sprintf("%-10s %7d %7d %10.4f %10.4f %10s\n", it, sum(!is.na(x)), nrow(lv),
                mean(x, na.rm = TRUE), mean(as.numeric(lv$resp)),
                paste0(eq, "/", nrow(lv))))
    if (is.na(eq) || eq != nrow(lv)) link_ok <- FALSE
}
cat("link .sav -> live (id = .sav row index): ",
    if (link_ok) "identical, cell for cell\n" else "MISMATCH\n", sep = "")

## ---- 2. re-fit the paper's eight-factor CFA ----------------------------------
mod <- '
PLOR =~ Eplor11+Eplor12+Eplor13+Eplor14+Eplor15
PLOI =~ Eploit21+Eploit22+Eploit23+Eploit24+Eploit25
MC   =~ MCultu11+MCultu12+MCultu13+MCultu14+MCultu15
ML   =~ MLear26+MLear27+MLear28+MLear29+MLear210
MO   =~ MOper311+MOper312+MOper313+MOper314+MOper315
PERF =~ Perfo416+Perfo417+Perfo418+Perfo419+Perfo420+Perfo421+Perfo422+Perfo423+Perfo424+Perfo425
ME   =~ ME1+ME2+ME3+ME4+ME5
PE   =~ PE1+PE2+PE3+PE4+PE5
'
fit <- lavaan::cfa(mod, data = d, std.lv = TRUE)
s   <- lavaan::standardizedSolution(fit)
s   <- s[s$op == "=~", ]
all_obs <- setNames(s$est.std, s$rhs)
obs <- all_obs[ITEMS]

## noise floor: how well does the method reproduce the WHOLE printed column?
floor_err <- max(abs(all_obs - PUB45))
cat(sprintf("\nnoise floor: re-fit reproduces all 45 published loadings to <= %.5f\n",
            floor_err))
cat(sprintf("             (%d of 45 within 0.0005, %d of 45 within 0.001)\n",
            sum(abs(all_obs - PUB45) <= 0.0005), sum(abs(all_obs - PUB45) <= 0.001)))

TXT <- c("The company can quickly identify changes in customer produ...",
         "The company conducts consumer evaluations of its products ...",
         "When recognizing customer expectations for product or serv...",
         "Supervisors from each department of the company regularly ...",
         "Managers in the company know how to motivate each employee...")
cat("\n=== published SFL vs re-fitted SFL, under the shipped mapping ===\n")
cat(sprintf("%-10s %10s %10s %9s  %s\n", "item", "published", "observed", "diff",
            "shipped item_text (truncated)"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-10s %10.3f %10.4f %9.4f  %s\n",
                ITEMS[i], PUBLISHED_SFL[i], obs[i], obs[i] - PUBLISHED_SFL[i], TXT[i]))
worst <- max(abs(obs - PUBLISHED_SFL))
cat(sprintf("\nlargest deviation under the shipped mapping: %.4f (tolerance %.3f)\n",
            worst, TOL))

## ---- 3. rival permutations ---------------------------------------------------
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
all_p  <- perms(1:5)
scores <- sapply(all_p, function(p) max(abs(obs[p] - PUBLISHED_SFL)))
ord <- order(scores)
cat("\n=== best five of the 120 orderings (max |diff|) ===\n")
for (k in ord[1:5])
    cat(sprintf("  %-10s %.4f%s\n", paste(all_p[[k]], collapse = "-"), scores[k],
                if (identical(all_p[[k]], 1:5)) "   <- shipped (identity)" else ""))
is_id <- sapply(all_p, function(p) identical(p, 1:5))
best_rival <- min(scores[!is_id])
cat(sprintf("\nshipped ordering %.4f ; best rival ordering %.4f ; ratio %.1fx\n",
            scores[is_id], best_rival, best_rival / max(scores[is_id], 1e-9)))
cat(sprintf("thinnest published gap in this block: %.3f (0.731 MLear28 vs 0.733 MLear29),\n",
            0.002))
cat("  which is ", sprintf("%.1fx", 0.002 / floor_err),
    " the reproduction error measured over all 45 items -- so even the closest\n",
    "  swap is excluded, not merely disfavoured.\n", sep = "")

## ---- 4. construct-level corroboration ----------------------------------------
w <- d[, ITEMS]; w <- w[complete.cases(w), ]; k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
ave <- mean(obs^2)
cr  <- sum(obs)^2 / (sum(obs)^2 + sum(1 - obs^2))
cat(sprintf("\nCronbach alpha  published %.3f   observed %.3f\n", PUBLISHED_ALPHA, alpha))
cat(sprintf("CR              published %.3f   observed %.3f\n", PUBLISHED_CR, cr))
cat(sprintf("AVE             published %.3f   observed %.3f\n", PUBLISHED_AVE, ave))

cat("\nWhat this does NOT establish: nothing here reads Chinese. The shipped\n",
    "item_text is the authors' English from the article table; the administered\n",
    "Chinese wording appears nowhere in the article or its S1 File. This check\n",
    "pins which COLUMN each printed loading -- and so each printed sentence --\n",
    "belongs to, not the wording itself. It also says nothing about option_text,\n",
    "which comes from the .sav's own value labels (mapping at the source).\n", sep = "")

pass <- link_ok && worst <= TOL && best_rival > 3 * worst
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
