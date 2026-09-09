# verify_li_2025_marketing_culture.R -- Step 5b, route 1 (per-item standardized
# factor loadings published in the source paper).
#
# CLAIM UNDER TEST: PLOS ONE 10.1371/journal.pone.0326329 Table 3 lists the five
# Marketing Culture (MC) items in an order that corresponds, one for one and in
# order, to the S1 File .sav columns MCultu11..MCultu15 -- which the processing
# script (data/li_2025_marketing_capability.py) melts BY NAME, so the .sav column
# name IS the IRW item code. Table 3 prints no item codes, so the tie is order.
#
# FALSIFIABLE PREDICTION: Table 3 also prints a standardized factor loading (SFL)
# for every item of all eight constructs. Re-fitting the paper's own eight-factor
# CFA on the S1 File reproduces those loadings, and each MC column must land on
# the loading printed against the item whose text we shipped for it. Swap any two
# MC items' text and the printed value no longer sits on that column.
#
# The script also re-links the .sav to the live IRW table (per-item n and mean),
# so the loadings computed from the .sav are demonstrably about the same numbers
# a user fetches from IRW.

suppressMessages({library(irw); library(haven); library(lavaan)})

TABLE <- "li_2025_marketing_culture"
ITEMS <- c("MCultu11","MCultu12","MCultu13","MCultu14","MCultu15")

# PLOS ONE 20(6):e0326329, Table 3, block "3. Marketing Culture (MC)", in the
# order the table prints the items (the order this extraction shipped).
PUBLISHED_SFL <- c(0.851, 0.686, 0.761, 0.756, 0.747)
PUBLISHED_ALPHA <- 0.877
PUBLISHED_AVE   <- 0.581
TOL <- 0.002

cache <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(cache)) cache <- file.path(".cache", TABLE)
if (!dir.exists(cache)) { dir.create(cache, recursive = TRUE) }
sav <- file.path(cache, "s1.sav")
if (!file.exists(sav))
    download.file(paste0("https://journals.plos.org/plosone/article/file?id=",
                         "10.1371/journal.pone.0326329.s001&type=supplementary"),
                  sav, quiet = TRUE, mode = "wb")

d <- read_sav(sav)
d <- as.data.frame(lapply(d, function(x)
        suppressWarnings(as.numeric(as.character(haven::zap_labels(x))))))

## ---- 1. link the .sav columns to the live IRW table -------------------------
live <- irw::irw_fetch(TABLE)
cat("=== .sav column vs live IRW item (n, mean) ===\n")
cat(sprintf("%-10s %8s %8s %10s %10s\n", "item", "n.sav", "n.live", "mean.sav", "mean.live"))
link_ok <- TRUE
for (it in ITEMS) {
    x  <- d[[it]]; x <- x[!is.na(x)]
    lv <- live$resp[live$item == it]
    cat(sprintf("%-10s %8d %8d %10.4f %10.4f\n", it, length(x), length(lv), mean(x), mean(lv)))
    if (length(x) != length(lv) || abs(mean(x) - mean(lv)) > 1e-8) link_ok <- FALSE
}
cat("link .sav -> live: ", if (link_ok) "identical\n" else "MISMATCH\n", sep = "")

## ---- 2. re-fit the paper's eight-factor CFA ---------------------------------
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
s <- lavaan::standardizedSolution(fit)
s <- s[s$op == "=~" & s$lhs == "MC", ]
obs <- setNames(s$est.std, s$rhs)[ITEMS]

cat("\n=== Table 3 SFL vs re-fitted SFL (paper's own 8-factor CFA) ===\n")
cat(sprintf("%-10s %10s %10s %8s  %s\n", "item", "published", "observed", "diff", "shipped item_text (truncated)"))
TXT <- c("The company's competitive advantage is built upon a thorough...",
         "Employees who provide excellent service to customers can rec...",
         "A company can swiftly respond to competitive actions that po...",
         "Each department of the company is capable of providing produ...",
         "During cross-departmental collaborations, departments treat ...")
for (i in seq_along(ITEMS))
    cat(sprintf("%-10s %10.3f %10.3f %8.3f  %s\n",
                ITEMS[i], PUBLISHED_SFL[i], obs[i], obs[i] - PUBLISHED_SFL[i], TXT[i]))
worst <- max(abs(obs - PUBLISHED_SFL))
cat(sprintf("\nlargest deviation under the shipped mapping: %.4f (tolerance %.3f)\n", worst, TOL))

## ---- 3. rival permutations ---------------------------------------------------
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
all_p <- perms(1:5)
scores <- sapply(all_p, function(p) max(abs(obs[p] - PUBLISHED_SFL)))
ord <- order(scores)
cat("\n=== best five of the 120 orderings (max |diff|) ===\n")
for (k in ord[1:5])
    cat(sprintf("  %-22s %.4f%s\n", paste(all_p[[k]], collapse = "-"), scores[k],
                if (identical(all_p[[k]], 1:5)) "   <- shipped (identity)" else ""))
best_rival <- min(scores[sapply(all_p, function(p) !identical(p, 1:5))])
cat(sprintf("\nshipped ordering: %.4f ; best rival ordering: %.4f\n", scores[which(sapply(all_p, function(p) identical(p, 1:5)))], best_rival))

## ---- 4. construct-level corroboration ---------------------------------------
w <- d[, ITEMS]; w <- w[complete.cases(w), ]
k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
ave <- mean(obs^2)
cat(sprintf("\nCronbach alpha  published %.3f   observed %.3f\n", PUBLISHED_ALPHA, alpha))
cat(sprintf("AVE             published %.3f   observed %.3f\n", PUBLISHED_AVE, ave))

cat("\nWhat this does NOT establish: nothing here reads Chinese wording -- the\n",
    "shipped item_text is the paper's English, and the administered Chinese\n",
    "original is not in the deposit. The check pins which COLUMN each printed\n",
    "loading (and therefore each printed sentence) belongs to, not the wording.\n", sep = "")

pass <- link_ok && worst <= TOL && best_rival > worst
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
