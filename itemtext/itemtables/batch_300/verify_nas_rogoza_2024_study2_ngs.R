# Verification for nas_rogoza_2024_study2_ngs (#2228, batch_300).
#
# SOURCE. Rogoza, Baran, Flakus, Krammer & Fatfouta (2024), 'Introducing the
# Narcissistic Antagonism Scale', Psychological Assessment; OSF deposit
# osf.io/u93eq, CC0. This table is the NGS (Narcissistic Grandiosity Scale)
# block of the study's Adjective Scales of Narcissism.
#
# THE DEPOSIT'S CODEBOOK LISTS THE ADJECTIVES IN ADMINISTRATION ORDER, with the
# instruction text and the anchors. What it does not do is label them NGS1..13 --
# so the load-bearing step is matching the codebook's running order onto the
# .sav's column blocks, which Route 1 does and which is exact.
#
# Route 1: the codebook's 42 adjectives partition onto the .sav's NVS/NAS/NGS
#   blocks as 11 / 18 / 13, in sequence, with no slack.
# Route 2: the shipped 13 are the Agentic factor of the paper's own supplement.
# Route 3: the scale, from the codebook.
SAV <- ".cache/batch_300/nas_study2.sav"
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven")
if (!file.exists(SAV)) stop("missing cached deposit file: ", SAV)
suppressWarnings(suppressMessages(library(haven)))
s <- read_sav(SAV)
d <- as.data.frame(irw::irw_fetch("nas_rogoza_2024_study2_ngs"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_300/nas_rogoza_2024_study2_ngs__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

# the codebook's list, in the order it prints them
CB <- c("Ashamed","Ignored","Self-absorbed","Fragile","Underappreciated","Envious","Resentful",
"Insecure","Irritable","Misunderstood","Vengeful",
"Abusive","Spiteful","Scheming","Humiliating","Misusing","Insidious","Treacherous","Nasty",
"Devaluing","Offending","Oppressive","Denouncing","Exploitative","Manipulative","Depreciating",
"Conceitful","Condescending","Selfish",
"Perfect","Superior","Heroic","Omnipotent","Authoritative","Glorious","Prestigous","Acclaimed",
"Prominent","High-status","Dominant","Envied","Powerful")

cat("=== Route 1: the codebook order partitions onto the .sav blocks ===\n")
nvs <- grep("^NVS[0-9]+$", names(s), value = TRUE)
nas <- grep("^NAS[0-9]+$", names(s), value = TRUE)
ngs <- grep("^NGS[0-9]+$", names(s), value = TRUE)
cat(sprintf("  .sav item columns: NVS %d, NAS %d, NGS %d (total %d)\n",
            length(nvs), length(nas), length(ngs), length(nvs)+length(nas)+length(ngs)))
cat(sprintf("  codebook adjectives: %d\n", length(CB)))
r1 <- length(CB) == length(nvs) + length(nas) + length(ngs) &&
      length(nvs) == 11 && length(nas) == 18 && length(ngs) == 13
cat(sprintf("  -> 11 + 18 + 13 = %d, exactly the codebook's count: %s\n", length(CB), r1))
cat("  The blocks appear in the .sav in that order (NVS, then NAS, then NGS) and\n")
cat("  the codebook prints the adjectives in one running list, so the last 13 are\n")
cat("  the NGS block. There is no slack: any other split leaves a block short.\n")
shipped <- unique(items[, c("item","item_text")])
shipped <- shipped[order(as.integer(sub("NGS","",shipped$item))), ]
r1b <- identical(shipped$item_text, tail(CB, 13))
cat(sprintf("  shipped NGS1..NGS13 equals the codebook's last 13, in order: %s\n", r1b))

cat("\n=== Route 2: the same 13 are the supplement's Agentic factor ===\n")
AG <- c("Perfect","Superior","Heroic","Omnipotent","Authoritative","Glorious","Prestigous",
        "Acclaimed","Prominent","High-status","Dominant","Envied","Powerful")
r2 <- setequal(shipped$item_text, AG)
cat(sprintf("  Supplementary Table 2 loads these on Agentic rather than Neurotic or\n"))
cat(sprintf("  Antagonistic, and the shipped set matches it: %s\n", r2))
cat("  Two sources that were produced separately -- a codebook listing order and\n")
cat("  a factor-loading table -- pick out the same 13 adjectives.\n")

cat("\n=== Route 3: the response scale ===\n")
lv <- sort(unique(d$resp))
r3 <- identical(as.numeric(lv), as.numeric(1:7))
cat(sprintf("  live levels %s; the codebook states '1 = Not at all' and '7 = Extremely': %s\n",
            paste(lv, collapse=","), r3))
cat("  Only those two points are labelled, so 2-6 ship with option_text blank.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Which adjective is NGS1 versus NGS2 by any route other than the codebook's\n")
cat("  print order. That order is the administration order the deposit documents,\n")
cat("  and the block arithmetic leaves no alternative alignment, but nothing in\n")
cat("  the response data separates one adjective from another within the block.\n")
cat("  Note also that the administered language is Polish; the adjectives ship in\n")
cat("  English because the codebook and NAS.xlsx give English alongside Polish.\n")
cat("\nVERDICT:", if (r1 && r1b && r2 && r3) "PASS" else "FAIL", "\n")
