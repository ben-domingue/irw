# verify_neurodegenerative_huizinga_2019_dass.R
#
# CLAIM UNDER TEST
#   item code DASS.N carries the wording of DASS-21 item N, in the Dutch
#   translation by de Beurs as REVISED in 2010 (the version whose item order is
#   identical to the English DASS-21).
#
# WHY IT NEEDS TESTING
#   The deposit's codebook labels the block only as "Depression Anxiety Stress
#   Scale - 21 (DASS-21)"; no per-item label exists, and the paper does not
#   reproduce the items or name a Dutch translation. Two Dutch DASS-21 forms are
#   distributed from the instrument's own site (www2.psy.unsw.edu.au/dass), and
#   the site states: "Note that the first 3 items of the Dutch DASS21 differ from
#   the English version, although they belong to the same scales." So items 1-3
#   are exactly where a wrong version would put wrong wording, and a subscale
#   check cannot see it.
#
# TWO CHECKS
#   A. Subscale membership. The deposit ships DASS_depr/DASS_anxiety/DASS_stress
#      /DASS_total alongside the item columns. Summing the CANONICAL DASS-21 keys
#      must reproduce them exactly, respondent by respondent. This pins which of
#      the three scales each of the 21 codes belongs to; it says nothing about
#      order within a scale, and nothing about the 2001-vs-2010 question.
#   B. Version discriminant for items 1 and 2, against de Beurs (2001,
#      Gedragstherapie 34:35-53) Table 1 varimax loadings (D/A/S):
#         DASS21 item 1: 2001 form = DASS-42 #29 "moeilijk tot rust te komen
#                        nadat iets me overstuur had gemaakt"  .31/.50/.51
#                        2010 form = "moeilijk mezelf te kalmeren"
#                        (= English item 1, DASS-42 #22)        .28/.29/.40
#            -> 2001 predicts anxiety ~ stress; 2010 predicts stress clearly
#               above anxiety.
#         DASS21 item 2: 2001 form = DASS-42 #19 "transpireerde merkbaar"
#                                                              .26/.57/.11
#                        2010 form = DASS-42 #02 "mond droog aanvoelde"
#                                                              .14/.43/.09
#            -> the sweating item is anxiety-specific (stress near zero); the
#               dry-mouth item is the weakest item in the whole scale.
#      Item 3 differs too ("enig plezier" vs "enig positief gevoel"); both are
#      depression items with near-identical loadings (.71/.33/.29 vs
#      .64/.30/.30) and this script does NOT separate them.
#
# DATA
#   The deposit CSV (dataverse.nl doi:10.34894/CMJXAK), because the subscale
#   totals used in check A exist only there. Its DASS.* column names are copied
#   unchanged into the IRW table by data/neurodegenerative_huizinga_2019.R, and
#   the linkage is confirmed here against irw::irw_table_sets() -- a server-side
#   aggregate, so no table export is spent.

suppressMessages(library(irw))

TABLE <- "neurodegenerative_huizinga_2019_dass"
URL   <- "https://dataverse.nl/api/access/datafile/19456"

f <- file.path(tempdir(), "huizinga_Data_total.csv")
if (!file.exists(f)) download.file(URL, f, quiet = TRUE)
d <- read.csv2(f, fileEncoding = "latin1", check.names = FALSE)

icols <- paste0("DASS.", 1:21)
num <- function(x) suppressWarnings(as.numeric(ifelse(trimws(x) == "#NULL!", NA, x)))
X <- as.data.frame(lapply(d[icols], num))
tot <- as.data.frame(lapply(d[c("DASS_total","DASS_depr","DASS_anxiety","DASS_stress")], num))
ok  <- stats::complete.cases(X, tot)
X <- X[ok, ]; tot <- tot[ok, ]
cat(sprintf("complete DASS records in deposit: %d\n", nrow(X)))

## ---- linkage to the live table (aggregate query, not an export) -------------
live <- try(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE), silent = TRUE)
link_ok <- TRUE
if (inherits(live, "try-error")) {
    cat("live per-item n unavailable (offline?) -- linkage check skipped\n")
} else {
    pi <- as.data.frame(live$per_item)
    ln <- setNames(pi$n, pi$item)[icols]
    cat(sprintf("live per-item n: %s ; deposit complete-case n: %d\n",
                paste(unique(ln), collapse = "/"), nrow(X)))
    link_ok <- all(ln == nrow(X))
}

## ---- CHECK A: canonical subscale keys reproduce the deposit's own totals ----
KEY <- list(depr = c(3,5,10,13,16,17,21),
            anx  = c(2,4,7,9,15,19,20),
            str  = c(1,6,8,11,12,14,18))
colmap <- c(depr = "DASS_depr", anx = "DASS_anxiety", str = "DASS_stress")
A_ok <- TRUE
for (k in names(KEY)) {
    s <- rowSums(X[paste0("DASS.", KEY[[k]])])
    nbad <- sum(abs(s - tot[[colmap[k]]]) > 1e-9)
    cat(sprintf("subscale %-4s items %-22s exact matches %d/%d, mismatches %d\n",
                k, paste(KEY[[k]], collapse = ","), nrow(X) - nbad, nrow(X), nbad))
    A_ok <- A_ok && nbad == 0
}
nbad <- sum(abs(rowSums(X) - tot$DASS_total) > 1e-9)
cat(sprintf("total    all 21 items            exact matches %d/%d, mismatches %d\n",
            nrow(X) - nbad, nrow(X), nbad))
A_ok <- A_ok && nbad == 0

## ---- CHECK B: version discriminant on items 1 and 2 -------------------------
sub_of <- setNames(rep(c("depr","anx","str"), each = 7),
                   paste0("DASS.", c(KEY$depr, KEY$anx, KEY$str)))
rest_r <- function(item) {
    v <- X[[item]]
    sapply(names(KEY), function(k) {
        cols <- setdiff(paste0("DASS.", KEY[[k]]), item)
        stats::cor(v, rowSums(X[cols]))
    })
}
cat("\ncorrected item-scale correlations (item excluded from its own scale):\n")
cat(sprintf("%-9s %-6s %7s %7s %7s %7s\n", "item","scale","D","A","S","mean"))
for (it in icols)
    cat(sprintf("%-9s %-6s %7.3f %7.3f %7.3f %7.3f\n", it, sub_of[it],
                rest_r(it)["depr"], rest_r(it)["anx"], rest_r(it)["str"], mean(X[[it]])))

r1 <- rest_r("DASS.1"); r2 <- rest_r("DASS.2")
anx_items <- paste0("DASS.", KEY$anx)
mean_anx  <- sapply(anx_items, function(i) mean(X[[i]]))
minr      <- min(sapply(icols, function(i) max(rest_r(i))))

cat(sprintf("\nDASS.1  S=%.3f vs A=%.3f  (S-A = %+.3f)\n", r1["str"], r1["anx"], r1["str"] - r1["anx"]))
cat("  2001 form (DASS-42 #29) predicts A ~= S (.50/.51); 2010 form predicts S > A (.29/.40).\n")
B1 <- (r1["str"] - r1["anx"]) > 0.10

cat(sprintf("DASS.2  D=%.3f A=%.3f S=%.3f ; largest item-scale r for this item = %.3f,\n",
            r2["depr"], r2["anx"], r2["str"], max(r2)))
cat(sprintf("  weakest such value across all 21 items = %.3f -> DASS.2 %s the weakest item.\n",
            minr, if (abs(max(r2) - minr) < 1e-9) "IS" else "is NOT"))
cat("  2001 form (sweating, #19) is anxiety-specific: A .57 with S only .11.\n")
cat("  2010 form (dry mouth, #02) is the weakest item in the pool: A .43, S .09.\n")
B2a <- abs(max(r2) - minr) < 1e-9                  # weakest item overall
B2b <- abs(r2["anx"] - r2["str"]) < 0.05           # no anxiety-specific pattern
cat(sprintf("DASS.2 mean %.3f vs other anxiety items %.3f-%.3f -> %s\n",
            mean(X[["DASS.2"]]), min(mean_anx[anx_items != "DASS.2"]),
            max(mean_anx[anx_items != "DASS.2"]),
            if (mean(X[["DASS.2"]]) == max(mean_anx)) "most endorsed anxiety item" else "not the most endorsed"))
cat("  dry mouth is characteristically the most endorsed DASS anxiety item;\n")
cat("  sweating-when-not-hot is not.\n")
B3 <- mean(X[["DASS.2"]]) == max(mean_anx)

cat("\nNOT ESTABLISHED BY THIS SCRIPT: order within a subscale (7! arrangements per\n")
cat("scale survive check A), and item 3, whose two candidate Dutch wordings are both\n")
cat("depression items with near-identical loadings. Status is therefore PARTIAL.\n\n")

pass <- A_ok && link_ok && B1 && B2a && B2b && B3
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
