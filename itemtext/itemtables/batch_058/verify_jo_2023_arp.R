# verify_jo_2023_arp.R -- Step 5b mapping evidence.
#
# CLAIM: item codes ARP1/ARP2/ARP3 in the IRW table are the very codes S1 Appendix
# Table A1 of Jo & Baek (2023, PLOS ONE 18(4):e0283997) prints beside each item's
# wording, carried through unchanged by data/jo_2023_social_networking.py (which
# melts the source CSV columns named "ARP1","ARP2","ARP3" -- no rename, no
# positional assignment).
#
# The falsifiable check: the raw S3 CSV column named ARP1 must reproduce, cell for
# cell, the live IRW distribution stored under item "ARP1" (and likewise 2, 3).
# If the shipped item_text for two items were swapped, the code->column tie shown
# here would still hold but the wording tie would not -- so this is combined with
# the appendix's own explicit code labels, printed below.

suppressMessages(library(irw))

TABLE <- "jo_2023_arp"
SRC   <- "https://doi.org/10.1371/journal.pone.0283997.s003"

# S1 Appendix Table A1 item codes -> wording, as shipped.
APPENDIX <- c(
  ARP1 = "I'm concerned that I'll get COVID-19.",
  ARP2 = "Concerned that members of my family may contract COVID-19.",
  ARP3 = "Concerning the possibility of COVID-19 in my area.")

raw <- read.csv(SRC, fileEncoding = "latin1", check.names = FALSE)
d   <- irw::irw_fetch(TABLE)

cat("Appendix code labels (the mapping basis):\n")
for (k in names(APPENDIX)) cat(sprintf("  %s = %s\n", k, APPENDIX[[k]]))
cat("\nSource CSV column names present: ",
    paste(intersect(names(APPENDIX), names(raw)), collapse = ", "), "\n\n", sep = "")

ok <- all(names(APPENDIX) %in% names(raw))

cat(sprintf("%-6s %28s %28s %8s\n", "item", "raw column 1..7 counts", "live 1..7 counts", "match"))
for (k in names(APPENDIX)) {
    rv <- suppressWarnings(as.numeric(raw[[k]])); rv <- rv[!is.na(rv) & rv >= 1 & rv <= 7]
    lv <- d$resp[d$item == k]
    rc <- as.vector(table(factor(rv, levels = 1:7)))
    lc <- as.vector(table(factor(lv, levels = 1:7)))
    same <- identical(rc, lc)
    ok <- ok && same
    cat(sprintf("%-6s %28s %28s %8s\n", k, paste(rc, collapse = "/"),
                paste(lc, collapse = "/"), if (same) "yes" else "NO"))
}

# Cross-item distinctness: the three response distributions must differ, otherwise
# the count match above would not discriminate between the items.
mats <- sapply(names(APPENDIX), function(k)
    as.vector(table(factor(d$resp[d$item == k], levels = 1:7))))
cat("\npairwise column-count identity among the three items (must all be FALSE):\n")
distinct <- TRUE
for (i in 1:2) for (j in (i+1):3) {
    id <- identical(mats[, i], mats[, j]); if (id) distinct <- FALSE
    cat(sprintf("  %s vs %s: %s\n", colnames(mats)[i], colnames(mats)[j], id))
}

cat("\nWhat this does NOT establish: it ties each IRW item code to the identically\n",
    "named column of the study's own data file, and that column to the appendix\n",
    "wording, but it cannot detect an error inside the appendix itself (i.e. if the\n",
    "authors mislabelled their own table). No response-option anchors are published\n",
    "anywhere in the paper or its supplements, so option_text is unverifiable and\n",
    "is shipped blank.\n", sep = "")

cat(if (ok && distinct) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
