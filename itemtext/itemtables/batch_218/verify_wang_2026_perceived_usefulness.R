# verify_wang_2026_perceived_usefulness.R
#
# Claim under test: each IRW item code PU1/PU2/PU3 carries the wording shipped
# for it, and sits on the identically-named column of Wang & Zou's S2 Appendix.
# Three links, all re-derived here from the source files and the live table:
#
#   LINK 1  code -> wording. The study's S1 Appendix questionnaire prints every
#           item with its code as a literal prefix ("PU1-Using DG technology
#           enables me to accomplish tasks more quickly."). Step 5b exemption 2.
#   LINK 2  code -> live column. Per-item counts of resp 1..5 in the live IRW
#           table vs the same-named S2 Appendix column. Route 9. The three count
#           vectors are pairwise distinct, so a permutation would break it.
#   LINK 3  corroboration from the paper. Table 2 publishes a per-item VIF under
#           the DATA's codes; recomputed from the deposit columns it reproduces
#           exactly, and the loading rank order matches.
#
# Deliberately NOT evidence: item counts / set membership (validate_items.R).

suppressMessages(library(irw))

TABLE <- "wang_2026_perceived_usefulness"
S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s001"
S2 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0346229.s002"
UA <- "Mozilla/5.0"   # no email is sent to any outside service

SHIPPED <- c(
  PU1 = "Using DG technology enables me to accomplish tasks more quickly.",
  PU2 = "Using DG technology enhances my effectiveness.",
  PU3 = "Using DG technology increases my productivity.")

# Paper Table 2 (image asset .t002), rows PU1/PU2/PU3.
PUB_LOADING <- c(PU1 = 0.849, PU2 = 0.822, PU3 = 0.802)
PUB_VIF     <- c(PU1 = 1.626, PU2 = 1.554, PU3 = 1.500)

tmp <- file.path(tempdir(), c("s001.docx", "s002.xlsx"))
ok <- TRUE
try({
  download.file(S1, tmp[1], quiet = TRUE, mode = "wb", headers = c("User-Agent" = UA))
  download.file(S2, tmp[2], quiet = TRUE, mode = "wb", headers = c("User-Agent" = UA))
}, silent = TRUE)
if (!all(file.exists(tmp))) { cat("could not download the supplements\nVERDICT: FAIL\n"); quit(status = 0) }

cat("sha256 s001.docx:", as.character(tools::sha256sum(tmp[1])), "\n")
cat("sha256 s002.xlsx:", as.character(tools::sha256sum(tmp[2])), "\n\n")

## ---- LINK 1: the appendix prints the data's own code as a prefix -------------
xmlf <- file.path(tempdir(), "document.xml")
unzip(tmp[1], files = "word/document.xml", exdir = tempdir(), overwrite = TRUE)
raw <- paste(readLines(file.path(tempdir(), "word", "document.xml"),
                       warn = FALSE, encoding = "UTF-8"), collapse = "")
# paragraph-preserving flatten of the WordprocessingML
raw <- gsub("</w:p>", "\n", raw)
txt <- gsub("<[^>]*>", "", raw)
txt <- unlist(strsplit(txt, "\n"))
txt <- trimws(txt); txt <- unique(txt[nzchar(txt)])

cat("LINK 1 -- S1 Appendix lines carrying the data's item codes as a prefix\n")
link1 <- logical(3)
for (i in 1:3) {
  code <- names(SHIPPED)[i]
  hit  <- grep(paste0("^", code, "[-–]"), txt, value = TRUE)
  hit  <- if (length(hit)) hit[1] else NA_character_
  strip <- if (is.na(hit)) NA_character_ else sub(paste0("^", code, "[-–]"), "", hit)
  link1[i] <- !is.na(strip) && identical(strip, unname(SHIPPED[i]))
  cat(sprintf("  appendix: %s\n  shipped : %s-%s   -> %s\n",
              ifelse(is.na(hit), "(not found)", hit), code, SHIPPED[i],
              ifelse(link1[i], "MATCH", "MISMATCH")))
}
cat(sprintf("  link 1: %d/3 verbatim\n\n", sum(link1)))

## ---- LINK 2: live per-item resp counts vs the same-named deposit column ------
dep <- as.data.frame(readxl::read_excel(tmp[2]))
live <- irw::irw_fetch(TABLE)
codes <- names(SHIPPED)
cnt <- function(v) as.integer(table(factor(as.numeric(v), levels = 1:5)))
Ldep  <- sapply(codes, function(c) cnt(dep[[c]]))
Llive <- sapply(codes, function(c) cnt(live$resp[live$item == c]))

cat("LINK 2 -- counts of resp 1..5, deposit column vs live item\n")
for (c in codes)
  cat(sprintf("  %-4s deposit %-22s live %-22s %s\n", c,
              paste(Ldep[, c], collapse = ","), paste(Llive[, c], collapse = ","),
              ifelse(identical(Ldep[, c], Llive[, c]), "EQUAL", "DIFFERS")))

eq <- outer(codes, codes, Vectorize(function(a, b) identical(Ldep[, a], Llive[, b])))
dimnames(eq) <- list(paste0("dep:", codes), paste0("live:", codes))
cat("\n  full 3x3 equality matrix (a permutation would move the TRUEs off the diagonal):\n")
print(eq)
diag_only <- all(diag(eq)) && sum(eq) == 3L
cat(sprintf("  %d of 9 comparisons equal; diagonal-only: %s\n\n", sum(eq), diag_only))

cat("  per-item means (live vs deposit):\n")
for (c in codes)
  cat(sprintf("    %-4s live %.6f   deposit %.6f\n", c,
              mean(as.numeric(live$resp[live$item == c])),
              mean(as.numeric(dep[[c]]), na.rm = TRUE)))
cat("\n")

## ---- LINK 3: paper Table 2 per-item VIF and loadings, recomputed -------------
X <- scale(as.matrix(dep[, codes]))
w <- rep(1, 3) / sqrt(3)
for (k in 1:500) { f <- as.numeric(X %*% w); f <- f / sd(f)
                   w <- apply(X, 2, function(x) cor(x, f)); w <- w / sqrt(sum(w^2)) }
f <- as.numeric(X %*% w); f <- f / sd(f)
load <- apply(X, 2, function(x) cor(x, f))
vif <- sapply(seq_along(codes), function(j)
  1 / (1 - summary(lm(X[, j] ~ X[, -j]))$r.squared))
names(vif) <- codes

cat("LINK 3 -- paper Table 2 (published under the DATA's codes) vs recomputed\n")
cat(sprintf("  %-4s  VIF pub %.3f  VIF obs %.3f   |  loading pub %.3f  obs %.3f\n",
            codes, PUB_VIF[codes], vif[codes], PUB_LOADING[codes], load[codes]))
vif_ok <- max(abs(vif[codes] - PUB_VIF[codes])) < 0.002
rank_ok <- identical(rank(-load[codes]), rank(-PUB_LOADING[codes]))
cat(sprintf("  max |VIF pub - obs| = %.4f ; loading rank order matches: %s\n\n",
            max(abs(vif[codes] - PUB_VIF[codes])), rank_ok))

## ---- what this does NOT establish -------------------------------------------
cat("Does NOT establish: (a) that the authors' own spreadsheet labelling is\n",
    "correct -- a mislabel inside the deposit satisfies every link above;\n",
    "(b) anything about the Chinese wording respondents actually read -- the\n",
    "administration was Chinese and the shipped English is the recoverability\n",
    "fallback; (c) note that Table 2's CA/CR/AVE column for the PU row\n",
    "(0.874/0.909/0.665) reproduces the deposit's BI block, not its PU block\n",
    "(PU recomputes to 0.765/0.865/0.680) -- a bookkeeping slip in the paper's\n",
    "construct-level column that does not touch the per-item VIF/loading rows\n",
    "used here.\n", sep = "")

pass <- sum(link1) == 3L && diag_only && vif_ok && rank_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
