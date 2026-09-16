# verify_tsai_2017_treeit_h11_undo.R -- Step 5b mapping check (batch_192)
#
# Claim: live item codes H11-1..H11-4 (the S3 File's own column headers, used verbatim by
# data/tsai_2017_treeit.py) correspond, in order, to the four items printed under
# "H11. Undo" in S1 File (Appendix 1, Treeit Heuristic Evaluation, p.7):
#   H11-1 "Each single step of a function can be repeated and allow for returning to previous steps."
#   H11-2 "Each function has multiple steps and users can return to previous steps."
#   H11-3 "The system encourages exploratory learning."
#   H11-4 "The system can prevent serious errors."
# mapping_basis = paper_order (the form prints no per-item codes).
#
# The paper publishes no per-item statistics for heuristic items (Table 3 is at heuristic
# level: H11 loading 0.84, item-total 0.856), so the routes are:
#   0. tie: live per-item n/range (irw_table_sets, server-side) == S3 File columns
#   A. content coherence: the two near-synonymous "return to previous steps" items should be
#      each other's strongest correlate, far above any other H11 pair
#   B. content coherence: "prevent serious errors" should track the H9 "Error" (prevent errors)
#      block far more than the other three H11 items do
#   C. structure: H11 has 4 items on the S1 form and 4 S3 columns (13 of 14 heuristics agree;
#      H8 prints 4 items on the form but has 3 S3 columns -- a sibling-table issue, reported)
# NOT established: order WITHIN {H11-1, H11-2} (near-synonymous, means 4.56 vs 4.55);
# H11-3 is placed by elimination once {1,2} and 4 are pinned. Hence PARTIAL.

suppressMessages({ library(irw); library(readxl) })
TABLE <- "tsai_2017_treeit_h11_undo"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
ok <- TRUE

tmp <- tempfile(fileext = ".xlsx")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
raw <- read_excel(tmp, col_names = FALSE, .name_repair = "minimal")
hdr <- as.character(unlist(raw[2, ]))
d <- as.data.frame(raw[-(1:2), ])
names(d) <- hdr
hcols <- grep("^(H[0-9]+-[0-9]+)$", hdr, value = TRUE)
X <- as.data.frame(lapply(d[, hcols], function(v) suppressWarnings(as.numeric(v))))
names(X) <- hcols
h11 <- paste0("H11-", 1:4)

# --- 0. live table is these columns ---
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat("== 0. live per-item (server-side) vs S3 File columns ==\n")
for (it in h11) {
  v <- X[[it]][X[[it]] >= 1 & X[[it]] <= 5 & !is.na(X[[it]])]
  lv <- pi[pi$item == it, ]
  cat(sprintf("%-6s live n=%d range %d-%d | S3 n=%d range %d-%d\n", it, lv$n, lv$resp_min, lv$resp_max,
              length(v), min(v), max(v)))
  if (lv$n != length(v) || lv$resp_min != min(v) || lv$resp_max != max(v)) ok <- FALSE
}

C <- cor(X, use = "pairwise.complete.obs")

# --- A ---
cat("\n== A. within-H11 correlations ==\n")
print(round(C[h11, h11], 3))
r12 <- C["H11-1", "H11-2"]
others <- c(C["H11-1","H11-3"], C["H11-1","H11-4"], C["H11-2","H11-3"], C["H11-2","H11-4"], C["H11-3","H11-4"])
cat(sprintf("r(H11-1,H11-2) = %.3f ; max other H11 pair = %.3f\n", r12, max(others)))
if (!(r12 > max(others) + 0.3)) ok <- FALSE

# --- B ---
h9 <- grep("^H9-", hcols, value = TRUE)
cat("\n== B. mean r with H9 'Error' (prevent errors) items", paste(h9, collapse = ","), "==\n")
m9 <- sapply(h11, function(it) mean(C[it, h9]))
print(round(m9, 3))
for (it in h11) {
  top <- sort(C[it, setdiff(hcols, it)], decreasing = TRUE)[1:3]
  cat(sprintf("%-6s top correlates: %s\n", it, paste(sprintf("%s %.3f", names(top), top), collapse = ", ")))
}
if (!(which.max(m9) == 4 && m9[4] > max(m9[1:3]) + 0.2)) ok <- FALSE

# --- C ---
cat("\n== C. items per heuristic: S1 form (hard-coded, counted from Appendix 1) vs S3 columns ==\n")
FORM <- c(6, 4, 3, 4, 7, 4, 3, 4, 4, 3, 4, 3, 2, 3)
S3 <- sapply(1:14, function(h) sum(grepl(paste0("^H", h, "-"), hcols)))
print(rbind(form = FORM, S3 = S3))
cat(sprintf("H11: form %d, S3 %d\n", FORM[11], S3[11]))
if (FORM[11] != S3[11] || FORM[11] != 4) ok <- FALSE
cat("Heuristics where form and S3 disagree (not this table; reported, not gated):",
    paste0("H", which(FORM != S3), " form ", FORM[FORM != S3], " vs S3 ", S3[FORM != S3], collapse = "; "), "\n")

# --- caveat: near-identical response columns across the whole S3 File ---
cat("\n== caveat: item pairs with >=93 of 101 identical responses (whole S3 heuristic block) ==\n")
pr <- combn(hcols, 2)
same <- apply(pr, 2, function(p) sum(X[[p[1]]] == X[[p[2]]], na.rm = TRUE))
cat(sprintf("%d of %d pairs; involving H11: %s\n", sum(same >= 93), ncol(pr),
            paste(apply(pr[, same >= 93 & (grepl("^H11", pr[1, ]) | grepl("^H11", pr[2, ])), drop = FALSE], 2,
                        paste, collapse = "="), sprintf("(%s)", same[same >= 93 & (grepl("^H11", pr[1, ]) | grepl("^H11", pr[2, ]))]),
                  collapse = ", ")))
cat("Content-unrelated pairs are also near-identical (e.g. H2-4 = H6-3), so routes A/B are\n",
    "consistent with the mapping but cannot exclude a data-entry pattern as their cause.\n", sep = "")

cat("\nNot established: order within {H11-1, H11-2} (near-synonymous; means",
    sprintf("%.3f vs %.3f", mean(X[["H11-1"]]), mean(X[["H11-2"]])),
    "); H11-3 placed by elimination. Status PARTIAL.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
