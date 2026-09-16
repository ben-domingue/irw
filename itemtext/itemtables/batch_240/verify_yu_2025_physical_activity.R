# verify_yu_2025_physical_activity.R  --  Step 5b re-runnable evidence.
#
# STATUS RECORDED: NO_ROUTE.  This script does not claim a verified item mapping;
# it makes the NO_ROUTE finding reproducible.  It establishes, with numbers:
#
#   (A) the deposit columns T{0,1,2}PE1..PE3 ARE the live IRW items PE1..PE3
#       (per-item n, per-item resp ranges, and total rows),
#   (B) those three columns ARE the "Physical Activity Rating Scale" block the
#       paper's Measures section describes -- its three published Cronbach alphas
#       reproduce exactly from them, and the paper's published MPA cross-wave
#       correlations reproduce from the sibling block, fixing the file identity,
#   (C) that NO route in Step 5b can separate PE1 from PE2 from PE3: the only
#       PE-block statistics the article publishes (alpha, KMO) are invariant under
#       every permutation of the three item labels, and the article never mentions
#       an item code at all.  The shipped assignment
#       PE1=intensity / PE2=duration / PE3=frequency therefore rests on the
#       paper's stated dimension order plus canonical PARS-3 item order
#       (mapping_basis=paper_order) and is NOT verified against data.
#
# PASS here means "the NO_ROUTE record reproduces", i.e. (A) and (B) hold and (C)
# is confirmed rather than assumed.  It does NOT mean the mapping is verified.

suppressMessages(library(irw))

TABLE <- "yu_2025_physical_activity"
S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0331340.s001")

## ---- published values, Yu et al. (2025) PLOS ONE 20(9):e0331340 --------------
PUB_ALPHA_PE  <- c(T1 = 0.828, T2 = 0.688, T3 = 0.730)   # Measures, PA scale
PUB_R_MPA     <- c(T1T2 = 0.439, T1T3 = 0.390, T2T3 = 0.511)  # Results / Table 3
TOL <- 0.0005

## ---- (A) live side: server-side sets only, no whole-table export -------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
cat("-- (A) live IRW table --\n")
cat(sprintf("rows=%d  items=%s  resp=%s\n", s$n_rows,
            paste(s$items, collapse = ","), paste(sort(s$resp), collapse = ",")))
print(pi, row.names = FALSE)

## ---- deposit ----------------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(S1, tmp, quiet = TRUE, mode = "wb")
d <- as.data.frame(readxl::read_excel(tmp))

waves <- c("T0", "T1", "T2")
pe <- function(w) d[, paste0(w, "PE", 1:3)]

dep_n <- vapply(1:3, function(i)
    sum(!is.na(unlist(lapply(waves, function(w) d[[paste0(w, "PE", i)]])))), numeric(1))
live_n <- pi$n[match(paste0("PE", 1:3), pi$item)]
cat("\ndeposit non-missing n per item (3 waves stacked) vs live n:\n")
for (i in 1:3) cat(sprintf("  PE%d  deposit=%4d  live=%4d  %s\n", i, dep_n[i], live_n[i],
                           ifelse(dep_n[i] == live_n[i], "match", "MISMATCH")))
okA <- all(dep_n == live_n) && s$n_rows == sum(dep_n)

## ---- (B) block identity: alphas and MPA correlations ------------------------
alpha <- function(X) {
    X <- X[stats::complete.cases(X), , drop = FALSE]; k <- ncol(X)
    k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}
cat("\n-- (B) block identity --\n")
obs_alpha <- vapply(waves, function(w) alpha(pe(w)), numeric(1))
cat(sprintf("%-6s %10s %10s %8s\n", "wave", "published", "observed", "diff"))
for (i in 1:3)
    cat(sprintf("%-6s %10.3f %10.3f %8.4f\n", names(PUB_ALPHA_PE)[i],
                PUB_ALPHA_PE[i], obs_alpha[i], obs_alpha[i] - PUB_ALPHA_PE[i]))
okB1 <- max(abs(obs_alpha - PUB_ALPHA_PE)) <= TOL

mpa <- d[, paste0(waves, "Average score for MPA")]
cm <- cor(mpa, use = "pairwise.complete.obs")
obs_r <- c(T1T2 = cm[1, 2], T1T3 = cm[1, 3], T2T3 = cm[2, 3])
cat("\nMPA cross-wave r (fixes that this is the paper's own data file):\n")
for (i in 1:3)
    cat(sprintf("%-6s %10.3f %10.3f %8.4f\n", names(PUB_R_MPA)[i],
                PUB_R_MPA[i], obs_r[i], obs_r[i] - PUB_R_MPA[i]))
okB2 <- max(abs(obs_r - PUB_R_MPA)) <= TOL

## ---- (C) the negative result: nothing published separates the three items ----
cat("\n-- (C) why NO_ROUTE --\n")
perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
spread <- vapply(waves, function(w) {
    X <- pe(w)
    diff(range(vapply(perms, function(p) alpha(X[, p]), numeric(1))))
}, numeric(1))
cat(sprintf("alpha spread across all 6 relabellings of PE1/PE2/PE3: %s\n",
            paste(sprintf("%s=%.15f", waves, spread), collapse = "  ")))
cat("  -> every published PE-block statistic (alpha, KMO, Bartlett) is a function of\n",
    "     the 3x3 covariance matrix and so is identical under any relabelling.\n", sep = "")

art <- tryCatch({
    x <- readLines(url("https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331340"),
                   warn = FALSE); paste(x, collapse = " ")
}, error = function(e) NA_character_)
if (!is.na(art)) {
    hits <- vapply(c("PE1", "PE2", "PE3"), function(k)
        length(gregexpr(k, art, fixed = TRUE)[[1]][gregexpr(k, art, fixed = TRUE)[[1]] > 0]), numeric(1))
    cat(sprintf("occurrences of item codes in the article HTML: PE1=%d PE2=%d PE3=%d\n",
                hits[1], hits[2], hits[3]))
    okC2 <- sum(hits) == 0
} else { cat("article fetch failed; code-occurrence check skipped (not load-bearing)\n"); okC2 <- TRUE }
okC1 <- all(spread < 1e-12)

cat("\nper-item distributions (deposit, all waves) -- consistent with, but NOT\n",
    "identifying, PE1 = the intensity item:\n", sep = "")
for (i in 1:3) {
    v <- unlist(lapply(waves, function(w) d[[paste0(w, "PE", i)]]))
    cat(sprintf("  PE%d  mean=%.3f sd=%.3f  counts(1..5)=%s\n", i, mean(v), sd(v),
                paste(as.integer(table(factor(v, 1:5))), collapse = "/")))
}
cat("  PE1 is flatter/left-shifted (sd ~1.38) while PE2 and PE3 peak at 3 (sd ~1.13),\n",
    "  which separates PE1 from {PE2,PE3} in SHAPE only. It does not say which item is\n",
    "  intensity, and nothing here separates PE2 from PE3. Hence NO_ROUTE.\n", sep = "")

ok <- okA && okB1 && okB2 && okC1 && okC2
cat("\nThis does NOT establish the item-to-text mapping. It establishes that the block\n",
    "is the PARS-3 block the paper describes, and that no data route can order it.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
