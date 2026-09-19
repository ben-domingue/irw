# verify_pickova2025_moral_justifications.R
#
# CLAIM UNDER TEST: item codes mj_1..mj_7 correspond, IN ORDER, to columns 51-57
# (1-based) of the raw Google Forms export
#   figshare 10.6084/m9.figshare.30576341.v2, file 59422829
#   "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# whose header row 1 carries the item wording that was shipped in item_text.
# There is no processing script for this table in the repo, so the code->column
# tie is POSITIONAL and cannot be exempted; it has to be checked against data.
#
# ROUTE 9 (response-frequency matching). The raw file stores the same 1-7
# integers the live table stores, so a correct positional mapping reproduces the
# per-item x per-level count matrix cell for cell. Any transposition of two item
# codes breaks it, because no two of the seven raw frequency vectors are equal.
#
# The raw counts below are HARD-CODED from that file (they cannot change), so the
# script needs only the live IRW data and runs offline apart from irw_fetch().

suppressMessages(library(irw))

TABLE <- "pickova2025_moral_justifications"

# Raw file, columns 51..57, counts of responses 1,2,...,7 (blanks excluded).
RAW <- rbind(
  mj_1 = c(21, 29, 16, 29, 20, 14,  5),   # col 51 "My individual purchase doesn't really make a difference."
  mj_2 = c(15,  7, 16, 24, 31, 27, 14),   # col 52 "It's the government's job to regulate brands, not the consumer's."
  mj_3 = c(19, 17, 13, 32, 27, 16,  7),   # col 53 "The environmental and social problems are so big..."
  mj_4 = c(13,  9,  8, 17, 23, 37, 26),   # col 54 "I need to save money for more important things..."
  mj_5 = c(10, 11,  5, 27, 34, 23, 24),   # col 55 "Many 'sustainable' brands are just hypocritical..."
  mj_6 = c( 3,  6,  7, 12, 32, 35, 37),   # col 56 "The low prices allow me to experiment with my style more freely."
  mj_7 = c(11,  4,  5, 15, 17, 43, 37)    # col 57 "I often need a specific item for a one-time event..."
)
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
LIVE <- matrix(0L, nrow = 7, ncol = 7,
               dimnames = list(paste0("mj_", 1:7), 1:7))
tb <- table(d$item, d$resp)
LIVE[rownames(tb), colnames(tb)] <- as.integer(tb)

cat("per-item x per-level counts: RAW (deposit cols 51-57) vs LIVE (irw_fetch)\n\n")
cat(sprintf("%-6s %-30s %-30s %s\n", "item", "raw 1..7", "live 1..7", "match"))
ok <- TRUE
for (i in rownames(RAW)) {
  same <- all(RAW[i, ] == LIVE[i, ])
  ok <- ok && same
  cat(sprintf("%-6s %-30s %-30s %s\n", i,
              paste(RAW[i, ], collapse = ","),
              paste(LIVE[i, ], collapse = ","),
              if (same) "yes" else "NO"))
}
cat(sprintf("\ncells matching: %d of %d\n", sum(RAW == LIVE), length(RAW)))

# Discriminating power: how many of the 5039 non-identity permutations of the
# seven codes would also reproduce the live matrix? A correct, non-degenerate
# mapping admits exactly zero.
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i)
    lapply(perms(v[-i]), function(p) c(v[i], p))))
allp <- perms(1:7)
n_alt <- sum(vapply(allp, function(p)
  !identical(p, 1:7) && all(RAW[p, ] == LIVE), logical(1)))
cat(sprintf("alternative permutations that also reproduce the live counts: %d of %d\n",
            n_alt, length(allp) - 1))

cat("\nWhat this does NOT establish: the resp<->option_text axis. The deposit\n",
    "publishes no anchor labels for the 1-7 scale points, so option_text is blank\n",
    "for every level by design and the scale direction is unverified. It also says\n",
    "nothing about the instructions stem's own wording (which carries a source\n",
    "artifact, 'how much you 6 with', shipped verbatim).\n", sep = "")

cat(if (ok && n_alt == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
