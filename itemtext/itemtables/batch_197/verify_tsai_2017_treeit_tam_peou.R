# verify_tsai_2017_treeit_tam_peou.R -- Step 5b mapping check (batch_197).
# Built from references/verify_template.R, following verify_tsai_2017_treeit_tam_bi.R (batch_196).
#
# CLAIM: live item codes PEOU1..PEOU6 are the S3 File (.xlsx) column names (data/tsai_2017_treeit.py
# melts by column name, no rename, resp kept 1-5), and PEOUk is the (5+k)-th statement of
# "Section Two: TAM Questions" in the study's S2 File (Appendix 2, TreeIt Technology Acceptance
# Model Questionnaire, pone.0180102.s002, p.2 rows 2-7):
#   PEOU1 "I find the TreeIt system to be easy to use."
#   PEOU2 "I find the TreeIt system easy to learn."
#   PEOU3 "My interaction with the TreeIt system is clear and understandable."
#   PEOU4 "Compared to other SNSs, the TreeIt system has a clearer and easier operating interface."
#   PEOU5 "Compared to other SNSs, the TreeIt system provides a more humanized operating interface."
#   PEOU6 "Overall, I think the TreeIt system is easy to use."
# S2 prints no construct headers and no item numbers. Paper Table 3 lists "Perceived Ease of use"
# items PEOU1..PEOU6 (between PU1-5 and nothing else of TAM; BI is numbered BI12-15, i.e. positions
# 12-15, which fixes PEOU at positions 6-11 of 15) and gives each its own item-total r.
#
# ROUTES:
#   A. Route 1 (per-item statistics): Table 3 prints a distinct item-total r per PEOU item
#      (0.860 / 0.842 / 0.825 / 0.780 / 0.756 / 0.873) plus alpha 0.905; Table 4 the mean 4.170.
#      Uncorrected r of each xlsx PEOU column with the PEOU sum must reproduce them IN ORDER.
#   A2. Controls, each scored against the WHOLE PEOU profile (6 item-total r + alpha + mean):
#      all 719 non-identity orderings of PEOU1..PEOU6; the 6-column window shifted one left
#      [PU5,PEOU1..5] and right [PEOU2..6,BI1]; every other contiguous 6-column Likert window;
#      every single foreign-column replacement.
#   B. Block size / layout: S2 has 15 TAM statements; xlsx columns 6-20 are PU1-5, PEOU1-6, BI1-4.
#   C. Live table == the xlsx PEOU columns (per-item response-level counts 1..5).
#
# NOT ESTABLISHED by any route: that Table 3's PEOU1..PEOU6 / the xlsx PEOU1..PEOU6 order follows
# S2's print order (an upstream labelling fact the data cannot test; consistent with 5 + 6 + 4 = 15,
# BI12-15, and the S3 PU/PEOU/BI column layout). Nothing here speaks to the wording itself.

suppressMessages(library(irw))
TABLE <- "tsai_2017_treeit_tam_peou"
SI <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"
CACHE <- "itemtext/.cache/tsai_2017_treeit_tam_peou/s003.xlsx"  # fallback if offline
PE <- paste0("PEOU", 1:6)
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
cat("  S2 prints 15 TAM statements; Table 3 labels PU1-5, PEOU1-6, BI12-15 (PEOU = positions 6-11)\n")
if (!identical(hdr[6:20], c(paste0("PU", 1:5), PE, paste0("BI", 1:4)))) ok <- FALSE

# ---- Route A
PUB_ITC <- c(0.860, 0.842, 0.825, 0.780, 0.756, 0.873); PUB_A <- 0.905; PUB_M <- 4.170
X <- num(PE); a <- alpha(X); r <- itc(X); mu <- mean(rowMeans(X))
cat("\nRoute A -- paper Table 3 (alpha, per-item item-total r) and Table 4 (construct mean)\n")
cat(sprintf("PEOU alpha published %.3f observed %.4f | mean published %.3f observed %.4f\n", PUB_A, a, PUB_M, mu))
for (i in seq_along(PE))
  cat(sprintf("     xlsx %-6s vs Table 3 %-6s (S2 statement %2d) item-total published %.3f observed %.4f\n",
              PE[i], PE[i], 5 + i, PUB_ITC[i], r[i]))
d0 <- max(abs(a - PUB_A), abs(r - PUB_ITC), abs(mu - PUB_M))
cat(sprintf("     max|dev| %.4f (tol %.4f)\n", d0, TOL))
if (d0 > TOL) ok <- FALSE
cat(sprintf("     smallest gap between published item-total r values: %.3f\n", min(diff(sort(PUB_ITC)))))

# ---- Route A2: controls against the whole PEOU profile
PUB <- c(PUB_ITC, PUB_A, PUB_M)
prof <- function(cc) { X <- num(cc); c(itc(X), alpha(X), mean(rowMeans(X))) }
dev <- function(v) max(abs(v - PUB))
cat("\nRoute A2 -- controls vs published PEOU profile\n")
perms <- function(v) if (length(v) <= 1) list(v) else do.call(c, lapply(seq_along(v), function(i) lapply(perms(v[-i]), function(p) c(v[i], p))))
P <- perms(PE)
# item-total r and alpha/mean of a permutation are the same numbers re-ordered, so compute once
pd <- sapply(P, function(p) max(abs(r[match(p, PE)] - PUB_ITC), abs(a - PUB_A), abs(mu - PUB_M)))
ident <- sapply(P, function(p) identical(p, PE))
cat(sprintf("orderings of PEOU1..PEOU6 tried: %d; reproducing: %s\n", length(P),
            paste(sapply(P[pd <= TOL], paste, collapse = ","), collapse = " | ")))
o <- order(pd)
for (i in o[1:4]) cat(sprintf("  [%s] max|dev| %.4f%s\n", paste(P[[i]], collapse = ","), pd[i], if (ident[i]) "  (published order)" else ""))
if (!ident[which.min(pd)] || sum(pd <= TOL) != 1) ok <- FALSE
nearest_perm <- min(pd[!ident])

j <- match("PEOU1", hdr)
wins <- list(shift_left = hdr[(j - 1):(j + 4)], shift_right = hdr[(j + 1):(j + 6)])
for (w in names(wins)) {
  v <- prof(wins[[w]])
  cat(sprintf("%-11s [%s] itc %s alpha %.4f mean %.4f | max|dev| %.4f%s\n", w, paste(wins[[w]], collapse = ","),
              paste(sprintf("%.4f", v[1:6]), collapse = " "), v[7], v[8], dev(v), if (dev(v) <= TOL) "  <- REPRODUCES" else ""))
  if (dev(v) <= TOL) ok <- FALSE
}
wd <- sapply(1:(length(likert) - 5), function(s) { cc <- likert[s:(s + 5)]; if (identical(cc, PE)) NA else dev(prof(cc)) })
cat(sprintf("other contiguous 6-column windows: %d; nearest max|dev| %.4f [%s]; reproducing: %d\n",
            sum(!is.na(wd)), min(wd, na.rm = TRUE), paste(likert[which.min(wd):(which.min(wd) + 5)], collapse = ","),
            sum(wd <= TOL, na.rm = TRUE)))
if (any(wd <= TOL, na.rm = TRUE)) ok <- FALSE
foreign <- setdiff(likert, PE)
best <- Inf; bestlab <- ""; und <- character(0)
for (f in foreign) for (k in 1:6) {
  w <- PE; w[k] <- f; dv <- dev(prof(w))
  if (dv < best) { best <- dv; bestlab <- sprintf("%s<-%s", PE[k], f) }
  if (dv <= TOL) und <- c(und, sprintf("%s<-%s", PE[k], f))
}
cat(sprintf("single foreign-column replacements tried: %d; nearest %s max|dev| %.4f; reproducing: %s\n",
            6 * length(foreign), bestlab, best, if (length(und)) paste(und, collapse = ", ") else "none"))
if (length(und)) ok <- FALSE
cat(sprintf("nearest rejected control overall: %.4f (tol %.4f)\n", min(nearest_perm, best, min(wd, na.rm = TRUE)), TOL))

# ---- Route C: live table equals the xlsx PEOU columns
d <- irw::irw_fetch(TABLE)
cat("\nRoute C -- response-level counts 1..5 per item, xlsx vs live\n")
for (it in PE) {
  x <- table(factor(as.numeric(dat[[it]]), levels = 1:5))
  l <- table(factor(d$resp[d$item == it], levels = 1:5))
  cat(sprintf("%-6s xlsx %s | live %s | mean %.3f\n", it, paste(x, collapse = "/"), paste(l, collapse = "/"),
              mean(as.numeric(dat[[it]]), na.rm = TRUE)))
  if (!all(x == l)) ok <- FALSE
}
cat(sprintf("live rows %d, ids %d\n", nrow(d), length(unique(d$id))))
if (nrow(d) != 606) { cat("live rows", nrow(d), "!= 606\n"); ok <- FALSE }

cat("NOT ESTABLISHED: that the PEOU1..PEOU6 numbering (Table 3 and xlsx) follows S2's print order,\n",
    "positions 6-11 (upstream labelling; consistent with 5 PU + 6 PEOU + 4 BI = 15 statements,\n",
    "Table 3's BI12-15, and the xlsx PU/PEOU/BI layout).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
