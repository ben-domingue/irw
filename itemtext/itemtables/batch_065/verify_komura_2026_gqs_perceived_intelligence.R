# verify_komura_2026_gqs_perceived_intelligence.R
#
# Step 5b evidence, re-runnable. mapping_basis = paper_explicit: the IRW item
# codes ARE the S3 workbook's own column names (data/komura_2026_godspeed.py
# melts gqs_perceived_intelligence_1..5 by name), and what ties a code to WORDS
# is the S2 File's numbered list under "Perceived Intelligence:".
#
# Four checks, none of which re-counts items:
#   A. BRIDGE   -- per-item x resp frequency, S3 columns vs live table, cell for cell.
#   B. ROUTE 3  -- live per-condition means/SDs vs the paper's Table 3 PI row.
#                  Pins subscale membership + raw (unreversed) storage + direction.
#   C. DUPLICATE-ANCHOR -- S2 prints "Unresponsive <-> Responsive" twice: Animacy 4
#                  and Perceived Intelligence 2. If item 2 is that anchor, PI_2 x
#                  animacy_4 should be the max of the 5x5 PI x Animacy correlation
#                  matrix. Pins item 2.
#   D. CONTENT  -- item 4 is the only moral-trust anchor in the block
#                  ("Irresponsible <-> Responsible"). Its partial correlation with
#                  the MDMT Ethical subscale mean, controlling for the other four
#                  PI items, should be the largest of the five. Pins item 4.
#
# NOT established: items 1, 3 and 5 (Incompetent-Competent, Ignorant-Knowledgeable,
# Unintelligent-Intelligent) are not separated from one another by any route here.
# Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "komura_2026_gqs_perceived_intelligence"
PI    <- paste0("gqs_perceived_intelligence_", 1:5)
AN    <- paste0("gqs_animacy_", 1:5)
ETH   <- paste0("mdmt_ethical_", 1:4)

# Paper Table 3, "Perceived Intelligence" row (10.1371/journal.pone.0340449.t003),
# read off the table image: M (SD) by AI-strategy condition.
PUB <- data.frame(cond = c("vertical", "horizontal", "random"),
                  m    = c(3.70, 3.45, 3.57),
                  sd   = c(0.81, 0.77, 0.75))

S3 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0340449.s003")
tmp <- tempfile(fileext = ".xlsx")
download.file(S3, tmp, quiet = TRUE, mode = "wb",
              headers = c("User-Agent" = "IRW-itemtext/1.0"))
raw <- as.data.frame(read_excel(tmp, sheet = "questionnaires"))

d <- irw::irw_fetch(TABLE)
ok <- TRUE

## ---- A. bridge: S3 column -> live item, by resp frequency -------------------
cat("=== A. S3 column vs live item: resp-level counts (must match cell for cell) ===\n")
cat(sprintf("%-30s %-18s %-18s\n", "item", "S3 counts 1..5", "live counts 1..5"))
for (v in PI) {
    s3c <- as.integer(table(factor(raw[[v]], levels = 1:5)))
    lvc <- as.integer(table(factor(d$resp[d$item == v], levels = 1:5)))
    same <- identical(s3c, lvc)
    ok <- ok && same
    cat(sprintf("%-30s %-18s %-18s %s\n", v,
                paste(s3c, collapse = "/"), paste(lvc, collapse = "/"),
                if (same) "match" else "MISMATCH"))
}

## ---- B. route 3: published subscale means by condition ----------------------
cat("\n=== B. Perceived Intelligence subscale mean by condition vs paper Table 3 ===\n")
dd <- as.data.frame(d)
w <- reshape(dd[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cond <- dd$cov_aitype[match(w$id, dd$id)]
cond[cond == "unknown"] <- "random"   # paper Table 1 gives Random n = 46 = 40 + 6
w$m <- rowMeans(w[, PI, drop = FALSE])
cat(sprintf("%-12s %5s %10s %10s %8s %8s %8s\n",
            "condition", "n", "pub M", "obs M", "dM", "pub SD", "obs SD"))
worst <- 0
for (k in seq_len(nrow(PUB))) {
    g  <- w$m[cond == PUB$cond[k]]
    dm <- mean(g) - PUB$m[k]; ds <- sd(g) - PUB$sd[k]
    worst <- max(worst, abs(dm), abs(ds))
    cat(sprintf("%-12s %5d %10.2f %10.3f %8.3f %8.2f %8.3f\n",
                PUB$cond[k], length(g), PUB$m[k], mean(g), dm, PUB$sd[k], sd(g)))
}
cat(sprintf("largest deviation: %.3f (tolerance 0.01)\n", worst))
ok <- ok && worst <= 0.01

## ---- C. duplicate anchor pins item 2 ---------------------------------------
cat("\n=== C. PI x Animacy cross-block correlations (S3); PI_2 & animacy_4 share",
    "\n       the anchor 'Unresponsive <-> Responsive' ===\n")
cm <- cor(raw[, PI], raw[, AN], use = "complete.obs")
print(round(cm, 3))
mx <- which(cm == max(cm), arr.ind = TRUE)
cat(sprintf("\nmatrix maximum: %s x %s = %.3f\n",
            PI[mx[1, "row"]], AN[mx[1, "col"]], max(cm)))
c_pin <- rownames(cm)[mx[1, "row"]] == "gqs_perceived_intelligence_2" &&
         colnames(cm)[mx[1, "col"]] == "gqs_animacy_4"
cat(sprintf("next largest entry in the gqs_animacy_4 column: %.3f\n",
            max(cm[rownames(cm) != "gqs_perceived_intelligence_2", "gqs_animacy_4"])))
cat(if (c_pin) "-> pins item 2\n" else "-> DOES NOT pin item 2\n")
ok <- ok && c_pin

## ---- D. item 4 is the moral-trust anchor -----------------------------------
cat("\n=== D. partial r of each PI item with the MDMT Ethical mean,",
    "controlling for\n       the other four PI items (S3) ===\n")
eth <- rowMeans(raw[, ETH])
pr <- sapply(PI, function(v) {
    ctrl <- setdiff(PI, v)
    X  <- as.matrix(cbind(1, raw[, ctrl]))
    ry <- resid(lm.fit(X, raw[[v]]))
    rx <- resid(lm.fit(X, eth))
    cor(ry, rx)
})
for (v in PI) cat(sprintf("%-30s %7.3f\n", v, pr[[v]]))
d_pin <- names(which.max(pr)) == "gqs_perceived_intelligence_4"
cat(sprintf("largest: %s (%.3f); next largest %.3f\n", names(which.max(pr)),
            max(pr), max(pr[names(pr) != "gqs_perceived_intelligence_4"])))
cat(if (d_pin) "-> pins item 4\n" else "-> DOES NOT pin item 4\n")
ok <- ok && d_pin

cat("\nNOT ESTABLISHED: nothing above separates gqs_perceived_intelligence_1,\n",
    "_3 and _5 from one another (means 3.669 / 3.669 / 3.615, corrected\n",
    "item-totals 0.827 / 0.834 / 0.852). Their order rests solely on the S2\n",
    "File's within-block numbering matching the S3 column suffixes. PARTIAL.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
