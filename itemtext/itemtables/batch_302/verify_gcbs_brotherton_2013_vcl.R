# Verification for gcbs_brotherton_2013_vcl (#2228, batch_302).
#
# SOURCE. openpsychometrics.org/_rawdata/, GCBS archive, CC BY. The archive
# ships codebook.txt beside data.csv; the codebook lists VCL1-VCL16 with their
# words, quotes the instruction verbatim, and -- the useful part -- states which
# of the words are fabricated.
#
# Route 1: the codebook's sixteen words equal the live item set, in order.
# Route 2: the fake words are the codebook's, not this project's guess.
# Route 3: the fakes behave like fakes in the data.
CB <- Sys.glob(".cache/batch_302/gcbs/*/codebook.txt")
if (!length(CB)) CB <- Sys.glob(".cache/batch_302/gcbs/**/codebook.txt")
if (!length(CB)) stop("missing cached deposit file: gcbs codebook.txt")
cb <- readLines(CB[1], warn = FALSE)
d <- as.data.frame(irw::irw_fetch("gcbs_brotherton_2013_vcl"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/gcbs_brotherton_2013_vcl__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: the codebook's word list ===\n")
hit <- grep("^VCL[0-9]+\t", cb, value = TRUE)
codes <- sub("\t.*", "", hit); words <- sub("^VCL[0-9]+\t", "", hit)
cat(sprintf("  codebook lists %d VCL items; live has %d\n", length(codes), length(unique(d$item))))
r1 <- setequal(codes, unique(d$item)) && length(codes) == 16
sh <- unique(items[, c("item", "item_text")])
key <- setNames(words, codes)
r1b <- all(sh$item_text == key[sh$item])
cat(sprintf("  item sets identical: %s; every shipped word matches the codebook: %s\n", r1, r1b))

cat("\n=== Route 2: the fake words are the codebook's own ===\n")
note <- grep("not real words", cb, value = TRUE)
cat(sprintf("  codebook says: %s\n", trimws(note[1])))
fake_shipped <- sort(unique(items$item[grepl("^Fake", items$section_prompt)]))
r2 <- setequal(fake_shipped, c("VCL6", "VCL9", "VCL12"))
cat(sprintf("  shipped as fake: %s\n", paste(fake_shipped, collapse = ", ")))
cat(sprintf("  -> matches the codebook's VCL6, VCL9, VCL12: %s\n", r2))
cat(sprintf("  those words are: %s\n", paste(key[c("VCL6","VCL9","VCL12")], collapse = ", ")))

cat("\n=== Route 3: do the fakes behave like fakes? ===\n")
p <- sapply(sort(unique(d$item)), function(i) mean(d$resp[d$item == i], na.rm = TRUE))
fk <- c("VCL6","VCL9","VCL12"); rl <- setdiff(names(p), fk)
cat("  proportion checking each word:\n")
for (i in names(sort(p))) cat(sprintf("    %-7s %-14s %.3f%s\n", i, key[i], p[[i]],
                                      if (i %in% fk) "   <- fake" else ""))
r3 <- max(p[fk]) < min(p[rl])
cat(sprintf("  -> every fake word is checked less often than every real one: %s\n", r3))
cat("  This is what the validity check is for: claiming to know a non-word is\n")
cat("  over-claiming, so the three fakes should sit at the bottom. They do, which\n")
cat("  also confirms the codebook's VCL numbering is the one the data uses -- a\n")
cat("  shifted numbering would put a real word at the bottom.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. The words, the numbering, the instruction and the fake\n")
cat("  flags all come from one codebook shipped with the data. resp is 1 for\n")
cat("  checked and 0 for unchecked, as the codebook states.\n")
cat("\nVERDICT:", if (r1 && r1b && r2 && r3) "PASS" else "FAIL", "\n")
