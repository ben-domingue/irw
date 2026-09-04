# verify_CV_OASIS_ODSIS_PPE_Novak_2020_BFI.R
#
# CLAIM UNDER TEST -----------------------------------------------------------
# The IRW item codes BFI_N_1 .. BFI_N_8 are the source spreadsheet's own column
# names (data/CV_OASIS_ODSIS_PPE_Novak_2020.R melts `starts_with("BFI")` out of
# ex.dataset.csv / pa.dataset.csv with no rename), and those eight columns are
# the BFI-44 Neuroticism items IN CANONICAL ORDER, i.e.
#   BFI_N_1 = BFI item 4  "Is depressed, blue"
#   BFI_N_2 = BFI item 9  "Is relaxed, handles stress well"        (reverse)
#   BFI_N_3 = BFI item 14 "Can be tense"
#   BFI_N_4 = BFI item 19 "Worries a lot"
#   BFI_N_5 = BFI item 24 "Is emotionally stable, not easily upset" (reverse)
#   BFI_N_6 = BFI item 29 "Can be moody"
#   BFI_N_7 = BFI item 34 "Remains calm in tense situations"        (reverse)
#   BFI_N_8 = BFI item 39 "Gets nervous easily"
#
# The falsifiable prediction: BFI-44 Neuroticism is reverse-keyed at canonical
# positions 2, 5 and 7 and nowhere else (C(8,3) = 56 possible triples), and the
# study's own OSF codebook (osf.io/t9fas, "code_book_BFI_N.txt") independently
# names exactly BFI_N_2, BFI_N_5, BFI_N_7 as the reverse-coded items. If the
# live table stores raw (un-rescored) responses -- which it must, since the IRW
# script reads the raw CSVs and the authors' rescoring lives only in their
# analysis .Rmd -- then those three items and only those three must correlate
# NEGATIVELY with the rest.
#
# Second, weaker signal (route 7, marker item): among the five forward-keyed
# items, "Is depressed, blue" is the one that must sit lowest in a general
# community sample. It is predicted to be BFI_N_1.
#
# WHAT THIS DOES NOT ESTABLISH: it pins the reverse-keyed CLASS {2,5,7} and the
# position of BFI_N_1, but it cannot separate BFI_N_3 / BFI_N_4 / BFI_N_6 /
# BFI_N_8 from each other, nor BFI_N_2 / BFI_N_5 / BFI_N_7 from each other.
# Hence PARTIAL, not VERIFIED.
#
# Everything below is a server-side aggregate query (no table export).

suppressMessages(library(redivis))

TBL <- "`datapages.item_response_warehouse:as2e:v47_0.cv_oasis_odsis_ppe_novak_2020_bfi:nwa2`"

REVERSE   <- c(2, 5, 7)   # codebook osf.io/t9fas AND canonical BFI-44 N positions
ITEM_TEXT <- c("Is depressed, blue", "Is relaxed, handles stress well",
               "Can be tense", "Worries a lot",
               "Is emotionally stable, not easily upset", "Can be moody",
               "Remains calm in tense situations", "Gets nervous easily")

piv <- paste0("WITH w AS (SELECT id, ",
              paste(sprintf('MAX(IF(item="BFI_N_%d", resp, NULL)) AS i%d', 1:8, 1:8),
                    collapse = ", "),
              " FROM ", TBL, " GROUP BY id)")
sel <- paste(c(sprintf("CORR(i1,i%d) AS c1_%d", 2:8, 2:8),
               sprintf("AVG(i%d) AS m%d", 1:8, 1:8)), collapse = ", ")

r <- as.data.frame(redivis::query(paste0(piv, " SELECT ", sel, " FROM w"))$to_data_frame())

cor1  <- c(NA, as.numeric(r[1, sprintf("c1_%d", 2:8)]))
means <- as.numeric(r[1, sprintf("m%d", 1:8)])

cat(sprintf("%-8s %-42s %10s %8s %s\n",
            "item", "shipped item_text", "cor w/ i1", "mean", "keyed"))
for (i in 1:8)
    cat(sprintf("%-8s %-42s %10s %8.2f %s\n",
                paste0("BFI_N_", i), ITEM_TEXT[i],
                if (i == 1) "  (self)" else sprintf("%+.3f", cor1[i]),
                means[i], if (i %in% REVERSE) "reverse" else "forward"))

obs_rev <- which(cor1 < 0)
cat(sprintf("\nnegatively correlated with BFI_N_1: {%s}\n",
            paste(obs_rev, collapse = ", ")))
cat(sprintf("codebook + canonical BFI-44 N reverse positions: {%s}\n",
            paste(REVERSE, collapse = ", ")))
ok_polarity <- setequal(obs_rev, REVERSE)
cat(sprintf("polarity classes agree: %s\n", ok_polarity))

fwd <- setdiff(1:8, REVERSE)
cat(sprintf("\nforward-keyed means: %s\n",
            paste(sprintf("BFI_N_%d=%.2f", fwd, means[fwd]), collapse = "  ")))
ok_marker <- which.min(means[fwd]) == 1L && (min(means[fwd[-1]]) - means[1]) > 0.3
cat(sprintf("lowest forward-keyed item is BFI_N_1 ('Is depressed, blue') by >0.3: %s\n",
            ok_marker))

cat("\nDoes NOT establish: order within {3,4,6,8} or within {2,5,7}.\n")
cat(if (ok_polarity && ok_marker) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
