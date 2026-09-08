# verify_li_2025_marketing_exploration.R -- Step 5b, route 1
# (per-item standardized factor loadings published in the source paper).
#
# CLAIM UNDER TEST: PLOS ONE 10.1371/journal.pone.0326329's measurement table
# (rendered image asset .t001; the article body calls it Table 3) prints the five
# "1. Marketing Exploration (PLOR)" item sentences in an order that corresponds,
# one for one and in order, to the S1 File .sav columns Eplor11..Eplor15 -- which
# data/li_2025_marketing_capability.py melts BY NAME, so the .sav column name IS
# the IRW item code. The table prints no item codes beside the sentences, so the
# tie is presentation order (mapping_basis = paper_order).
#
# FALSIFIABLE PREDICTION: that same table prints a standardized factor loading
# (SFL) per item. Re-fitting the paper's own eight-factor CFA on the S1 File must
# put the printed loading on the column whose text we shipped for it, and any of
# the 119 rival orderings of this block must fit measurably worse.
#
# The script first re-links the .sav to the live IRW table cell by cell, so the
# loadings are demonstrably about the numbers a user actually fetches.

suppressMessages({library(irw); library(haven); library(lavaan)})

TABLE <- "li_2025_marketing_exploration"
ITEMS <- c("Eplor11","Eplor12","Eplor13","Eplor14","Eplor15")

# Measurement table, block "1. Marketing Exploration (PLOR)", in printed order
# (= the order this extraction shipped).
PUBLISHED_SFL   <- c(0.804, 0.730, 0.703, 0.734, 0.748)
PUBLISHED_ALPHA <- 0.861
PUBLISHED_AVE   <- 0.554
PUBLISHED_CR    <- 0.861
TOL <- 0.002   # printed to 3 dp, so rounding alone can cost 0.0005

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

## ---- 1. link .sav columns to the live IRW table, cell for cell --------------
live <- irw::irw_fetch(TABLE)
cat("=== .sav column vs live IRW item ===\n")
cat(sprintf("%-10s %6s %6s %11s %11s %10s\n",
            "item","n.sav","n.live","mean.sav","mean.live","cells eq"))
link_ok <- TRUE; eq_tot <- 0; n_tot <- 0
for (it in ITEMS) {
    sub <- live[live$item == it, ]
    sub <- sub[order(as.numeric(sub$id)), ]
    x   <- d[[it]][as.numeric(sub$id)]
    eq  <- sum(x == as.numeric(sub$resp))
    eq_tot <- eq_tot + eq; n_tot <- n_tot + nrow(sub)
    cat(sprintf("%-10s %6d %6d %11.6f %11.6f %6d/%d\n", it,
                sum(!is.na(d[[it]])), nrow(sub),
                mean(d[[it]], na.rm = TRUE), mean(as.numeric(sub$resp)), eq, nrow(sub)))
    if (eq != nrow(sub)) link_ok <- FALSE
}
cat(sprintf("cellwise agreement: %d / %d -- %s\n\n", eq_tot, n_tot,
            if (link_ok) "identical" else "MISMATCH"))

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
s   <- lavaan::standardizedSolution(fit)
s   <- s[s$op == "=~" & s$lhs == "PLOR", ]
obs <- setNames(s$est.std, s$rhs)[ITEMS]

TXT <- c("We introduce bold, adventurous, or avant-garde marketing proc...",
         "We will consistently develop innovative marketing processes t...",
         "We will continuously apply market knowledge to devise entirel...",
         "We employ market knowledge to break traditional patterns and ...",
         "We will continually acquire new marketing knowledge or skills...")
cat("=== published SFL vs re-fitted SFL (paper's own 8-factor CFA) ===\n")
cat(sprintf("%-10s %10s %10s %9s  %s\n","item","published","observed","diff","shipped item_text (truncated)"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-10s %10.3f %10.4f %9.4f  %s\n",
                ITEMS[i], PUBLISHED_SFL[i], obs[i], obs[i]-PUBLISHED_SFL[i], TXT[i]))
worst <- max(abs(obs - PUBLISHED_SFL))
cat(sprintf("\nlargest deviation under the shipped mapping: %.5f (tolerance %.3f)\n", worst, TOL))

## ---- 3. rival orderings ------------------------------------------------------
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
all_p  <- perms(1:5)
scores <- sapply(all_p, function(p) max(abs(obs[p] - PUBLISHED_SFL)))
ord    <- order(scores)
cat("\n=== best six of the 120 orderings (max |diff|) ===\n")
for (k in ord[1:6])
    cat(sprintf("  %-12s %.5f%s\n", paste(all_p[[k]], collapse="-"), scores[k],
                if (identical(all_p[[k]], 1:5)) "   <- shipped (identity)" else ""))
is_id      <- sapply(all_p, function(p) identical(p, 1:5))
best_rival <- min(scores[!is_id])
cat(sprintf("\nshipped ordering %.5f ; best rival %.5f ; ratio %.1fx\n",
            worst, best_rival, best_rival/worst))

## ---- 4. construct-level corroboration ---------------------------------------
w <- d[, ITEMS]; w <- w[complete.cases(w), ]; k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
ave   <- mean(obs^2)
cr    <- sum(obs)^2 / (sum(obs)^2 + sum(1 - obs^2))
cat(sprintf("\nCronbach alpha  published %.3f   observed %.4f\n", PUBLISHED_ALPHA, alpha))
cat(sprintf("AVE             published %.3f   observed %.4f\n", PUBLISHED_AVE, ave))
cat(sprintf("CR              published %.3f   observed %.4f\n", PUBLISHED_CR, cr))

cat("\nWhat this does NOT establish: (a) the Chinese wording respondents read --\n",
    "the shipped item_text is the paper's English and no Chinese exists in the\n",
    "deposit; (b) the option_text/resp axis, which rests on the .sav's own value\n",
    "labels rather than on a count match, and which the paper's prose contradicts.\n",
    "It pins which .sav COLUMN each printed loading, and so each printed sentence,\n",
    "belongs to.\n", sep = "")

pass <- link_ok && worst <= TOL && best_rival > 5 * worst
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
