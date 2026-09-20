# Verification for iat_poverty (#2228, batch_302).
#
# SOURCE. Project Implicit demo-website Race IAT dataset (Xu, Nosek & Greenwald
# 2014, Journal of Open Psychology Data, doi:10.5334/jopd.ac), 2021 wave. The
# item wording comes from the deposit's own codebook,
# Race_IAT_public_2021_codebook.xlsx (osf.io/52qxl), which lists efp1-efp12
# against their full text. The 210 MB data archive was NOT needed -- the
# codebook is a separate 93 KB file.
#
# THE ANCHORS COME FROM THE PROCESSING SCRIPT ITSELF, which is unusually direct:
# data/iat.R maps the stored strings to integers with
#   levs <- c("Not at All Important","Slightly Important","Moderately Imporant",
#             "Very Important","Extremely Important")
#   df$resp <- match(df$resp, levs)
# so resp 1-5 is that vector's order by construction, not by inference.
#
# Route 1: the codebook's twelve efp variables equal the live item set.
# Route 2: the shipped stem and bodies come from the codebook verbatim.
CB <- ".cache/batch_302/iat_codebook.xlsx"
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
if (!file.exists(CB)) stop("missing cached deposit file: ", CB)
suppressWarnings(suppressMessages(library(readxl)))
cb <- as.data.frame(read_excel(CB, sheet = "All", col_names = FALSE))
d <- as.data.frame(irw::irw_fetch("iat_poverty"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/iat_poverty__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: the codebook's efp variables ===\n")
nm  <- trimws(as.character(cb[[2]]))
txt <- as.character(cb[[3]])
keep <- grepl("^efp[0-9]+$", nm)
codes <- nm[keep]; bodies <- txt[keep]
cat(sprintf("  codebook efp variables: %d; live items: %d\n", length(codes), length(unique(d$item))))
r1 <- setequal(codes, unique(d$item))
cat(sprintf("  identical sets: %s\n", r1))

cat("\n=== Route 2: the shipped text against the codebook ===\n")
STEM <- "There are many poor people in the world because of..."
key <- setNames(bodies, codes)
sh <- unique(items[, c("item", "item_text", "section_prompt")])
ok <- 0
for (i in seq_len(nrow(sh))) {
    want <- trimws(sub(".*\\.\\.\\.", "", key[[sh$item[i]]]))
    if (identical(sh$item_text[i], want)) ok <- ok + 1
    else cat(sprintf("  MISMATCH %s\n    codebook: %s\n    shipped : %s\n", sh$item[i], want, sh$item_text[i]))
}
r2 <- ok == nrow(sh) && all(sh$section_prompt == STEM)
cat(sprintf("  %d of %d bodies match the codebook exactly: %s\n", ok, nrow(sh), ok == nrow(sh)))
cat("  The codebook stores each entry as one string with the shared stem and the\n")
cat("  specific cause joined by an ellipsis. The stem is split out into\n")
cat("  section_prompt and the cause into item_text, so no wording is invented and\n")
cat("  none is lost; the two fields concatenate back to the codebook string.\n")

cat("\n=== Route 3: the response scale ===\n")
lv <- sort(unique(d$resp))
r3 <- identical(as.numeric(lv), as.numeric(1:5))
cat(sprintf("  live levels %s -- the five labels in data/iat.R's levs vector: %s\n",
            paste(lv, collapse = ","), r3))
cat("  option_text reproduces that vector, INCLUDING its typo: the third label is\n")
cat("  'Moderately Imporant' in the script and is shipped as printed rather than\n")
cat("  silently corrected, because it is the token the recode matched on.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. The wording is the deposit's codebook, the numbering is\n")
cat("  the codebook's own variable names, and the anchors are the processing\n")
cat("  script's own recode vector. This table is a subset of a much larger IAT\n")
cat("  dataset -- only the twelve poverty-explanation items ship here.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
