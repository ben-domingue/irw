# verify_thanh_2025_green_knowledge.R -- Step 5b mapping check (batch_187).
#
# Claim: GK1..GK6 carry the S1 Appendix wording of "Green Knowledge 1".."Green Knowledge 6"
# (Thanh & Cong 2025, PLoS ONE 10.1371/journal.pone.0320053).
#
# Route: the paper's Table 2 prints, per retained item WITH ITS WORDING, the SmartPLS 4 outer
# loading. Green Knowledge retains four statements (knowledgeable about env. issues 0.908;
# environment deteriorating 0.902; issues caused by employees 0.922; protect from air pollution
# 0.906) and drops two. Re-estimating the paper's PLS-SEM (path weighting scheme; structural
# model from Table 6: EC->ATT, EC->PBC, EC->GK, ATT/PBC/GK/EC->EGB; retained indicators as listed
# in Table 2) on the live GK table (other construct blocks from the same S1 File, joined on id)
# must reproduce those four loadings on exactly one assignment of live codes to the four
# published statements. We try every ordered choice of 4 of the 6 GK codes (6P4 = 360) and
# count the assignments whose loadings all round to the published values.
#
# What this does NOT establish: GK5 vs GK6. Both are the two dropped statements (not in Table 2),
# and no published statistic separates them; that pair rests on the S1 Appendix numbering only.

suppressMessages(library(irw))
TABLE <- "thanh_2025_green_knowledge"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0320053.s002"

PUB_GK <- c(knowledgeable = 0.908, deteriorating = 0.902, employees = 0.922, air_pollution = 0.906)
PUB_OTHER <- list(EGB = c(0.774, 0.880, 0.831, 0.832, 0.758), ATT = c(0.817, 0.836, 0.834),
                  EC = c(0.877, 0.882, 0.853, 0.912, 0.926), PBC = c(0.831, 0.901, 0.888, 0.900, 0.826))
TOL <- 0.0006  # published to 3 dp

live <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(live[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

tf <- tempfile(fileext = ".xlsx")
download.file(S1, tf, mode = "wb", quiet = TRUE, headers = c("User-Agent" = "Mozilla/5.0"))
raw <- as.data.frame(readxl::read_excel(tf))
names(raw)[names(raw) == "ID"] <- "id"
raw <- raw[, setdiff(names(raw), paste0("GK", 1:6))]
dat <- merge(raw, w, by = "id")
cat(sprintf("joined rows: %d (live ids %d, S1 ids %d)\n\n", nrow(dat), nrow(w), nrow(raw)))

pls_loadings <- function(dat, blocks) {
  lv <- names(blocks)
  B <- matrix(0, length(lv), length(lv), dimnames = list(lv, lv))  # B[i,j]=1: j -> i
  B["ATT", "EC"] <- 1; B["PBC", "EC"] <- 1; B["GK", "EC"] <- 1
  B["EGB", c("ATT", "PBC", "GK", "EC")] <- 1
  Z <- lapply(blocks, function(b) scale(as.matrix(dat[, b])))
  wt <- lapply(blocks, function(b) rep(1, length(b)))
  for (it in 1:1000) {
    Y <- sapply(lv, function(k) as.vector(scale(Z[[k]] %*% wt[[k]])))
    R <- cor(Y); E <- matrix(0, length(lv), length(lv), dimnames = list(lv, lv))
    for (i in lv) {
      pr <- lv[B[i, ] == 1]; su <- lv[B[, i] == 1]
      if (length(pr)) E[i, pr] <- solve(R[pr, pr, drop = FALSE], R[pr, i])
      if (length(su)) E[i, su] <- R[i, su]
    }
    Yt <- Y %*% t(E)
    wn <- lapply(seq_along(lv), function(j) {
      v <- as.vector(cor(Z[[j]], Yt[, j])); v / sd(as.vector(Z[[j]] %*% v)) })
    names(wn) <- lv
    done <- max(abs(unlist(wn) - unlist(wt))) < 1e-10
    wt <- wn
    if (done) break
  }
  Y <- sapply(lv, function(k) as.vector(scale(Z[[k]] %*% wt[[k]])))
  setNames(lapply(lv, function(k) setNames(as.vector(cor(Z[[k]], Y[, k])), blocks[[k]])), lv)
}

base_blocks <- list(EGB = paste0("EGB", 1:5), ATT = paste0("ATT", 1:3), EC = paste0("EC", 1:5),
                    PBC = paste0("PBC", 1:5), GK = paste0("GK", 1:4))
L <- pls_loadings(dat, base_blocks)

cat("Model-spec check -- other constructs vs Table 2:\n")
spec_ok <- TRUE
for (k in names(PUB_OTHER)) {
  d <- L[[k]] - PUB_OTHER[[k]]
  cat(sprintf("  %-4s obs %s | pub %s | max|diff| %.4f\n", k,
              paste(sprintf("%.4f", L[[k]]), collapse = " "),
              paste(sprintf("%.3f", PUB_OTHER[[k]]), collapse = " "), max(abs(d))))
  if (max(abs(d)) > TOL) spec_ok <- FALSE
}

cat("\nGreen Knowledge, claimed mapping (GK1..GK4 -> Table 2 statements in order):\n")
for (i in 1:4) cat(sprintf("  GK%d  obs %.4f  pub %.3f  (%s)  diff %+.4f\n", i, L$GK[i], PUB_GK[i],
                           names(PUB_GK)[i], L$GK[i] - PUB_GK[i]))

# Exhaustive: every ordered 4-of-6 assignment of live GK codes to the four published statements.
subsets <- combn(paste0("GK", 1:6), 4, simplify = FALSE)
perms <- function(v) if (length(v) == 1) list(v) else do.call(c, lapply(seq_along(v), function(i)
  lapply(perms(v[-i]), function(p) c(v[i], p))))
matches <- character(0); best_alt <- Inf
for (s in subsets) {
  bl <- base_blocks; bl$GK <- s
  Ls <- pls_loadings(dat, bl)$GK
  for (p in perms(s)) {
    dev <- max(abs(Ls[p] - PUB_GK))
    lab <- paste(p, collapse = ",")
    if (dev <= TOL) matches <- c(matches, lab)
    else if (lab != "GK1,GK2,GK3,GK4") best_alt <- min(best_alt, dev)
  }
}
cat(sprintf("\nassignments tried: %d; within %.4f of all four published loadings: %d [%s]\n",
            length(subsets) * 24, TOL, length(matches), paste(matches, collapse = " ; ")))
cat(sprintf("closest non-matching assignment misses by %.4f\n", best_alt))

C <- cor(dat[, paste0("GK", 1:6)])
cat(sprintf("\nGK5/GK6 (dropped pair): max |r| with GK1-4 = %.3f; GK1-4 inter-item r = %.3f-%.3f\n",
            max(abs(C[5:6, 1:4])), min(C[1:4, 1:4][upper.tri(diag(4))]), max(C[1:4, 1:4][upper.tri(diag(4))])))
cat("Not established: which of GK5/GK6 is 'educate the next generation' vs 'organize this meeting'.\n")

pass <- spec_ok && length(matches) == 1 && matches == "GK1,GK2,GK3,GK4"
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
