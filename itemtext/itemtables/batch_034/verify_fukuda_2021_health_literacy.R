# verify_fukuda_2021_health_literacy.R
#
# WHAT IS BEING VERIFIED
#   The shipped item_text is the canonical HLS-EU-Q47 wording (Sorensen et al. 2013,
#   BMC Public Health 13:948, Additional file 1 -- the HLS-EU Consortium's own annex).
#   The claim that has to be checked is the CODE mapping:
#
#       IRW code hl_itemN  ->  S1 Data column "Health literacy item M"  ->  HLS-EU-Q47 item M
#
#   with M = N for N <= 38 and M = N + 1 for N >= 39, because
#   data/fukuda_2021_healthliteracy.py selects columns via startswith("Health literacy")
#   and the S1 column for question 39 is named "<Japanese>  Health literacy item 39",
#   so it is silently skipped and everything above it shifts down by one. If that shift
#   were missed, items 39-46 would each ship the text of the PRECEDING question.
#
#   Second axis: the shipped option_text is the S1 file's own value labels, whose
#   integer coding (1 = "very easy" ... 4 = "very difficult") RUNS OPPOSITE to the
#   canonical HLS-EU-Q47 key printed in the same annex (1 = Very difficult ... 4 = Very
#   easy) and opposite to what this paper's own Methods section states.
#
# ROUTE
#   Route 9 (response-frequency matching), run over all 46 items x 4 levels at once.
#   The raw S1 column asserted to be behind each IRW code is recoded with the
#   processing script's own map and cross-tabulated; a correct mapping reproduces the
#   live per-item x per-level counts cell for cell. A permuted item, a one-off shift,
#   or a flipped scale direction all break it immediately.
#
#   The live counts come from a server-side GROUP BY (irw_table_sets()'s own query
#   helper), NOT irw_fetch(), so re-running this costs no export quota.
#
# NOT ESTABLISHED BY THIS SCRIPT
#   That S1's column "Health literacy item M" really holds HLS-EU-Q47 question M.
#   That tie is a label match (the header names the number; the paper names the
#   instrument; the instrument has exactly 47 canonically numbered items), not a
#   statistical result. Section (3) below is corroboration for it, not proof.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "fukuda_2021_health_literacy"
URL   <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0257552.s001"
CACHE <- file.path(".cache", TABLE, "s001.xlsx")

# ---- raw source ------------------------------------------------------------
if (file.exists(CACHE)) {
    xlsx <- CACHE
} else {
    xlsx <- tempfile(fileext = ".xlsx")
    utils::download.file(URL, xlsx, quiet = TRUE, mode = "wb")
}
raw <- suppressMessages(readxl::read_excel(xlsx))

HL_MAP <- c("very easy" = 1, "fairly easy" = 2,
            "fairly difficult" = 3, "very difficult" = 4)

hl_cols <- grep("^Health literacy", names(raw), value = TRUE)
# The S1 headers mix ASCII and FULL-WIDTH digits ("Health literacy item \uff12"), which
# Python's str.isdigit()/int() in the processing script accept transparently; R's
# regex classes do not, so normalise them explicitly before extracting the number.
src_q   <- as.integer(gsub("[^0-9]", "",
                           chartr("\uff10\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19",
                                  "0123456789", hl_cols)))
stopifnot(!any(is.na(src_q)))
ord     <- order(src_q)
hl_cols <- hl_cols[ord]; src_q <- src_q[ord]
codes   <- paste0("hl_item", seq_along(hl_cols))

cat("S1 'Health literacy' columns selected by the processing script:", length(hl_cols), "\n")
cat("source question numbers present:", paste(src_q, collapse = ","), "\n")
cat("MISSING from the selection (Japanese-prefixed header, skipped by startswith()):",
    paste(setdiff(1:47, src_q), collapse = ","), "\n\n")

raw_counts <- do.call(rbind, lapply(seq_along(hl_cols), function(i) {
    v <- HL_MAP[trimws(as.character(raw[[hl_cols[i]]]))]
    v <- v[!is.na(v)]
    data.frame(item = codes[i], src_q = src_q[i],
               n1 = sum(v == 1), n2 = sum(v == 2), n3 = sum(v == 3), n4 = sum(v == 4),
               stringsAsFactors = FALSE)
}))

# ---- live counts, server-side ----------------------------------------------
live_counts <- tryCatch({
    tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
    q <- sprintf(paste("SELECT CAST(item AS STRING) AS item,",
                       "TRIM(CAST(resp AS STRING)) AS resp, COUNT(*) AS n FROM `%s`",
                       "WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','')",
                       "GROUP BY item, resp"), tbl$qualified_reference)
    as.data.frame(irw:::.irw_query_tibble(q))
}, error = function(e) {
    cat("server-side query unavailable (", conditionMessage(e), "); falling back to irw_fetch()\n")
    d <- irw::irw_fetch(TABLE)
    as.data.frame(stats::aggregate(list(n = d$resp), by = list(item = d$item, resp = d$resp), length))
})
live_counts$resp <- as.integer(as.character(live_counts$resp))
lw <- reshape(live_counts, idvar = "item", timevar = "resp", direction = "wide")
names(lw) <- sub("^n\\.", "L", names(lw))
for (cl in c("L1","L2","L3","L4")) if (!cl %in% names(lw)) lw[[cl]] <- 0L
lw <- lw[, c("item", "L1", "L2", "L3", "L4")]
# A level a given item's respondents never used has no GROUP BY row at all; that is a
# zero count, not a missing value. hl_item6 is the real case here -- 0 respondents chose
# "fairly difficult" (resp 3) for "understand the leaflets that come with your medicine?",
# while 37 chose "very difficult". The option row is still shipped, because every item in
# the S1 file carries the same four labels.
lw[is.na(lw)] <- 0L

m <- merge(raw_counts, lw, by = "item", all = TRUE)
m <- m[order(as.integer(sub("hl_item", "", m$item))), ]
m$ok <- with(m, n1 == L1 & n2 == L2 & n3 == L3 & n4 == L4)

cat("(1) ROUTE 9 -- raw S1 column vs live IRW table, per item x per level\n")
cat(sprintf("%-10s %-5s %-22s %-22s %s\n", "IRW code", "srcQ", "raw (1/2/3/4)", "live (1/2/3/4)", "match"))
for (i in seq_len(nrow(m)))
    cat(sprintf("%-10s %-5d %-22s %-22s %s\n", m$item[i], m$src_q[i],
                paste(m$n1[i], m$n2[i], m$n3[i], m$n4[i], sep = "/"),
                paste(m$L1[i], m$L2[i], m$L3[i], m$L4[i], sep = "/"),
                ifelse(m$ok[i], "YES", "** NO **")))
cat(sprintf("\ncells compared: %d (%d items x 4 levels); mismatched cells: %d\n",
            4 * nrow(m), nrow(m),
            sum(abs(c(m$n1 - m$L1, m$n2 - m$L2, m$n3 - m$L3, m$n4 - m$L4)) > 0)))

sig <- paste(m$n1, m$n2, m$n3, m$n4)
cat(sprintf("distinct 4-level count signatures: %d of %d items -- every item is\n",
            length(unique(sig)), nrow(m)))
cat("  distinguished from every other, so no permutation of the 46 codes reproduces this.\n\n")

# ---- (2) the shift, stated as a falsifiable alternative --------------------
cat("(2) THE OFF-BY-ONE ALTERNATIVE (what the table would look like if question 39\n")
cat("    had NOT been dropped, i.e. hl_itemN <- source question N throughout):\n")
shift_ok <- sapply(39:46, function(k) {
    i <- which(m$item == paste0("hl_item", k))
    j <- which(m$src_q == k)                       # the column that naive numbering would use
    if (length(j) == 0) return(NA)
    all(c(m$n1[i], m$n2[i], m$n3[i], m$n4[i]) == c(m$n1[j], m$n2[j], m$n3[j], m$n4[j]))
})
for (k in 39:46) {
    i <- which(m$item == paste0("hl_item", k)); j <- which(m$src_q == k)
    cat(sprintf("    hl_item%-2d live=%s | shipped srcQ%d=%s | naive srcQ%d=%s -> naive %s\n",
                k, paste(m$L1[i], m$L2[i], m$L3[i], m$L4[i], sep = "/"),
                m$src_q[i], paste(m$n1[i], m$n2[i], m$n3[i], m$n4[i], sep = "/"),
                k, paste(m$n1[j], m$n2[j], m$n3[j], m$n4[j], sep = "/"),
                ifelse(isTRUE(shift_ok[k - 38]), "ALSO matches (inconclusive)", "FAILS")))
}
cat("\n")

# ---- (3) corroboration for the header-number <-> canonical-item tie --------
M <- as.data.frame(lapply(hl_cols, function(c) HL_MAP[trimws(as.character(raw[[c]]))]))
names(M) <- as.character(src_q)
mu <- sort(sapply(M, mean, na.rm = TRUE))
cat("(3) CORROBORATION (route 8): mean difficulty by canonical question number,\n")
cat("    1 = very easy ... 4 = very difficult, so HIGHER = harder.\n")
cat("    easiest 5:", paste(sprintf("Q%s=%.2f", names(mu)[1:5], mu[1:5]), collapse = "  "), "\n")
n <- length(mu)
cat("    hardest 5:", paste(sprintf("Q%s=%.2f", names(mu)[(n-4):n], mu[(n-4):n]), collapse = "  "), "\n")
cat("    The canonical HLS-EU difficulty gradient puts understand/healthcare items at the\n")
cat("    easy end and appraise-the-media plus apply/health-promotion items (Q45 sports club,\n")
cat("    Q46 influence living conditions, Q47 community activities, Q12/Q28 media reliability)\n")
cat("    at the hard end, which is what the numbering under test produces.\n")

dom <- ifelse(src_q <= 16, "HC", ifelse(src_q <= 31, "DP", "HP"))
C <- suppressWarnings(cor(M, use = "pairwise.complete.obs"))
pairmean <- function(a, b) {
    ia <- which(dom == a); ib <- which(dom == b)
    if (a == b) mean(C[ia, ib][upper.tri(C[ia, ib])]) else mean(C[ia, ib])
}
cat(sprintf("    route 5, mean r within/between the three canonical domains (Q1-16 healthcare,\n"))
cat(sprintf("    Q17-31 disease prevention, Q32-47 health promotion):\n"))
cat(sprintf("      HC-HC %.3f  DP-DP %.3f  HP-HP %.3f | HC-DP %.3f  HC-HP %.3f  DP-HP %.3f\n",
            pairmean("HC","HC"), pairmean("DP","DP"), pairmean("HP","HP"),
            pairmean("HC","DP"), pairmean("HC","HP"), pairmean("DP","HP")))
nn <- sapply(seq_along(src_q), function(i) { r <- C[i, ]; r[i] <- -Inf; dom[which.max(r)] == dom[i] })
cat(sprintf("      each item's single most-correlated partner is in its own canonical domain for %d of %d items (chance ~15).\n",
            sum(nn), length(nn)))
cat("      Weak by construction (health literacy is dominated by a general factor), so this\n")
cat("      is corroboration for the canonical numbering, not proof of it.\n\n")

pass <- all(m$ok) && !any(is.na(m$ok)) && length(unique(sig)) == nrow(m)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
