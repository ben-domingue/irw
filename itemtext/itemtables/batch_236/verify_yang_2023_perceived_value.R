# verify_yang_2023_perceived_value.R
#
# CLAIM UNDER TEST (Step 5b): the item_text shipped for live items E1, E2, E3 of
# `yang_2023_perceived_value` is the CONSUMPTION INTENTION block of Yang et al.
# (2023) PLOS ONE 18(10):e0292633 Table 1 -- NOT the "perceived value" block the
# IRW table name asserts. The paper's Table 1 assigns E1-E3 to "Consumption
# intention" and F1-F4 to "Customer perceived value"; data/yang_2023_green_brand.py
# ships E1-E3 under the name yang_2023_perceived_value, so the two IRW table names
# are swapped. Per the Step 3b rule the extraction follows the live data.
#
# The falsifiable prediction: the paper's Table 3 publishes Cronbach's alpha and
# standardized factor loadings PER LATENT VARIABLE against the very codes the raw
# file uses. If the E block really is "Consumption intention", recomputing alpha
# from the study's own S1 File must land on .934, not on the .849 that Table 3
# prints for "Customer perceived value".
#
# This script fetches the S1 File (the study's own data) and queries the live IRW
# table's per-item aggregates SERVER-SIDE via irw_table_sets(); it never exports
# the table.

suppressMessages(library(irw))

TABLE <- "yang_2023_perceived_value"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0292633.s001"
S1_SHA256 <- "5aabb592951f0b0bff81eab1baeb0203fce733c461bdf8f04a495758eea4504e"

# Paper Table 3 (t003, image-only), verbatim.
PUB_ALPHA <- c(A = 0.807, B = 0.779, C = 0.712, D = 0.743,
               F = 0.849,   # "Customer perceived value"
               E = 0.934)   # "Consumption intention"
PUB_LOADINGS_E <- c(E1 = 0.893, E2 = 0.896, E3 = 0.836)

BLOCKS <- list(A = c("A1","A2","A3"), B = c("B1","B2","B3"),
               C = c("C1","C2","C4"),          # raw file has C4 where Table 1 prints C3
               D = c("D1","D2","D3"),
               E = c("E1","E2","E3"), F = c("F1","F2","F3","F4"))

tmp <- tempfile(fileext = ".csv")
utils::download.file(S1, tmp, quiet = TRUE)
d <- utils::read.csv(tmp, check.names = FALSE)
cat(sprintf("S1 File: %d rows, %d columns\n\n", nrow(d), ncol(d)))

cronbach <- function(X) {
    k <- ncol(X); S <- stats::cov(X, use = "complete.obs")
    (k / (k - 1)) * (1 - sum(diag(S)) / sum(S))
}

cat("-- ROUTE 3: Cronbach's alpha per letter block, recomputed vs paper Table 3 --\n")
cat(sprintf("%-6s %-28s %10s %10s %8s\n", "block", "Table 3 latent variable",
            "published", "observed", "diff"))
LABS <- c(A = "Agribusiness image", B = "Agricultural product image",
          C = "Social Image of Agribusiness", D = "Consumer image",
          E = "Consumption intention", F = "Customer perceived value")
obs_alpha <- sapply(BLOCKS, function(v) cronbach(d[, v]))
for (b in names(BLOCKS))
    cat(sprintf("%-6s %-28s %10.3f %10.4f %8.4f\n", b, LABS[b],
                PUB_ALPHA[b], obs_alpha[b], obs_alpha[b] - PUB_ALPHA[b]))
worst_alpha <- max(abs(obs_alpha[names(PUB_ALPHA)] - PUB_ALPHA))
cat(sprintf("\nlargest alpha deviation across all six blocks: %.4f\n", worst_alpha))
cat(sprintf("E block alpha %.4f -- matches 'Consumption intention' (%.3f, diff %.4f),\n",
            obs_alpha["E"], PUB_ALPHA["E"], obs_alpha["E"] - PUB_ALPHA["E"]))
cat(sprintf("  misses 'Customer perceived value' (%.3f) by %.3f.\n\n",
            PUB_ALPHA["F"], abs(obs_alpha["E"] - PUB_ALPHA["F"])))

cat("-- ROUTE 1: standardized one-factor loadings on E1,E2,E3 vs Table 3 --\n")
R <- stats::cor(d[, BLOCKS$E])
l <- c(E1 = sqrt(R[1,2]*R[1,3]/R[2,3]),
       E2 = sqrt(R[1,2]*R[2,3]/R[1,3]),
       E3 = sqrt(R[1,3]*R[2,3]/R[1,2]))   # exact, 3 indicators = just-identified
cat(sprintf("%-4s %10s %10s\n", "item", "published", "observed"))
for (i in names(l)) cat(sprintf("%-4s %10.3f %10.3f\n", i, PUB_LOADINGS_E[i], l[i]))
cat(sprintf("rank order published: %s | observed: %s\n\n",
            paste(names(sort(PUB_LOADINGS_E)), collapse = " < "),
            paste(names(sort(l)), collapse = " < ")))

cat("-- Tie from the S1 File to the live IRW table (server-side aggregates) --\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
src_n <- sapply(BLOCKS$E, function(v) sum(!is.na(d[[v]]) & d[[v]] >= 1 & d[[v]] <= 5))
cat(sprintf("%-4s %10s %10s\n", "item", "S1 n", "live n"))
for (i in BLOCKS$E)
    cat(sprintf("%-4s %10d %10d\n", i, src_n[i], pi$n[pi$item == i]))
n_ok <- all(sapply(BLOCKS$E, function(i) src_n[i] == pi$n[pi$item == i])) &&
        setequal(pi$item, BLOCKS$E)

cat("\nWHAT THIS DOES NOT ESTABLISH: the alpha match identifies the BLOCK (E is the\n")
cat("  .934 Consumption intention factor, not the .849 Customer perceived value one)\n")
cat("  and the loadings separate E3 (lowest in both, .836 published / .825 observed)\n")
cat("  from {E1,E2}; they do NOT separate E1 from E2, whose published loadings differ\n")
cat("  by .003. Within that pair the mapping rests on Table 1's explicit E1/E2/E3 code\n")
cat("  labels, and this paper's code labels slip once (Table 1 prints C3 where the raw\n")
cat("  file's column is C4). The per-item n are 341 for all three items, so they tie\n")
cat("  the block to the live table but distinguish no item from another. The\n")
cat("  option_text<->resp axis is not tested here at all: the paper names only the two\n")
cat("  endpoints (1 = disagree, 5 = agree). Hence PARTIAL, not VERIFIED.\n\n")

pass <- (worst_alpha <= 0.001) &&
        (abs(obs_alpha["E"] - PUB_ALPHA["E"]) < abs(obs_alpha["E"] - PUB_ALPHA["F"])) &&
        (names(sort(l))[1] == "E3") && n_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
