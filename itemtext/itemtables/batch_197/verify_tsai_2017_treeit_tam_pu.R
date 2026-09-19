# verify_tsai_2017_treeit_tam_pu.R -- Step 5b mapping check (batch_197).
# Built from references/verify_template.R, following the sibling
# batch_196/verify_tsai_2017_treeit_tam_bi.R approach.
#
# CLAIM: live item codes PU1..PU5 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and PUk is the k-th statement of
# "Section Two: TAM Questions" in the study's S2 File (Appendix 2, TreeIt Technology Acceptance
# Model Questionnaire, pone.0180102.s002; statements 1-3 on p.1, 4-5 at the top of p.2):
#   PU1 "Using the TreeIt system helps me understand my social status."
#   PU2 "Using the TreeIt system helps me quickly analyze my social status."
#   PU3 "Compared to other SNSs, the TreeIt system provides more complete inspection of my social status."
#   PU4 "Compared to other SNSs, it is more convenient to use the TreeIt system."
#   PU5 "Overall, I think the TreeIt system is useful for me."
# S2 prints no construct headers and no item numbers. Paper Table 3 labels the Perceived
# Usefulness items PU1..PU5 (and the BI items BI12..BI15, i.e. questionnaire positions), and gives
# each its own item-total r.
#
# ROUTES:
#   A. Route 1 (per-item statistics): Table 3 item-total r PU1..PU5 = 0.876 / 0.870 / 0.860 /
#      0.838 / 0.874, PU alpha 0.912; Table 4 PU mean 4.085. Uncorrected r of each xlsx PU column
#      with the PU sum must reproduce them IN ORDER. PEOU and BI checked with the same definitions.
#   A2. Controls, each scored against the WHOLE PU profile (5 item-total r + alpha + mean):
#      all 119 non-identity orderings of PU1..PU5; window shifted one right [PU2..PEOU1]; every other
#      contiguous 5-column Likert window; every single foreign-column replacement (63 x 5).
#      THIN PAIR: PU1 0.876 vs PU5 0.874 differ by 0.002 in print. Reported against both the family
#      tolerance (0.0015) and the 3-dp rounding half-width (0.0005).
#   A3. Corroboration for the thin pair (scored): rank order of one-factor ML loadings must equal the
#      rank order of Table 3's (LISREL, not reproduced exactly) PU loadings 0.87/0.86/0.80/0.77/0.84.
#   B. Block layout: xlsx columns 6-10 = PU1..PU5, then PEOU1..6, BI1..4 (15 = S2's 15 statements).
#   C. Live table == the xlsx PU columns (per-item response-level counts 1..5; 505 rows).
#   D. (not scored) within-block correlations / identical answers vs wording similarity.
#
# NOT ESTABLISHED by any route: that Table 3's PU1..PU5 numbering follows S2's print order (an
# upstream labelling fact the data cannot test; consistent with BI12..BI15 = positions 12-15 and
# 5 PU + 6 PEOU + 4 BI = 15 statements). Nothing here speaks to the wording itself or to the
# administered (Chinese) language; the anchors' numeric direction rests on the article Methods.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_tam_pu"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_tam_pu/s003.xlsx"  # fallback if offline
PU <- paste0("PU", 1:5)
TOL <- 0.0015
ROUND <- 0.0005

tmp <- tempfile(fileext = ".xlsx")
got <- tryCatch({ download.file(SI, tmp, mode = "wb", quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!got || file.size(tmp) < 1000) {
  cands <- c(CACHE, sub("^itemtext/", "", CACHE), file.path("..", "..", CACHE), file.path("..", "..", "..", CACHE))
  hit <- cands[file.exists(cands)]
  if (!length(hit)) stop("S3 xlsx neither downloadable nor cached")
  tmp <- hit[1]; cat("(using cached S3 xlsx)\n")
}
raw <- as.data.frame(readxl::read_excel(tmp, col_names = FALSE, .name_repair = "minimal"))
hdr <- as.character(unlist(raw[2, ]))
dat <- raw[-(1:2), , drop = FALSE]
names(dat) <- hdr
num <- function(cc) sapply(dat[cc], function(v) as.numeric(v))
alpha <- function(X) { k <- ncol(X); k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X))) }
itc <- function(X) apply(X, 2, function(x) cor(x, rowSums(X)))
ok <- TRUE

# ---- Route B
likert <- hdr[6:length(hdr)]
cat("Route B -- xlsx columns 6-20:", paste(hdr[6:20], collapse = " "), "\n")
cat("  S2 prints 15 TAM statements; Table 3 labels PU1-5, PEOU1-6, BI12-15\n")
if (!identical(hdr[6:20], c(PU, paste0("PEOU", 1:6), paste0("BI", 1:4)))) ok <- FALSE

# ---- Route A
pub <- list(
  PU   = list(cc = PU, a = 0.912, itc = c(0.876, 0.870, 0.860, 0.838, 0.874), mean = 4.085),
  PEOU = list(cc = paste0("PEOU", 1:6), a = 0.905, itc = c(0.860, 0.842, 0.825, 0.780, 0.756, 0.873), mean = 4.170),
  BI   = list(cc = paste0("BI", 1:4), a = 0.923, itc = c(0.916, 0.912, 0.896, 0.886), mean = 4.020))
cat("\nRoute A -- paper Table 3 (alpha, per-item item-total r) and Table 4 (construct mean)\n")
for (nm in names(pub)) {
  p <- pub[[nm]]; X <- num(p$cc)
  a <- alpha(X); r <- itc(X); mu <- mean(rowMeans(X))
  cat(sprintf("%-4s alpha published %.3f observed %.5f | mean published %.3f observed %.5f\n", nm, p$a, a, p$mean, mu))
  lab <- if (nm == "BI") paste0("BI", 12:15) else p$cc
  for (i in seq_along(p$cc))
    cat(sprintf("     xlsx %-6s vs Table 3 %-6s item-total published %.3f observed %.5f\n", p$cc[i], lab[i], p$itc[i], r[i]))
  dev <- max(abs(a - p$a), abs(r - p$itc), abs(mu - p$mean))
  cat(sprintf("     max|dev| %.5f (tol %.4f; 3-dp rounding half-width %.4f)\n", dev, TOL, ROUND))
  if (dev > TOL) ok <- FALSE
  if (nm == "PU" && dev > ROUND) { cat("     PU does not reproduce within rounding\n"); ok <- FALSE }
}

# ---- Route A2: controls against the whole PU profile
PUPUB <- c(pub$PU$itc, pub$PU$a, pub$PU$mean)
prof <- function(cc) { X <- num(cc); c(itc(X), alpha(X), mean(rowMeans(X))) }
dev <- function(v) max(abs(v - PUPUB))
cat("\nRoute A2 -- controls vs published PU profile (itc 0.876 0.870 0.860 0.838 0.874, alpha 0.912, mean 4.085)\n")
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(PU)
pd <- sapply(P, function(p) dev(prof(p)))
ident <- sapply(P, function(p) identical(p, PU))
cat(sprintf("orderings of PU1..PU5 tried: %d; within tol %.4f: %s; within rounding %.4f: %s\n", length(P), TOL,
            paste(sapply(P[pd <= TOL], paste, collapse = ","), collapse = " | "), ROUND,
            paste(sapply(P[pd <= ROUND], paste, collapse = ","), collapse = " | ")))
o <- order(pd)
for (i in o[1:5]) cat(sprintf("  [%s] max|dev| %.5f%s\n", paste(P[[i]], collapse = ","), pd[i], if (ident[i]) "  (published order)" else ""))
if (!ident[which.min(pd)] || sum(pd <= TOL) != 1) ok <- FALSE
nearest_perm <- min(pd[!ident])
cat(sprintf("THIN PAIR PU1<->PU5: identity %.5f vs swap %.5f; swap margin over tol %.5f, over rounding %.5f (%.1fx half-width)\n",
            min(pd[ident]), nearest_perm, nearest_perm - TOL, nearest_perm - ROUND, nearest_perm / ROUND))

j <- match("PU1", hdr)
w <- hdr[(j + 1):(j + 5)]
v <- prof(w)
cat(sprintf("shift_right [%s] max|dev| %.4f%s\n", paste(w, collapse = ","), dev(v), if (dev(v) <= TOL) "  <- REPRODUCES" else ""))
if (dev(v) <= TOL) ok <- FALSE
wd <- sapply(1:(length(likert) - 4), function(s) { cc <- likert[s:(s + 4)]; if (identical(cc, PU)) NA else dev(prof(cc)) })
cat(sprintf("other contiguous 5-column windows: %d; nearest max|dev| %.4f [%s]; reproducing: %d\n",
            sum(!is.na(wd)), min(wd, na.rm = TRUE), paste(likert[which.min(wd):(which.min(wd) + 4)], collapse = ","),
            sum(wd <= TOL, na.rm = TRUE)))
if (any(wd <= TOL, na.rm = TRUE)) ok <- FALSE
foreign <- setdiff(likert, PU)
best <- Inf; bestlab <- ""; und <- character(0)
for (f in foreign) for (k in 1:5) {
  ww <- PU; ww[k] <- f; dv <- dev(prof(ww))
  if (dv < best) { best <- dv; bestlab <- sprintf("%s<-%s", PU[k], f) }
  if (dv <= TOL) und <- c(und, sprintf("%s<-%s", PU[k], f))
}
cat(sprintf("single foreign-column replacements tried: %d; nearest %s max|dev| %.4f; reproducing: %s\n",
            5 * length(foreign), bestlab, best, if (length(und)) paste(und, collapse = ", ") else "none"))
if (length(und)) ok <- FALSE

# ---- Route A3: loading rank order (corroborates the thin pair)
XP <- num(PU)
L <- factanal(XP, 1)$loadings[, 1]
PUBL <- c(0.87, 0.86, 0.80, 0.77, 0.84)
cat(sprintf("\nRoute A3 -- one-factor ML loadings %s vs Table 3 LISREL %s\n",
            paste(sprintf("%.4f", L), collapse = "/"), paste(sprintf("%.2f", PUBL), collapse = "/")))
cat(sprintf("  rank order observed %s | published %s | PU1-PU5 gap observed %.4f, published %.2f\n",
            paste(PU[order(-L)], collapse = ">"), paste(PU[order(-PUBL)], collapse = ">"), L[1] - L[5], PUBL[1] - PUBL[5]))
cat(sprintf("  CR %.4f (pub 0.9124), AVE %.4f (pub 0.6759)  [not scored]\n", sum(L)^2 / (sum(L)^2 + sum(1 - L^2)), mean(L^2)))
if (!identical(order(-L), order(-PUBL))) ok <- FALSE

# ---- Route C: live table equals the xlsx PU columns
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in PU) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-4s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}
if (nrow(d) != 505) { cat("live rows", nrow(d), "!= 505\n"); ok <- FALSE }

# ---- Route D (not scored)
cat("\nWithin-PU r / identical answers (of 101)  [not scored]:\n")
for (a in 1:4) for (b in (a + 1):5)
  cat(sprintf("  %s~%s r %.3f  identical %3d\n", PU[a], PU[b], cor(XP[, a], XP[, b]), sum(XP[, a] == XP[, b])))
cat("  (PU1/PU2 are the near-paraphrase pair 'helps me [quickly analyze|understand] my social status'.)\n")
cat("NOT ESTABLISHED: that Table 3's PU1..PU5 numbering follows S2's print order (upstream labelling).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
