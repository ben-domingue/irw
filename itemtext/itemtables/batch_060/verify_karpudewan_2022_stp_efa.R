# verify_karpudewan_2022_stp_efa.R
#
# CLAIM UNDER TEST
#   S3 Appendix of Karpudewan et al. (2022, PLoS ONE 17(5):e0268509) prints the
#   retained EFA items under the FINAL construct names -- PD (perceived
#   difficulties) and PE (self-efficacy) -- while the EFA response file (S2
#   Dataset, .s005) and therefore the IRW table use the ORIGINAL names CH and
#   PSE, plus STP and KN. The extraction claims the numbering is preserved
#   across that rename: PD_k -> CH_k, PE_k -> PSE_k, STP_k -> STP_k, KN_k -> KN_k.
#   Nothing in the appendix states that; it is the thing that could be wrong.
#
# THE FALSIFIABLE PREDICTION
#   The appendix prints the rotated factor loading of every retained item from
#   an EFA on exactly these N=300 respondents. If the numbering really is
#   preserved, re-running that EFA (PCA + varimax, 4 factors, 29 retained items
#   -- the method the paper states) must reproduce the published loading
#   PROFILE within each block under the identity mapping, and must do so better
#   than a random re-labelling of the items inside that block. If the mapping
#   were permuted, the profile would not track.
#
# DATA
#   Fetched from the PLOS supplement, not from irw_fetch(): the IRW table is a
#   melt of exactly these columns (see data/karpudewan_2022_stp_efa.py), and a
#   full export costs against the 200GB/30-day corpus cap for nothing.

suppressMessages(library(psych))

TABLE <- "karpudewan_2022_stp_efa"
URL <- paste0("https://journals.plos.org/plosone/article/file?",
              "type=supplementary&id=10.1371/journal.pone.0268509.s005")

# --- published loadings, S3 Appendix (Appendix 3), read down each factor column,
# --- with the construct prefixes renamed to the codes the data file uses.
PUB <- list(
  CH  = c(CH4 = .787, CH7 = .778, CH8 = .765, CH3 = .747, CH2 = .740,
          CH1 = .718, CH6 = .713, CH10 = .706, CH9 = .688, CH5 = .678),
  KN  = c(KN5 = .840, KN6 = .788, KN7 = .786, KN2 = .774, KN4 = .747,
          KN8 = .719, KN3 = .708),
  PSE = c(PSE1 = .814, PSE2 = .797, PSE3 = .736, PSE4 = .732),
  # The appendix's factor-4 cell lists items and loadings with mismatched blank
  # lines; every other block is strictly descending, so the loadings are paired
  # with the listed items in descending order.
  STP = c(STP2 = .798, STP3 = .719, STP1 = .715, STP4 = .698, STP8 = .631,
          STP5 = .622, STP7 = .605, STP10 = .515)
)
DROPPED <- c("KN1", "KN9", "STP6", "STP9")   # removed at EFA; no published wording

tmp <- tempfile(fileext = ".xlsx")
ok <- tryCatch({
  download.file(URL, tmp, quiet = TRUE,
                headers = c(`User-Agent` = "IRW-itemtext/1.0"))
  TRUE
}, error = function(e) FALSE)
if (!ok || !file.exists(tmp) || file.info(tmp)$size < 1000) {
  cat("Could not fetch the S2 Dataset supplement; cannot verify offline.\n")
  cat("VERDICT: FAIL\n"); quit(status = 0)
}
raw <- as.data.frame(readxl::read_excel(tmp, sheet = "EFA dataset"))

items <- c(paste0("STP", 1:10), paste0("KN", 1:9),
           paste0("CH", 1:10), paste0("PSE", 1:4))
X <- raw[, items]
X[] <- lapply(X, function(v) suppressWarnings(as.numeric(v)))
X[X < 1 | X > 5] <- NA                    # the single KN1 == 33 data-entry error
X <- X[, setdiff(items, DROPPED)]

fit <- principal(X, nfactors = 4, rotate = "varimax",
                 missing = TRUE, impute = "median")
L <- unclass(fit$loadings)

# Name each recovered component by the block it is dominated by.
blockof <- sub("[0-9]+$", "", colnames(X))
comp <- sapply(c("CH", "KN", "PSE", "STP"),
               function(b) unname(which.max(colMeans(abs(L[blockof == b, , drop = FALSE])))))
stopifnot(length(unique(comp)) == 4)

set.seed(20260907)
NPERM <- 20000
pass <- TRUE
for (b in names(PUB)) {
  pub <- PUB[[b]]
  obs <- L[names(pub), comp[[b]]]
  r <- cor(pub, obs)
  perm <- replicate(NPERM, cor(pub, sample(obs)))
  p <- mean(perm >= r)
  cat("=== block ", b, " (", length(pub), " items)\n", sep = "")
  cat(sprintf("%-8s %10s %10s\n", "item", "published", "re-run"))
  for (i in seq_along(pub))
    cat(sprintf("%-8s %10.3f %10.3f\n", names(pub)[i], pub[i], obs[i]))
  cat(sprintf("identity-mapping r = %.3f   permutation p = %.4f\n\n", r, p))
  if (b %in% c("CH", "KN", "STP") && !(r >= 0.70 && p <= 0.05)) pass <- FALSE
}

cat("What this does NOT establish:\n",
    " - PSE/PE. Its four published loadings span .732-.814 and the re-run does\n",
    "   not order them the same way (permutation p ~ 0.2), so PE1..PE4 -> PSE1..PSE4\n",
    "   is asserted from the construct rename, not verified. The paper's own body\n",
    "   quote for PSE4 (\"I am confident to deliver integrated STEM education\")\n",
    "   corroborates PE4 = PSE4 only.\n",
    " - Near-tied neighbours inside a block (e.g. published KN6 .788 vs KN7 .786)\n",
    "   are not separated by this route.\n",
    " - KN1, KN9, STP6, STP9 carry no item_text at all: the source never published\n",
    "   their wording, so there is nothing to verify for them.\n", sep = "")

cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
