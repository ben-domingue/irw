# verify_anh_2026_digitaltrust.R -- Step 5b mapping verification.
#
# CLAIM: the six Digital Trust item wordings transcribed from the paper's Table 3
# (PLOS ONE 10.1371/journal.pone.0340002, "Measurement model assessment"), which
# are printed against the variable codes DT 1..DT6, belong to the live IRW items
# DT1..DT6 in that same order.
#
# WHY THAT NEEDS CHECKING: the wording came from an image of Table 3, and Table 3
# is a separate artifact from the S1 File data. Nothing but the code strings ties
# them together, so a block-boundary slip or a row permutation inside the DT block
# would be invisible to validate_items.R (the item set would still match).
#
# ROUTE: Table 3 publishes a per-item VIF for every item. VIF_i for item i within
# the six-item DT block is 1/(1 - R^2) from regressing DT_i on the other five --
# a deterministic function of the S1 File's own DT columns, and a per-item
# fingerprint. If the paper's DT rows were in any other order than the CSV's DT
# columns, the reproduced VIF vector would not line up. Published loadings and AVE
# are compared as a secondary check.
#
# The S1 CSV column names ARE the live item codes: data/anh_2026_finwellbeing.py
# melts value_vars=["DT1".."DT6"] by name (no positional assignment), so there is
# no mapping step between the CSV column and the live `item`. irw_table_sets()
# is used to confirm the live item set and per-item n against the CSV.

suppressMessages(library(irw))

TABLE <- "anh_2026_digitaltrust"
ITEMS <- paste0("DT", 1:6)

# --- Published values, PLOS ONE 10.1371/journal.pone.0340002 Table 3, DT block ---
PUB_VIF  <- c(1.694, 1.823, 1.987, 1.986, 2.102, 2.440)
PUB_LOAD <- c(0.719, 0.782, 0.802, 0.790, 0.811, 0.851)
PUB_AVE  <- 0.630
TOL_VIF  <- 0.0008  # measured max dev is 4e-4; a DT3<->DT4 swap costs 1e-3, so this fails it

URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0340002.s001")
f <- tempfile(fileext = ".csv")
utils::download.file(URL, f, quiet = TRUE,
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
raw <- utils::read.csv(f, check.names = FALSE)

stopifnot(all(ITEMS %in% names(raw)))
X <- as.matrix(raw[, ITEMS])
X <- X[stats::complete.cases(X), , drop = FALSE]
cat(sprintf("S1 File: %d complete DT rows, %d DT columns\n", nrow(X), ncol(X)))

# --- live aggregates: server-side sets/counts, no table export ---
sets <- irw::irw_table_sets(TABLE)
live_items <- sort(as.character(sets$item))
cat("live item set:", paste(live_items, collapse = ", "), "\n")
cat("live resp set:", paste(sort(as.numeric(sets$resp)), collapse = ", "), "\n")
set_ok <- identical(live_items, sort(ITEMS))

# --- reproduce Table 3's per-item VIF from the S1 columns ---
R  <- stats::cor(X)
Ri <- solve(R)
vif <- diag(Ri)

cat(sprintf("\n%-6s %10s %10s %9s\n", "item", "pub VIF", "obs VIF", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %10.3f %10.3f %9.4f\n",
                ITEMS[i], PUB_VIF[i], vif[i], vif[i] - PUB_VIF[i]))
worst <- max(abs(vif - PUB_VIF))
cat(sprintf("largest VIF deviation: %.4f (tolerance %.4f)\n", worst, TOL_VIF))

# DT3 and DT4 are near-tied on VIF (1.987 vs 1.986); VIF alone does NOT separate
# them -- a swap costs only ~7e-4. The loading column is what does. Reported below.
sw <- vif; sw[c(3, 4)] <- sw[c(4, 3)]
cat(sprintf("if DT3/DT4 were swapped, largest VIF deviation would be %.4f (VIF alone: %s)\n",
            max(abs(sw - PUB_VIF)),
            if (max(abs(sw - PUB_VIF)) > TOL_VIF) "rejects it" else "does NOT separate them"))

# --- secondary: first-component loadings and AVE ---
e <- eigen(R, symmetric = TRUE)
load <- e$vectors[, 1] * sqrt(e$values[1])
if (load[1] < 0) load <- -load
ave <- mean(load^2)
cat(sprintf("\n%-6s %10s %10s %9s\n", "item", "pub load", "PC1 load", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-6s %10.3f %10.3f %9.3f\n",
                ITEMS[i], PUB_LOAD[i], load[i], load[i] - PUB_LOAD[i]))
cat(sprintf("AVE: published %.3f, PC1 %.3f\n", PUB_AVE, ave))
cat("(published loadings are PLS mode-A composite loadings, PC1 is a proxy;\n",
    " agreement to ~0.015 is expected, the VIF column is the exact check)\n", sep = "")
swl <- load; swl[c(3,4)] <- swl[c(4,3)]
cat(sprintf("DT3/DT4 loading residuals: as shipped %+.3f/%+.3f, if swapped %+.3f/%+.3f\n",
            load[3]-PUB_LOAD[3], load[4]-PUB_LOAD[4],
            swl[3]-PUB_LOAD[3], swl[4]-PUB_LOAD[4]))

# --- observed means, against the sibling-table warning about round numbers ---
cat(sprintf("\nS1 DT item means: %s\n",
            paste(sprintf("%.3f", colMeans(X)), collapse = " ")))

# --- what this does NOT establish ---
cat("\nNot established by this route: that the ENGLISH wording in Table 3 is what\n",
    "respondents read -- the study administered a Vietnamese translation that no\n",
    "deposited file contains. It also does not check the anchors for resp 2-4,\n",
    "which the source never labels and which ship blank.\n", sep = "")

# --- permutation test: is the shipped order the unique best fit? -------------
# Score every one of the 6! = 720 orderings of the shipped wording against BOTH
# published columns, on their own error scales. If the shipped order is the strict
# minimum, then every item is distinguished from every other item.
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(1:6)
score <- function(p) sum(abs(vif[p] - PUB_VIF)) / 0.001 +
                     sum(abs(load[p] - PUB_LOAD)) / 0.015
sc <- vapply(P, score, 0)
id <- which(vapply(P, function(p) identical(p, 1:6), TRUE))
ord <- order(sc)
cat(sprintf("\npermutation test over all %d orderings (lower = better fit):\n", length(P)))
cat(sprintf("  shipped order DT1..DT6 : score %.2f  (rank %d of %d)\n",
            sc[id], which(ord == id), length(P)))
cat(sprintf("  next-best ordering %s : score %.2f\n",
            paste0("DT", P[[ord[2]]], collapse = ""), sc[ord[2]]))
unique_best <- (which(ord == id) == 1L) && (sc[ord[2]] > sc[id])

ok <- set_ok && worst <= TOL_VIF && unique_best
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
