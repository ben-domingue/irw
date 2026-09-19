# verify_torices_2025_bapq.R  (batch_189)
#
# Claim under test: live item BAPQ_nn carries the CANONICAL BAPQ item number nn
# (Hurley et al. 2007 numbering, as printed 1..36 in Sasson et al. 2013 Table 2),
# so item_text for BAPQ_nn is canonical BAPQ item nn; and resp 1..6 carry the
# deposit codebook's labels (sheet "Codigos": 1 Muy raramente .. 6 Muy a menudo).
#
# Code derivation (data/torices_2025_ltcansiTEA.py): POSITIONAL --
# f"BAPQ_{i+1:02d}" over enumerate([c for c in columns if c.startswith('BAPQ')]).
# The deposit columns carry no item wording (bare headers BAPQ1..BAPQ36), so the
# name->wording tie rests on the instrument's numbering and is tested here:
#
#   P1  Header diff: the deposit's BAPQ-prefixed columns, in sheet order, are
#       exactly BAPQ1..BAPQ36, so position i -> BAPQ_{i:02d} preserves the number.
#   P2  Live per-item x per-level counts equal the deposit's for all 36 x 6 cells
#       (the positional rename reproduces the live table; resp is stored as the
#       deposit's own integer codes, no recode, so the codebook labels apply).
#   P3  Keying polarity (route 6): the canonical reverse-keyed set is
#       {1,3,7,9,12,15,16,19,21,23,25,28,30,34,36}. On raw data every reverse item
#       should correlate on average POSITIVELY with the other reverse items and
#       NEGATIVELY with the forward items, and every forward item the opposite.
#       Must hold for 36/36.
#   P4  Subscale block structure (route 5): after reversing the 15 items, each item's
#       mean r with its own canonical subscale (Aloof/Pragmatic language/Rigid)
#       should exceed its mean r with the other two. Chance = 12/36. Threshold 24/36.
#       Underpowered at N=108 and the BAPQ's PL items cross-load onto Aloof
#       (Sasson 2013 reports items 7, 10, 11, 21 off-subscale in self-ratings), so a
#       miss there is expected, not evidence of a bad mapping.
#
# NOT established: order WITHIN a polarity x subscale cell -- e.g. aloof-reverse
# {1,9,12,16,23,25,28,36} or rigid-forward {6,8,13,22,24,26,33,35}. No per-item
# statistics for this sample were located (paper not found), so a permutation
# inside a cell would pass P3/P4. -> PARTIAL.

suppressMessages({ library(irw); library(readxl) })

TABLE <- "torices_2025_bapq"
URL   <- "https://ndownloader.figshare.com/files/51612044"   # figshare 28188872 v1, CC BY 4.0
f <- tempfile(fileext = ".xlsx")
utils::download.file(URL, f, quiet = TRUE, mode = "wb")
dep <- as.data.frame(readxl::read_excel(f, sheet = "Respuestas de formulario 1"))
ok <- logical(0)

## P1 --------------------------------------------------------------------------
bcols <- grep("^BAPQ", names(dep), value = TRUE)
p1 <- identical(bcols, paste0("BAPQ", 1:36))
cat(sprintf("P1 deposit BAPQ columns in order: %s ... %s (n=%d); == BAPQ1..BAPQ36: %s\n\n",
            paste(head(bcols, 3), collapse = ","), paste(tail(bcols, 2), collapse = ","),
            length(bcols), ifelse(p1, "PASS", "FAIL")))
ok <- c(ok, p1)

X <- as.data.frame(lapply(dep[, bcols], as.numeric))
names(X) <- sprintf("BAPQ_%02d", 1:36)
cat(sprintf("Deposit rows: %d\n", nrow(X)))

## P2 --------------------------------------------------------------------------
live <- irw::irw_fetch(TABLE)
cat(sprintf("Live rows: %d, ids: %d\n", nrow(live), length(unique(live$id))))
lt <- table(factor(live$item, levels = names(X)), factor(live$resp, levels = 1:6))
dt <- t(sapply(names(X), function(v) table(factor(X[[v]], levels = 1:6))))
agree <- sum(lt == dt)
cat("Per-item counts, levels 1..6 (live | deposit), first 5 and BAPQ_28:\n")
for (v in c(names(X)[1:5], "BAPQ_28"))
  cat(sprintf("  %-8s %s | %s\n", v, paste(lt[v, ], collapse = "/"), paste(dt[v, ], collapse = "/")))
p2 <- agree == 216
cat(sprintf("P2 cells agreeing: %d / 216 -> %s\n\n", agree, ifelse(p2, "PASS", "FAIL")))
ok <- c(ok, p2)

## P3 --------------------------------------------------------------------------
REV <- c(1,3,7,9,12,15,16,19,21,23,25,28,30,34,36)
C <- stats::cor(X, use = "pairwise.complete.obs")
p3n <- 0
cat("P3 item class | mean r with forward items | mean r with reverse items\n")
for (i in 1:36) {
  fw <- setdiff(setdiff(1:36, REV), i); rv <- setdiff(REV, i)
  mf <- mean(C[i, fw]); mr <- mean(C[i, rv])
  good <- if (i %in% REV) (mr > 0 && mf < 0) else (mf > 0 && mr < 0)
  p3n <- p3n + good
  cat(sprintf("  BAPQ_%02d %s  %+.3f  %+.3f  %s\n", i, ifelse(i %in% REV, "R", "F"), mf, mr,
              ifelse(good, "ok", "MISS")))
}
p3 <- p3n == 36
cat(sprintf("P3 polarity consistent with canonical key: %d / 36 -> %s\n\n", p3n, ifelse(p3, "PASS", "FAIL")))
ok <- c(ok, p3)

## P4 --------------------------------------------------------------------------
Y <- X; for (r in REV) Y[[r]] <- 7 - Y[[r]]
CY <- stats::cor(Y, use = "pairwise.complete.obs")
SUB <- list(Aloof = c(1,5,9,12,16,18,23,25,27,28,31,36),
            PragLang = c(2,4,7,10,11,14,17,20,21,29,32,34),
            Rigid = c(3,6,8,13,15,19,22,24,26,30,33,35))
p4n <- 0; miss <- character(0)
for (i in 1:36) {
  own <- names(SUB)[sapply(SUB, function(s) i %in% s)]
  m <- sapply(SUB, function(s) mean(CY[i, setdiff(s, i)]))
  if (names(which.max(m)) == own) p4n <- p4n + 1 else
    miss <- c(miss, sprintf("%d(%s->%s)", i, own, names(which.max(m))))
}
p4 <- p4n >= 24
cat(sprintf("P4 items closest to own subscale: %d / 36 (chance 12, threshold 24) -> %s\n",
            p4n, ifelse(p4, "PASS", "FAIL")))
cat("   misses:", paste(miss, collapse = " "), "\n\n")
ok <- c(ok, p4)

## Response-data observation (reported, not a pass/fail criterion) --------------
n6 <- colSums(X == 6, na.rm = TRUE)
cat(sprintf("Note: resp=6 ('Muy a menudo') occurs %d times on BAPQ_01 and %d times across BAPQ_02..BAPQ_36.\n",
            n6[1], sum(n6[-1])))
cat("Not established: order within a polarity x subscale cell (no per-item statistics for this sample).\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
