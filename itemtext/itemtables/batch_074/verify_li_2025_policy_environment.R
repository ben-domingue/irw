# verify_li_2025_policy_environment.R -- Step 5b, route 1 (per-item standardized
# factor loadings published in the source paper).
#
# CLAIM UNDER TEST: PLOS ONE 10.1371/journal.pone.0326329's measurement table
# (asset id t001; the article body calls it Table 3) prints the five
# "8. Policy Environment (PE)" item sentences with NO item code beside any of
# them. The extraction ties them to the S1 File .sav columns PE1..PE5 by printed
# order -- mapping_basis=paper_order. The processing script
# data/li_2025_marketing_capability.py melts those five columns BY NAME
# (SCALES["li_2025_policy_environment"] = ["PE1".."PE5"], var_name="item"), so
# the .sav column name IS the IRW item code (core-model pattern 1); the only
# inference is which printed sentence belongs to which column.
#
# FALSIFIABLE PREDICTION: the same table prints a standardized factor loading
# (SFL) for every one of the study's 45 items. Re-fitting the paper's own
# eight-factor CFA on the S1 File must reproduce that column, and each PE column
# must land on the loading printed against the sentence shipped for it. Swap any
# two PE sentences and the printed loading no longer sits on that column.
#
# TWO THINGS SPECIFIC TO THIS TABLE, both consequences of the processing
# script's QC filter (see its header note):
#   * PE2..PE5 each carry ~40 non-integer / out-of-range values in the .sav
#     (PE2 x1.05, PE3 x1.071, PE4 x1.01, PE5 x1.0815 applied to a subset of
#     respondents; PE1 is untouched). The script drops them, so the live table
#     has n = 352/312/313/312/312, not 352 each.
#   * The paper's own CFA was clearly fit on the UNFILTERED file: refitting on
#     the raw .sav reproduces the printed PE loadings to <= 0.0004, while
#     refitting on the filtered data misses by up to 0.061. So the loading route
#     is run on the raw .sav, and the link between the .sav and the live table is
#     established separately, by reproducing the filter and comparing item x resp
#     cell counts server-side.
#
# The live link uses a server-side GROUP BY (irw:::.irw_query_tibble), not
# irw_fetch(), because irw_fetch() exports the whole table against the account's
# 200GB/30-day Redivis quota.

suppressMessages({library(irw); library(haven); library(lavaan)})

TABLE <- "li_2025_policy_environment"
ITEMS <- c("PE1","PE2","PE3","PE4","PE5")

# Table t001, block "8. Policy Environment (PE)", in the printed order (= shipped).
PUBLISHED_SFL   <- c(0.814, 0.786, 0.773, 0.726, 0.742)
PUBLISHED_AVE   <- 0.591
PUBLISHED_CR    <- 0.878
PUBLISHED_ALPHA <- 0.879
TOL <- 0.001   # 3-dp rounding of the published column

# The whole 45-item SFL column, in .sav column order, for the noise floor.
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

## ---- 1. tie the .sav columns to the live IRW table (no export) --------------
# Reproduce the processing script's QC filter, then compare item x resp cells.
keep <- function(x) x[!is.na(x) & x == round(x) & x >= 1 & x <= 7]
tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
q <- irw:::.irw_query_tibble(sprintf(
  paste("SELECT CAST(item AS STRING) AS item,",
        "SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp,",
        "COUNT(*) AS n FROM `%s` GROUP BY 1,2 ORDER BY 1,2"),
  tbl$qualified_reference))
q <- as.data.frame(q)
cat("=== live item x resp cell counts vs the QC-filtered .sav ===\n")
cat(sprintf("%-6s %5s %8s %8s\n", "item", "resp", "live", ".sav"))
link_ok <- TRUE
for (it in ITEMS) {
    x <- keep(d[[it]])
    rl <- sort(unique(q$resp[q$item == it]))
    for (r in rl) {
        nlive <- q$n[q$item == it & q$resp == r]
        nsav  <- sum(x == r)
        cat(sprintf("%-6s %5g %8d %8d%s\n", it, r, nlive, nsav,
                    if (nlive == nsav) "" else "   <- MISMATCH"))
        if (nlive != nsav) link_ok <- FALSE
    }
    if (!setequal(rl, sort(unique(x)))) link_ok <- FALSE
    cat(sprintf("%-6s   n live %d   n .sav kept %d (of 352 raw; %d dropped by the QC filter)\n",
                it, sum(q$n[q$item == it]), length(x), 352 - length(x)))
}
cat("link QC-filtered .sav -> live: ",
    if (link_ok) "all cells identical\n" else "MISMATCH\n", sep = "")

## ---- 2. re-fit the paper's eight-factor CFA on the RAW .sav ------------------
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
s   <- lavaan::standardizedSolution(fit); s <- s[s$op == "=~", ]
all_obs <- setNames(s$est.std, s$rhs)
obs <- all_obs[ITEMS]

floor_err <- max(abs(all_obs - PUB45))
cat(sprintf("\nnoise floor: the re-fit reproduces all 45 published loadings to <= %.5f\n",
            floor_err))
cat(sprintf("             (%d of 45 within 0.0005, %d of 45 within 0.001)\n",
            sum(abs(all_obs - PUB45) <= 0.0005), sum(abs(all_obs - PUB45) <= 0.001)))

TXT <- c("The government provides policies and projects conducive to compa...",
         "The government provides the necessary technical information and...",
         "Government provides direct fiscal policies to our company, incl...",
         "The government encourages companies to protect intellectual pro...",
         "The government provides the necessary legal support for compani...")
cat("\n=== published SFL vs re-fitted SFL, under the shipped mapping ===\n")
cat(sprintf("%-6s %10s %10s %9s  %s\n", "item", "published", "observed", "diff",
            "shipped item_text (truncated)"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %10.3f %10.4f %9.4f  %s\n",
                ITEMS[i], PUBLISHED_SFL[i], obs[i], obs[i] - PUBLISHED_SFL[i], TXT[i]))
worst <- max(abs(obs - PUBLISHED_SFL))
cat(sprintf("\nlargest deviation under the shipped mapping: %.4f (tolerance %.3f)\n",
            worst, TOL))

## ---- 3. rival permutations, and a random-permutation null -------------------
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
cat(sprintf("\nshipped ordering %.4f ; best rival ordering %.4f ; ratio %.0fx\n",
            scores[is_id], best_rival, best_rival / max(scores[is_id], 1e-9)))
cat(sprintf("random-permutation null: median max|diff| over the 119 rivals %.4f, min %.4f\n",
            median(scores[!is_id]), best_rival))
gaps <- sort(abs(outer(PUBLISHED_SFL, PUBLISHED_SFL, "-"))[
             lower.tri(matrix(0, 5, 5))])
cat(sprintf("thinnest gap between any two published PE loadings: %.3f (%.0fx the shipped residual)\n",
            gaps[1], gaps[1] / max(worst, 1e-9)))

## ---- 4. construct-level corroboration (raw .sav, as the paper fitted it) -----
w <- d[, ITEMS]; w <- w[complete.cases(w), ]; k <- ncol(w)
alpha <- (k/(k-1)) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
ave <- mean(obs^2)
cr  <- sum(obs)^2 / (sum(obs)^2 + sum(1 - obs^2))
cat(sprintf("\nCronbach alpha  published %.3f   observed %.3f\n", PUBLISHED_ALPHA, alpha))
cat(sprintf("CR              published %.3f   observed %.3f\n", PUBLISHED_CR, cr))
cat(sprintf("AVE             published %.3f   observed %.3f\n", PUBLISHED_AVE, ave))

cat("\nWhat this does NOT establish. (a) Nothing here reads Chinese: the survey was\n",
    "administered in Chinese and the shipped item_text is the authors' English from\n",
    "the article's table, so this pins which COLUMN each printed sentence belongs to,\n",
    "not the wording respondents read. (b) It says nothing about the option_text<->resp\n",
    "axis, which comes from the .sav's own value labels (mapping at the source) and\n",
    "which the article's prose contradicts (1 'strongly disagree' .. 7 'strongly agree'\n",
    "vs the labels' 'Extremely inconsistent' .. 'Completely consistent').\n", sep = "")

pass <- link_ok && worst <= TOL && best_rival > 3 * worst
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
