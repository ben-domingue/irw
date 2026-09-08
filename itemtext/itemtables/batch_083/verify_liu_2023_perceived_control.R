# verify_liu_2023_perceived_control.R
#
# mapping_basis = paper_order. The three item codes PBC1-PBC3 ARE the S1 Data
# workbook's own column names (data/liu_2023_brand_trust.py selects them with
# ^PBC\d+$ and melts, so there is no rename and no positional assignment). The
# wording comes from S1 File (Annexure 1: Questionnaire items), which lists the
# three Perceived Behavioral Control sentences in order but attaches NO code to
# any of them. So the shipped mapping rests on one inference: the k-th sentence
# under a construct heading in the annexure is that construct's column k.
#
# This script re-runs the search for a route that could test that inference, and
# banks the numbers behind the NO_ROUTE verdict. VERDICT: PASS means "the facts
# recorded in verification_liu_2023_perceived_control.csv reproduce", NOT that
# the item_text<->item mapping was confirmed. It was not, and no route exists.

suppressMessages(library(irw))

TABLE <- "liu_2023_perceived_control"
ITEMS <- c("PBC1", "PBC2", "PBC3")

# PLoS ONE 18(12):e0295133, Table 2 (Reliability and validity), PBC block.
PUB_LOADING <- c(PBC1 = 0.743, PBC2 = 0.796, PBC3 = 0.726)
PUB_ALPHA   <- 0.852

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, ITEMS]
w <- w[complete.cases(w), ]
cat(sprintf("n complete cases: %d\n\n", nrow(w)))

# --- (1) Cronbach's alpha: reproduces the published value, and establishes only
#         that the three live codes are the three PBC columns the paper analysed.
k <- ncol(w)
alpha <- k / (k - 1) * (1 - sum(apply(w, 2, var)) / var(rowSums(w)))
cat(sprintf("alpha: published %.3f, observed %.4f, diff %.4f\n\n",
            PUB_ALPHA, alpha, alpha - PUB_ALPHA))

# --- (2) Route 1 (per-item published statistics). The only per-item numbers the
#         paper prints are the Table 2 standardised loadings. They come from the
#         full 19-item, 6-factor CFA; the closed-form congeneric solution for a
#         standalone 3-indicator factor is the best offline reconstruction, and
#         its RANK ORDER disagrees with the published one -- so the loadings
#         cannot be used to pin anything.
r <- cor(w)
lam <- c(PBC1 = sqrt(r[1,2] * r[1,3] / r[2,3]),
         PBC2 = sqrt(r[1,2] * r[2,3] / r[1,3]),
         PBC3 = sqrt(r[1,3] * r[2,3] / r[1,2]))
cat(sprintf("%-6s %10s %10s\n", "item", "published", "congeneric"))
for (i in ITEMS) cat(sprintf("%-6s %10.3f %10.3f\n", i, PUB_LOADING[i], lam[i]))
cat(sprintf("published rank order: %s\n", paste(names(sort(-PUB_LOADING)), collapse = " > ")))
cat(sprintf("observed  rank order: %s\n", paste(names(sort(-lam)), collapse = " > ")))
rank_ok <- identical(names(sort(-PUB_LOADING)), names(sort(-lam)))
cat(sprintf("rank orders agree: %s (route 1 is %s)\n\n", rank_ok,
            if (rank_ok) "usable" else "DEAD"))

# --- (3) Route 8 (semantic coherence of the response distribution). Means are
#         ordered confidence > channels > resources-and-time, which is the
#         intuitive endorsement order, but the prior is unpublished judgment and
#         the PBC2/PBC3 gap is small.
m <- colMeans(w); s <- apply(w, 2, sd)
for (i in ITEMS) cat(sprintf("%-6s mean %.3f  sd %.3f\n", i, m[i], s[i]))
t23 <- t.test(w$PBC2, w$PBC3, paired = TRUE)
t12 <- t.test(w$PBC1, w$PBC2, paired = TRUE)
cat(sprintf("paired PBC1-PBC2: diff %.3f, t = %.2f, p = %.4g\n",
            m["PBC1"] - m["PBC2"], t12$statistic, t12$p.value))
cat(sprintf("paired PBC2-PBC3: diff %.3f, t = %.2f, p = %.4g\n\n",
            m["PBC2"] - m["PBC3"], t23$statistic, t23$p.value))

# --- (4) Routes that need no computation to rule out.
cat("route 2 (differing resp ranges): DEAD -- all 3 items are 1-5, 5 levels each.\n")
cat("route 3 (published subscale totals): DEAD -- the paper prints no PBC total M/SD.\n")
cat("route 5 (subscale block structure): DEAD -- all 3 items are one subscale.\n")
cat("route 6 (keying polarity): DEAD -- all 3 items are positively worded, r = ",
    sprintf("%.2f/%.2f/%.2f", r[1,2], r[1,3], r[2,3]), ".\n", sep = "")
cat("route 7 (marker item): DEAD -- no item has an unmistakable distribution.\n")
cat("source labels: DEAD -- S1 Data XLSX header row is bare PBC1/PBC2/PBC3,\n",
    "  no variable or value labels; S1 File attaches no code to any sentence.\n", sep = "")

cat("\nNOT ESTABLISHED: which of the three annexure sentences is PBC1, PBC2 or PBC3.\n")
cat("3! = 6 assignments remain consistent with every fact above; the shipped one is\n")
cat("the annexure's own listing order. This script confirms that no route separates them.\n")

ok <- abs(alpha - PUB_ALPHA) <= 0.005 && !rank_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
