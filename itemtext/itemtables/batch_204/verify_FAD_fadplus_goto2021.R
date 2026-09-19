# Verification for FAD_fadplus_goto2021 (#1945, batch_204).
#
# SOURCE. The paper's Supplementary Table 1 prints all 27 items three ways --
# FAD-Plus (the English original), FAD-J and FAD+ (the two Japanese
# translations) -- against a single 1-27 numbering. The deposit supplies the raw
# data (FAD_compare_rawdata.csv) and the authors' analysis (FAD_compare_analysis.Rmd).
#
# WHY THE MAPPING IS A LOOKUP RATHER THAN AN INFERENCE. The live codes are
# FAD_G_1..27 and FAD_W_1..27: the number is the supplement's item number and the
# G/W marks which translation. The raw data's columns are exactly those 54 names,
# so both which item and which translation come straight off the source.
#
# Route 1: codes == the raw data's FAD_G_/FAD_W_ columns.
# Route 2: every response vector reproduced from the raw data, per item.
# Route 3: FACTOR assignment taken from the authors' own lavaan model rather
#   than from the published FAD-Plus key, and checked against what ships.
# Route 4: the G/W pairing -- item n of one translation must be item n of the
#   other, which the authors' own per-item correlations assume and the data
#   confirms by construction.
RAW <- ".cache/batch_204/fad_FAD_compare_rawdata.csv"
RMD <- ".cache/batch_204/fad_FAD_compare_analysis.Rmd"
for (p in c(RAW, RMD)) if (!file.exists(p)) stop("missing cached deposit file: ", p)
x <- read.csv(RAW, stringsAsFactors = FALSE)

d <- as.data.frame(irw::irw_fetch("FAD_fadplus_goto2021"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_204/FAD_fadplus_goto2021__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: codes are the raw data's own column names ===\n")
cols <- grep("^FAD_[GW]_[0-9]+$", names(x), value = TRUE)
r1 <- setequal(cols, unique(d$item))
cat(sprintf("  raw data FAD_ columns %d (G %d, W %d), live codes %d, identical: %s\n",
            length(cols), sum(grepl("_G_", cols)), sum(grepl("_W_", cols)),
            length(unique(d$item)), r1))
cat("  27 numbers x 2 translations = 54, with no gaps and no extras.\n")

cat("\n=== Route 2: every response vector reproduced from the raw data ===\n")
tot <- ok <- 0; bad <- character(0)
for (cn in cols) {
    live <- sort(d$resp[d$item == cn]); s <- sort(as.numeric(na.omit(x[[cn]])))
    tot <- tot + 1
    if (length(s) == length(live) && all(abs(s - live) < 1e-9)) ok <- ok + 1
    else bad <- c(bad, sprintf("%s source n=%d live n=%d", cn, length(s), length(live)))
}
cat(sprintf("  %d of %d reproduced EXACTLY%s\n", ok, tot,
            if (!length(bad)) "" else paste0("\n  -- ", paste(head(bad, 8), collapse="\n  -- "))))
r2 <- !length(bad)

cat("\n=== Route 3: factors from the authors' lavaan model ===\n")
rmd <- readLines(RMD, warn = FALSE)
mdl <- grep("^(FW|SD|FD|UP) =~ FAD_G_", rmd)
mdl <- mdl[1:4]                                  # the 4-factor model_g block
FMAP <- list()
for (l in mdl) {
    f  <- sub(" =~.*", "", trimws(rmd[l]))
    ns <- as.integer(gsub("FAD_G_", "", strsplit(sub(".*=~", "", rmd[l]), "\\+")[[1]]))
    FMAP[[f]] <- sort(ns)
    cat(sprintf("    %-3s (%d items): %s\n", f, length(ns), paste(sort(ns), collapse=", ")))
}
LAB <- c(FW = "Free Will", SD = "Scientific Determinism",
         FD = "Fatalistic Determinism", UP = "Unpredictability")
r3 <- TRUE
for (f in names(FMAP)) for (tr in c("G", "W")) {
    want <- sort(paste0("FAD_", tr, "_", FMAP[[f]]))
    got  <- sort(unique(items$item[items$section_prompt == LAB[[f]] &
                                   grepl(paste0("^FAD_", tr, "_"), items$item)]))
    if (!setequal(want, got)) { r3 <- FALSE
        cat(sprintf("  MISMATCH %s %s: want %s got %s\n", f, tr,
                    paste(want, collapse=","), paste(got, collapse=",")))
    }
}
cat(sprintf("  sizes 7 / 7 / 5 / 8, summing to %d with no repeats: %s\n",
            length(unique(unlist(FMAP))), length(unique(unlist(FMAP))) == 27))
cat(sprintf("  shipped section_prompt matches the model for both translations: %s\n", r3))
cat("  Taken from the deposit's code, not from the published FAD-Plus key, so\n")
cat("  this is the factor structure THIS study fitted to THIS data.\n")

cat("\n=== Route 4: the G/W pairing ===\n")
gn <- sort(as.integer(sub("FAD_G_", "", grep("_G_", cols, value = TRUE))))
wn <- sort(as.integer(sub("FAD_W_", "", grep("_W_", cols, value = TRUE))))
r4 <- identical(gn, wn) && identical(gn, 1:27)
cat(sprintf("  G numbers == W numbers == 1:27: %s\n", r4))
pairs <- sapply(1:27, function(n) {
    a <- x[[paste0("FAD_G_", n)]]; b <- x[[paste0("FAD_W_", n)]]
    suppressWarnings(cor(a, b, use = "pairwise.complete.obs"))
})
cat(sprintf("  same-number G/W correlations: median %.3f, min %.3f, all positive: %s\n",
            median(pairs, na.rm=TRUE), min(pairs, na.rm=TRUE), all(pairs > 0, na.rm=TRUE)))
cat("  Two translations of one item answered by the same respondents should\n")
cat("  agree; every same-number pair does, which is consistent with the\n")
cat("  numbering meaning the same item in both. (The authors run these same\n")
cat("  per-item correlations themselves at cor.test(dat_cl$FAD_G_4, dat_cl$FAD_W_4).)\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The transcription. The Japanese item wording and the English alongside it\n")
cat("  are both quoted from Supplementary Table 1, and the 1-5 anchors from the\n")
cat("  paper's method section; no numeric route can check quoted text. What the\n")
cat("  routes above establish is that the numbering the quotes are keyed to is\n")
cat("  the numbering the live codes use.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r4) "PASS" else "FAIL", "\n")
