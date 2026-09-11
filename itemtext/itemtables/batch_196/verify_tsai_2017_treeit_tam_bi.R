# verify_tsai_2017_treeit_tam_bi.R -- Step 5b mapping check (batch_196).
# Built from references/verify_template.R.
#
# CLAIM: live item codes BI1..BI4 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and BIk is the (11+k)-th statement of
# "Section Two: TAM Questions" in the study's S2 File (Appendix 2, TreeIt Technology Acceptance
# Model Questionnaire, pone.0180102.s002, the last four rows of the table on p.2):
#   BI1 "To inspect my social status in the future, I am willing to continue using the TreeIt system."
#   BI2 "I plan to use the TreeIt system to inspect my social status."
#   BI3 "I will recommend the TreeIt system to my family and friends."
#   BI4 "Overall, I have a high intention to use the TreeIt system."
# S2 prints no construct headers and no item numbers. Paper Table 3 labels the Behavioral
# Intention items BI12, BI13, BI14, BI15 -- questionnaire positions 12-15, i.e. after the 5 PU and
# 6 PEOU statements (5 + 6 + 4 = 15 statements in S2) -- and gives each its own item-total r.
#
# ROUTES:
#   A. Route 1 (per-item statistics): Table 3 prints a distinct item-total r per BI item
#      (0.916 / 0.912 / 0.896 / 0.886) plus the BI alpha 0.923; Table 4 the BI mean 4.020.
#      Uncorrected r of each xlsx BI column with the BI sum must reproduce them IN ORDER.
#      The same statistic definitions are checked on PU and PEOU (sanity: same table, same method).
#   A2. Controls, each scored against the WHOLE BI profile (4 item-total r + alpha + mean):
#      all 23 non-identity orderings of BI1..BI4 against rows BI12..BI15; the 4-column window
#      shifted one left [PEOU6,BI1,BI2,BI3] and right [BI2,BI3,BI4,H1-1]; every other contiguous
#      4-column Likert window in the file; every single foreign-column replacement (61 x 4).
#   B. Block size: S2 has 15 TAM statements; Table 3 numbers BI as 12-15 (4 items);
#      xlsx has BI1..BI4 (4 columns) after PU1-5 and PEOU1-6.
#   C. Live table == the xlsx BI columns (per-item response-level counts 1..5).
#   D. (not scored) identical-answer counts; Table 4 S.D. and latent r^2; ML CR/AVE/loadings.
#
# NOT ESTABLISHED by any route: that Table 3's numbering BI12..BI15 follows S2's print order
# (an upstream labelling fact the data cannot test; it is consistent with 5 + 6 + 4 = 15 and with
# the S3 column layout PU/PEOU/BI). Nothing here speaks to the wording or to the administered
# (Chinese) language; the anchors' numeric direction rests on the article Methods sentence.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_tam_bi"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_tam_bi/s003.xlsx"  # fallback if offline
BI <- paste0("BI", 1:4)
TOL <- 0.0015

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
cat("  S2 prints 15 TAM statements; Table 3 labels PU1-5, PEOU1-6, BI12-15 (4 BI items)\n")
if (!identical(hdr[17:20], BI) || !identical(hdr[6:16], c(paste0("PU", 1:5), paste0("PEOU", 1:6)))) ok <- FALSE

# ---- Route A
pub <- list(
  BI   = list(cc = BI, a = 0.923, itc = c(0.916, 0.912, 0.896, 0.886), mean = 4.020),
  PU   = list(cc = paste0("PU", 1:5), a = 0.912, itc = c(0.876, 0.870, 0.860, 0.838, 0.874), mean = 4.085),
  PEOU = list(cc = paste0("PEOU", 1:6), a = 0.905, itc = c(0.860, 0.842, 0.825, 0.780, 0.756, 0.873), mean = 4.170))
cat("\nRoute A -- paper Table 3 (alpha, per-item item-total r) and Table 4 (construct mean)\n")
for (nm in names(pub)) {
  p <- pub[[nm]]; X <- num(p$cc)
  a <- alpha(X); r <- itc(X); mu <- mean(rowMeans(X))
  cat(sprintf("%-4s alpha published %.3f observed %.4f | mean published %.3f observed %.4f\n", nm, p$a, a, p$mean, mu))
  lab <- if (nm == "BI") paste0("BI", 12:15) else p$cc
  for (i in seq_along(p$cc))
    cat(sprintf("     xlsx %-6s vs Table 3 %-6s item-total published %.3f observed %.4f\n", p$cc[i], lab[i], p$itc[i], r[i]))
  dev <- max(abs(a - p$a), abs(r - p$itc), abs(mu - p$mean))
  cat(sprintf("     max|dev| %.4f (tol %.4f)\n", dev, TOL))
  if (dev > TOL) ok <- FALSE
}

# ---- Route A2: controls against the whole BI profile
BIPUB <- c(pub$BI$itc, pub$BI$a, pub$BI$mean)
prof <- function(cc) { X <- num(cc); c(itc(X), alpha(X), mean(rowMeans(X))) }
hits <- function(v) all(abs(v - BIPUB) <= TOL)
dev <- function(v) max(abs(v - BIPUB))
cat("\nRoute A2 -- controls vs published BI profile (itc 0.916 0.912 0.896 0.886, alpha 0.923, mean 4.020)\n")
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(BI)
pd <- sapply(P, function(p) dev(prof(p)))
ident <- sapply(P, function(p) identical(p, BI))
cat(sprintf("orderings of BI1..BI4 tried: %d; reproducing: %s\n", length(P),
            paste(sapply(P[pd <= TOL], paste, collapse = ","), collapse = " | ")))
o <- order(pd)
for (i in o[1:4]) cat(sprintf("  [%s] max|dev| %.4f%s\n", paste(P[[i]], collapse = ","), pd[i], if (ident[i]) "  (published order)" else ""))
if (!ident[which.min(pd)] || sum(pd <= TOL) != 1) ok <- FALSE
nearest_perm <- min(pd[!ident])

j <- match("BI1", hdr)
wins <- list(shift_left = hdr[(j - 1):(j + 2)], shift_right = hdr[(j + 1):(j + 4)])
for (w in names(wins)) {
  v <- prof(wins[[w]])
  cat(sprintf("%-11s [%s] itc %s alpha %.4f mean %.4f | max|dev| %.4f%s\n", w, paste(wins[[w]], collapse = ","),
              paste(sprintf("%.4f", v[1:4]), collapse = " "), v[5], v[6], dev(v), if (hits(v)) "  <- REPRODUCES" else ""))
  if (hits(v)) ok <- FALSE
}
wd <- sapply(1:(length(likert) - 3), function(s) { cc <- likert[s:(s + 3)]; if (identical(cc, BI)) NA else dev(prof(cc)) })
cat(sprintf("other contiguous 4-column windows: %d; nearest max|dev| %.4f [%s]; reproducing: %d\n",
            sum(!is.na(wd)), min(wd, na.rm = TRUE), paste(likert[which.min(wd):(which.min(wd) + 3)], collapse = ","),
            sum(wd <= TOL, na.rm = TRUE)))
if (any(wd <= TOL, na.rm = TRUE)) ok <- FALSE
foreign <- setdiff(likert, BI)
best <- Inf; bestlab <- ""; und <- character(0)
for (f in foreign) for (k in 1:4) {
  w <- BI; w[k] <- f; dv <- dev(prof(w))
  if (dv < best) { best <- dv; bestlab <- sprintf("%s<-%s", BI[k], f) }
  if (dv <= TOL) und <- c(und, sprintf("%s<-%s", BI[k], f))
}
cat(sprintf("single foreign-column replacements tried: %d; nearest %s max|dev| %.4f; reproducing: %s\n",
            4 * length(foreign), bestlab, best, if (length(und)) paste(und, collapse = ", ") else "none"))
if (length(und)) ok <- FALSE
cat(sprintf("nearest rejected control overall: %.4f (tol %.4f)\n", min(nearest_perm, best, min(wd, na.rm = TRUE)), TOL))

# ---- Route C: live table equals the xlsx BI columns
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in BI) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-4s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}
if (nrow(d) != 404) { cat("live rows", nrow(d), "!= 404\n"); ok <- FALSE }

# ---- Route D (not scored)
XB <- num(BI); A <- num(likert)
cat("\nWithin-BI identical answers (of 101) / r  [not scored]:\n")
for (a in 1:3) for (b in (a + 1):4)
  cat(sprintf("  %s~%s %3d  r %.3f\n", BI[a], BI[b], sum(XB[, a] == XB[, b]), cor(XB[, a], XB[, b])))
cat("Most-identical columns outside BI [not scored]:\n")
for (it in BI) {
  s <- sapply(foreign, function(o) sum(A[, it] == A[, o])); o <- order(-s)[1:3]
  cat(sprintf("  %s: %s\n", it, paste(sprintf("%s %d", names(s)[o], s[o]), collapse = "; ")))
}
cat(sprintf("[not scored] Table 4 BI S.D. 0.771 vs composite SD %.3f; Table 4 lower triangle is latent r^2\n",
            sd(rowMeans(XB))),
    sprintf("  (BI-PU 0.6889, BI-PEOU 0.5476) vs composite r^2 %.4f / %.4f -- LISREL values, not reproduced, not used.\n",
            cor(rowMeans(XB), rowMeans(num(pub$PU$cc)))^2, cor(rowMeans(XB), rowMeans(num(pub$PEOU$cc)))^2), sep = "")
f <- factanal(XB, 1); L <- f$loadings[, 1]
cat(sprintf("[not scored] one-factor ML loadings %s (Table 3 LISREL 0.89/0.88/0.85/0.85); CR %.4f (pub 0.9241), AVE %.4f (pub 0.7534)\n",
            paste(sprintf("%.3f", L), collapse = "/"), sum(L)^2 / (sum(L)^2 + sum(1 - L^2)), mean(L^2)))
cat("NOT ESTABLISHED: that Table 3's BI12..BI15 numbering follows S2's print order (upstream labelling;\n",
    "consistent with 5 PU + 6 PEOU + 4 BI = 15 statements and with the xlsx PU/PEOU/BI layout).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
