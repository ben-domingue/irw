# verify_johannisson_2016_ipip_neo.R
#
# CLAIM UNDER TEST. data/johannisson_2016_ipip_neo.py assigns the IRW item codes
# POSITIONALLY -- item_block.index = [f"item_{i+1:03d}" for i in range(120)] over rows
# 50..169 (0-indexed) of the supplement peerj-04-2245-s002.xlsx, whose column 0 on those
# same rows holds the IPIP-NEO-120 item statements. The shipped item_text is that column.
# So the claim is: item_NNN is exactly the response row whose label is the shipped text.
#
# TWO INDEPENDENT CHECKS, both of which break if any two items' texts were swapped:
#
#  A. RE-RUN THE DERIVATION (core model section 3). Rebuild the long table from the raw
#     supplement and compare it cell-for-cell with irw_fetch() on (id, item). No two items
#     have identical 200-value response vectors, so a match on all 24,000 cells pins each
#     item uniquely -- not merely as a set. A +/-1 row shift is reported as a control.
#
#  B. DIRECTION OF resp (the option_text axis). The IPIP-NEO-120 cycles its 30 facets in a
#     fixed order (item i -> facet ((i-1) mod 30)+1, domain order N,E,O,A,C), and the same
#     supplement carries the online IPIP-NEO scoring service's OWN facet percentile score
#     for each participant (rows 10..48). Scoring the shipped items with 1 = "Very
#     Inaccurate" and the published reverse key must reproduce those facet scores. If the
#     anchors were reversed (1 = "Very Accurate"), every one of the 30 correlations would
#     flip sign.
#
# Needs network: the Europe PMC supplementary zip, and irw_fetch (24,000 rows, ~0.5 MB).

suppressMessages({library(irw); library(readxl)})

TABLE   <- "johannisson_2016_ipip_neo"
SUPPL   <- "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4957988/supplementaryFiles"
MEMBER  <- "peerj-04-2245-s002.xlsx"
N_ITEMS <- 120; N_SUBJ <- 200; ROW0 <- 51  # 1-based first item row in the sheet

# Reverse-keyed items of the IPIP-NEO-120 (Johnson 2014), by item number.
REV <- c(9,19,24,30,39,40,48,49,51,53,54,60,62,67,68,69,70,73,74,75,78,79,80,81,83,84,
         85,88,89,90,92,94,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,
         113,114,115,116,118,119,120)   # 55 items, read off the IPIP-NEO-120 form's own
                                        # reversed 5-4-3-2-1 response rows

tmp <- tempfile(fileext = ".zip")
utils::download.file(SUPPL, tmp, quiet = TRUE,
                     headers = c(`User-Agent` = "IRW-itemtext/1.0"))
xl <- file.path(tempdir(), MEMBER); utils::unzip(tmp, files = MEMBER, exdir = tempdir())
raw <- as.data.frame(read_excel(xl, col_names = FALSE, .name_repair = "minimal"))

ids   <- as.character(unlist(raw[5, 2:(1 + N_SUBJ)]))
items <- sprintf("item_%03d", seq_len(N_ITEMS))
blk   <- apply(as.matrix(raw[ROW0:(ROW0 + N_ITEMS - 1), 2:(1 + N_SUBJ)]), 2, as.numeric)
dimnames(blk) <- list(items, ids)
labels <- trimws(as.character(raw[[1]][ROW0:(ROW0 + N_ITEMS - 1)]))

d <- irw::irw_fetch(TABLE)
d$id <- as.character(d$id); d$item <- as.character(d$item)
live <- matrix(NA_real_, N_ITEMS, N_SUBJ, dimnames = list(items, ids))
live[cbind(match(d$item, items), match(d$id, ids))] <- as.numeric(d$resp)

cat("== A. re-run of the positional derivation ==\n")
cat(sprintf("live rows fetched: %d ; raw cells: %d\n", nrow(d), sum(!is.na(blk))))
agree <- sum(live == blk, na.rm = TRUE)
cat(sprintf("cells identical (live vs raw, matched on id AND item): %d of %d\n",
            agree, N_ITEMS * N_SUBJ))
dupvec <- sum(duplicated(split(blk, row(blk))))
cat(sprintf("pairs of items with identical 200-value response vectors: %d\n", dupvec))
for (s in c(1, -1)) {
    sh <- blk[((seq_len(N_ITEMS) - 1 - s) %% N_ITEMS) + 1, , drop = FALSE]
    cat(sprintf("control, item text shifted by %+d: items reproducing live exactly: %d/120\n",
                s, sum(rowSums(live != sh, na.rm = TRUE) == 0)))
}
cat(sprintf("first/last shipped label at position 1/120: %s / %s\n",
            sQuote(labels[1]), sQuote(labels[120])))
okA <- agree == N_ITEMS * N_SUBJ && dupvec == 0

cat("\n== B. resp direction against the deposit's own IPIP-NEO facet scores ==\n")
frow <- list(N = c(36,37,38,39,40,41), E = c(12,13,14,15,16,17),
             O = c(44,45,46,47,48,49), A = c(20,21,22,23,24,25),
             C = c(28,29,30,31,32,33))   # 1-based sheet rows of the 6 facets per domain
dom <- c("N","E","O","A","C")
cors <- numeric(30); nms <- character(30)
for (k in 0:29) {
    r <- frow[[dom[(k %% 5) + 1]]][(k %/% 5) + 1]
    fac <- as.numeric(unlist(raw[r, 2:(1 + N_SUBJ)]))
    idx <- k + 1 + 30 * (0:3)
    x <- blk[idx, , drop = FALSE]
    x[idx %in% REV, ] <- 6 - x[idx %in% REV, , drop = FALSE]
    cors[k + 1] <- cor(colSums(x), fac, use = "complete.obs")
    nms[k + 1]  <- as.character(raw[[1]][r])
}
for (k in seq_len(30)) cat(sprintf("  %-22s r = %+.3f\n", nms[k], cors[k]))
cat(sprintf("30 facets: min r = %+.3f, mean r = %+.3f (a reversed 1..5 anchoring flips every sign)\n",
            min(cors), mean(cors)))
okB <- min(cors) > 0.8

cat("\nNOT established: the administration language (neither the paper nor the deposit\n",
    "states it; the deposit's labels are English). No instructions text is published by\n",
    "either source, so instructions ships blank.\n", sep = "")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
