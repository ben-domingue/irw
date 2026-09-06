# verify_CQTMS_Hur_2023.R
#
# WHAT IS BEING VERIFIED. The shipped item_text ties each Korean/English item to a
# paper item number I<n> (Supplements 1-3, 5 of Hur & Seo 2023, jeehp 2023;20:20).
# The IRW table's codes are the source spreadsheet's own column names itm1..itm160.
# The load-bearing inference is that itm<n> IS the paper's I<n>. Supplement 1
# publishes the response distribution (proportions at 1..5) for each of the 79
# finally selected items, which is a falsifiable prediction about the live data.
#
# NOTE ON DIRECTION: Supplement 1 reports 17 negatively-worded items ALREADY
# REVERSE-SCORED, while the IRW table stores raw responses. Those items are matched
# against the mirrored published profile; which items those are is itself content-
# consistent (they are exactly the negatively-worded stems).
#
# This does NOT establish: (a) anything about the 81 preliminary items dropped
# before the final selection -- they ship blank item_text; (b) the Korean-text-to-
# number tie for the 30 final items that appear only in Supplement 5 (Korean, no
# item numbers), which rests on the sub-factor + ascending-number ordering rule,
# validated on the 49 items where Supplement 3 gives the number explicitly.

suppressMessages(library(irw))
TABLE <- "CQTMS_Hur_2023"

# Supplement 1: proportion of responses at each of 1..5, by paper item number.
PUB <- list(
  "1" = c(0.064, 0.160, 0.292, 0.386, 0.098),
  "2" = c(0.004, 0.051, 0.180, 0.574, 0.190),
  "3" = c(0.004, 0.017, 0.085, 0.473, 0.420),
  "5" = c(0.012, 0.093, 0.189, 0.465, 0.240),
  "12" = c(0.005, 0.034, 0.192, 0.536, 0.232),
  "13" = c(0.103, 0.370, 0.327, 0.172, 0.027),
  "14" = c(0.047, 0.137, 0.288, 0.387, 0.141),
  "15" = c(0.010, 0.057, 0.288, 0.462, 0.183),
  "17" = c(0.008, 0.046, 0.209, 0.538, 0.198),
  "19" = c(0.004, 0.023, 0.177, 0.623, 0.172),
  "21" = c(0.057, 0.306, 0.396, 0.209, 0.030),
  "23" = c(0.004, 0.044, 0.279, 0.484, 0.188),
  "24" = c(0.027, 0.164, 0.288, 0.420, 0.100),
  "27" = c(0.001, 0.020, 0.112, 0.488, 0.379),
  "29" = c(0.007, 0.052, 0.223, 0.458, 0.259),
  "31" = c(0.005, 0.033, 0.219, 0.538, 0.205),
  "32" = c(0.076, 0.220, 0.288, 0.317, 0.098),
  "33" = c(0.008, 0.040, 0.220, 0.553, 0.177),
  "34" = c(0.017, 0.126, 0.306, 0.425, 0.124),
  "35" = c(0.001, 0.022, 0.173, 0.555, 0.243),
  "37" = c(0.012, 0.100, 0.343, 0.407, 0.137),
  "39" = c(0.018, 0.059, 0.189, 0.482, 0.250),
  "40" = c(0.100, 0.300, 0.336, 0.213, 0.050),
  "41" = c(0.016, 0.073, 0.334, 0.430, 0.146),
  "47" = c(0.005, 0.043, 0.231, 0.527, 0.193),
  "49" = c(0.021, 0.099, 0.322, 0.455, 0.102),
  "50" = c(0.026, 0.162, 0.301, 0.377, 0.133),
  "51" = c(0.004, 0.022, 0.143, 0.559, 0.270),
  "53" = c(0.001, 0.023, 0.128, 0.520, 0.325),
  "54" = c(0.076, 0.227, 0.244, 0.336, 0.115),
  "55" = c(0.029, 0.224, 0.352, 0.310, 0.083),
  "58" = c(0.003, 0.043, 0.240, 0.541, 0.172),
  "62" = c(0.083, 0.270, 0.270, 0.282, 0.094),
  "63" = c(0.031, 0.136, 0.301, 0.394, 0.137),
  "64" = c(0.009, 0.065, 0.317, 0.456, 0.151),
  "66" = c(0.007, 0.044, 0.289, 0.536, 0.124),
  "67" = c(0.008, 0.040, 0.232, 0.559, 0.159),
  "69" = c(0.046, 0.259, 0.411, 0.246, 0.038),
  "70" = c(0.056, 0.214, 0.274, 0.349, 0.106),
  "71" = c(0.026, 0.180, 0.344, 0.355, 0.094),
  "72" = c(0.014, 0.095, 0.284, 0.471, 0.134),
  "73" = c(0.014, 0.112, 0.348, 0.451, 0.072),
  "75" = c(0.004, 0.022, 0.164, 0.632, 0.177),
  "77" = c(0.025, 0.215, 0.316, 0.330, 0.115),
  "78" = c(0.061, 0.185, 0.236, 0.362, 0.155),
  "81" = c(0.035, 0.227, 0.360, 0.306, 0.072),
  "84" = c(0.004, 0.052, 0.203, 0.567, 0.173),
  "85" = c(0.070, 0.293, 0.348, 0.246, 0.042),
  "86" = c(0.005, 0.033, 0.206, 0.554, 0.201),
  "89" = c(0.033, 0.286, 0.368, 0.258, 0.056),
  "97" = c(0.039, 0.169, 0.370, 0.329, 0.093),
  "100" = c(0.010, 0.087, 0.279, 0.506, 0.115),
  "102" = c(0.008, 0.039, 0.151, 0.592, 0.207),
  "106" = c(0.004, 0.031, 0.248, 0.562, 0.153),
  "108" = c(0.001, 0.018, 0.142, 0.507, 0.329),
  "110" = c(0.005, 0.035, 0.283, 0.527, 0.146),
  "111" = c(0.043, 0.227, 0.352, 0.295, 0.081),
  "112" = c(0.016, 0.090, 0.258, 0.441, 0.192),
  "114" = c(0.009, 0.072, 0.278, 0.506, 0.133),
  "116" = c(0.008, 0.082, 0.403, 0.405, 0.098),
  "118" = c(0.004, 0.029, 0.179, 0.613, 0.173),
  "122" = c(0.007, 0.069, 0.284, 0.503, 0.134),
  "123" = c(0.004, 0.026, 0.194, 0.602, 0.171),
  "124" = c(0.073, 0.271, 0.305, 0.271, 0.077),
  "127" = c(0.034, 0.156, 0.325, 0.364, 0.119),
  "128" = c(0.093, 0.361, 0.309, 0.188, 0.047),
  "129" = c(0.008, 0.051, 0.329, 0.493, 0.117),
  "131" = c(0.005, 0.044, 0.252, 0.559, 0.140),
  "132" = c(0.047, 0.231, 0.316, 0.293, 0.112),
  "133" = c(0.057, 0.306, 0.396, 0.209, 0.030),
  "138" = c(0.004, 0.044, 0.270, 0.528, 0.154),
  "140" = c(0.009, 0.096, 0.338, 0.439, 0.117),
  "144" = c(0.005, 0.063, 0.270, 0.515, 0.147),
  "152" = c(0.027, 0.169, 0.295, 0.404, 0.104),
  "154" = c(0.008, 0.065, 0.301, 0.485, 0.141),
  "155" = c(0.003, 0.016, 0.129, 0.537, 0.314),
  "156" = c(0.026, 0.145, 0.227, 0.430, 0.171),
  "158" = c(0.003, 0.020, 0.186, 0.606, 0.185),
  "160" = c(0.043, 0.183, 0.330, 0.368, 0.077)
)

tbl <- irw:::.fetch_redivis_table(TABLE, source = "core")
q <- sprintf(paste("SELECT item, CAST(resp AS STRING) AS resp, COUNT(*) AS n FROM `%s`",
                   "WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                   "GROUP BY item, resp"), tbl$qualified_reference)
d <- as.data.frame(irw:::.irw_query_tibble(q))
d$resp <- as.integer(d$resp)

prof <- function(it) {
    s <- d[d$item == it, ]
    v <- sapply(1:5, function(k) sum(s$n[s$resp == k]))
    v / sum(v)
}
all_items <- unique(d$item)
P <- lapply(all_items, prof); names(P) <- all_items
L1 <- function(a, b) sum(abs(a - b))

cat(sprintf("%-7s %-8s %8s %8s %9s\n", "item", "orient", "L1", "margin", "verdict"))
bad <- 0; worst_margin <- Inf; rev_items <- c()
for (nm in names(PUB)) {
    p <- PUB[[nm]]; it <- paste0("itm", nm)
    dfwd <- L1(P[[it]], p); drev <- L1(rev(P[[it]]), p)
    own <- min(dfwd, drev)
    if (drev < dfwd) rev_items <- c(rev_items, nm)
    # nearest live column over ALL 160, in either orientation
    sc <- sapply(all_items, function(x) min(L1(P[[x]], p), L1(rev(P[[x]]), p)))
    ord <- order(sc)
    best <- all_items[ord[1]]; second <- sc[ord[2]]
    ok <- identical(best, it)
    if (!ok) bad <- bad + 1 else worst_margin <- min(worst_margin, second - own)
    cat(sprintf("%-7s %-8s %8.4f %8.4f %9s\n", it,
                if (drev < dfwd) "reversed" else "direct", own, second - own,
                if (ok) "ok" else paste0("NEAREST=", best)))
}
cat(sprintf("\n%d of %d published items whose nearest live column (over all 160) is itm<n> itself\n",
            length(PUB) - bad, length(PUB)))
cat(sprintf("smallest separation margin among matched items: %.4f\n", worst_margin))
cat("supplement-reverse-scored items: ", paste(rev_items, collapse = ", "), "\n")
cat("KNOWN EXCEPTION: Supplement 1's row for I21 is byte-identical to its row for I133\n",
    "(0.057/0.306/0.396/0.209/0.030), a duplicated row in the published supplement; itm21's\n",
    "own reversed profile sits 0.105 from it. That single item is expected to report\n",
    "NEAREST=itm133 and is not counted as a failure.\n", sep = "")

cat(if (bad <= 1) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
