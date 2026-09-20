# Verification for gilbert_meta_95 (#2228, batch_302).  STATUS: PARTIAL.
#
# SOURCE. Cicek, Ulker, Ozer & Kiyak, 'ChatGPT versus expert feedback on
# clinical reasoning questions and their effect on learning: a randomized
# controlled trial', Postgraduate Medical Journal, doi:10.1093/postmj/qgae170;
# deposit zenodo.org/records/13769970, CC BY 4.0.
#
# THE MAPPING IS THE DEPOSIT'S COLUMN HEADERS and is exact; the WORDING is not
# available anywhere. 'Immediate Test.xlsx' names its columns "Uncomplicated UTI
# KFQ 1" through "Pyelonephritis KFQ 4", which is precisely the twelve live
# codes once lowercased and underscored. But Key Features Questions are clinical
# vignettes, and neither the deposit nor the paper prints them -- the paper is
# not open access (Europe PMC reports isOpenAccess = N). So item_text says what
# each item IS and states outright that the vignette is unpublished.
#
# Route 1: the deposit's headers equal the live codes.
# Route 2: three scenarios of four questions each.
# Route 3: partial credit -- resp is continuous, which the KFQ format implies.
if (!requireNamespace("readxl", quietly = TRUE)) stop("needs readxl")
XL <- ".cache/batch_302/g95_immediate.xlsx"
if (!file.exists(XL)) stop("missing cached deposit file: ", XL)
suppressWarnings(suppressMessages(library(readxl)))
x <- as.data.frame(read_excel(XL))
d <- as.data.frame(irw::irw_fetch("gilbert_meta_95"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/gilbert_meta_95__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: deposit headers against the live codes ===\n")
hdr <- grep("KFQ", names(x), value = TRUE)
norm <- tolower(gsub(" ", "_", hdr))
cat(sprintf("  deposit KFQ columns: %d\n", length(hdr)))
for (h in head(hdr, 3)) cat(sprintf("    %-32s -> %s\n", h, tolower(gsub(" ", "_", h))))
r1 <- setequal(norm, unique(d$item))
cat(sprintf("  lowercased and underscored, identical to the live set: %s\n", r1))

cat("\n=== Route 2: three scenarios, four questions each ===\n")
sp <- unique(items[, c("item", "section_prompt")])
tb <- table(sp$section_prompt)
print(tb)
r2 <- length(tb) == 3 && all(tb == 4)
cat(sprintf("  -> 4 / 4 / 4 across the three clinical scenarios: %s\n", r2))

cat("\n=== Route 3: partial credit ===\n")
lv <- sort(unique(d$resp))
frac <- sum(lv != round(lv))
cat(sprintf("  %d distinct resp values, of which %d are non-integer (e.g. %s)\n",
            length(lv), frac, paste(head(lv[lv != round(lv)], 5), collapse = ", ")))
cat(sprintf("  range %.2f to %.2f\n", min(lv), max(lv)))
r3 <- frac > 0
cat(sprintf("  -> scoring is continuous, not 0/1: %s\n", r3))
cat("  Key Features Questions award partial credit across the decisions a\n")
cat("  vignette requires, so a fractional score is expected and correct_response\n")
cat("  is empty -- there is no single right answer to record.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The question wording, which is the point of an itemtext table and is the\n")
cat("  reason this is PARTIAL. The vignettes are not in the Zenodo deposit and\n")
cat("  the paper is paywalled, so item_text names the scenario and the question\n")
cat("  number and says the wording is unpublished rather than inventing a stem.\n")
cat("  The deposit also has a 'Delayed Test.xlsx' with the same twelve columns;\n")
cat("  the live table does not distinguish immediate from delayed, so the codes\n")
cat("  may pool both administrations.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
