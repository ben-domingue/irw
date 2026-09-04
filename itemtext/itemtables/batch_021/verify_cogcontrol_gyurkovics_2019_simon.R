# verify_cogcontrol_gyurkovics_2019_simon.R
#
# CLAIM UNDER TEST (mapping_basis = reconstructed):
#   each item code targ_19..targ_26 denotes one specific Simon-task display --
#   an arrow pointing in one of four directions, presented on one of four sides
#   of fixation -- and the shipped item_text / correct_response name that display.
#
# The OSF readme documents `targ` only as "the identifier of the specific target
# image", so the display is decoded from the deposit's own trial data:
#   (a) the key code recorded on CORRECT trials gives the arrow's DIRECTION.
#       Participants pressed keypad 2/4/6/8 for down/left/right/up (paper, Method).
#       The stored codes 98/100/102/104 are the Windows virtual-key codes for the
#       numeric keypad (VK_NUMPAD0 = 96, so key n -> 96 + n), which is the unique
#       assignment consistent with the paper's design constraint that "right was
#       always paired with left, and up was always paired with down".
#   (b) `cong` (invariant within targ) plus the paper's rule -- congruent = arrow
#       direction and location match, incongruent = opposite -- gives the LOCATION.
#       The 3-letter `code` feature string corroborates (b) independently: its
#       outer letter equals its middle letter exactly on congruent trials.
#
# This is NOT a plumbing check: if item_text for any two targ codes were swapped,
# step 4 below breaks.

suppressMessages(library(irw))

TABLE <- "cogcontrol_gyurkovics_2019_simon"
SRC   <- "https://osf.io/download/rmsk9/"          # simon_merge.csv, OSF node 7vbtr
ITEMS_CSV <- file.path(dirname(sub("^--file=", "",
    commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
    paste0(TABLE, "__items.csv"))

f <- tempfile(fileext = ".csv")
ok <- tryCatch({ download.file(SRC, f, quiet = TRUE); TRUE }, error = function(e) FALSE)
if (!ok || !file.exists(f) || file.size(f) < 1e5) {
    cat("could not download the OSF source file -- cannot verify\nVERDICT: FAIL\n"); quit(status = 0)
}
d <- read.csv(f, strip.white = TRUE)
d <- d[, c("subid", "code", "cong", "targ", "resp", "trial", "block", "Acc", "RT")]
d$code <- trimws(d$code)
cat(sprintf("source: simon_merge.csv -- %s trials, %d participants\n",
            format(nrow(d), big.mark = ","), length(unique(d$subid))))

## ---- (a) direction, from the key code on correct trials -----------------
ok_tr <- d[d$Acc == 1, ]
KEY <- c("98" = 2, "100" = 4, "102" = 6, "104" = 8)          # 96 + keypad digit
DIR <- c("2" = "down", "4" = "left", "6" = "right", "8" = "up")
GLY <- c(down = "↓", left = "←", right = "→", up = "↑")
WHERE <- c(down = "below fixation", up = "above fixation",
           left = "left of fixation", right = "right of fixation")
OPP <- c(down = "up", up = "down", left = "right", right = "left")

targs <- paste0("targ_", 19:26)
cat("\n-- decode --\n")
cat(sprintf("%-8s %5s %6s %9s %6s %8s %-32s\n",
            "item", "cong", "key", "purity", "dir", "loc", "derived item_text"))
derived_text <- derived_key <- character(0)
pure_all <- TRUE
for (i in 19:26) {
    ki <- ok_tr$resp[ok_tr$targ == i]
    tab <- sort(table(ki), decreasing = TRUE)
    kc <- names(tab)[1]; purity <- tab[[1]] / length(ki)
    if (purity < 0.999) pure_all <- FALSE
    key <- KEY[[kc]]; dir <- DIR[[as.character(key)]]
    cg <- unique(d$cong[d$targ == i])
    if (length(cg) != 1) { cat("cong not invariant within targ", i, "\nVERDICT: FAIL\n"); quit(status = 0) }
    loc <- if (cg == 0) dir else OPP[[dir]]
    txt <- paste0(GLY[[dir]], " presented ", WHERE[[loc]])
    derived_text <- c(derived_text, txt); derived_key <- c(derived_key, as.character(key))
    cat(sprintf("%-8s %5d %6s %9.4f %6s %8s %-32s\n",
                paste0("targ_", i), cg, kc, purity, dir, loc, txt))
}
names(derived_text) <- names(derived_key) <- targs

## ---- (b) independent corroboration from the `code` feature string --------
mid <- substr(d$code, 2, 2); out <- substr(d$code, 1, 1)
tab_cc <- table(d$cong, out == mid)
cat("\n-- `code` outer letter == middle letter, by congruency --\n")
print(tab_cc)
code_ok <- tab_cc["0", "FALSE"] == 0 && tab_cc["1", "TRUE"] == 0 &&
           all(substr(d$code, 1, 1) == substr(d$code, 3, 3))
cat("congruent <=> outer==middle, and code is always XYX:", code_ok, "\n")
# each targ maps to exactly one middle letter within a participant
mid_ok <- max(tapply(mid, paste(d$subid, d$targ), function(x) length(unique(x)))) == 1
cat("per-participant targ -> one middle letter:", mid_ok, "\n")

## ---- (c) live per-item n vs raw per-targ n (server-side, no export) -------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- s$per_item; pi <- pi[match(targs, pi$item), ]
raw_n <- as.integer(table(d$targ)[as.character(19:26)])
cat("\n-- per-item n: raw simon_merge.csv vs live IRW table --\n")
cat(sprintf("%-8s %8s %8s %6s\n", "item", "raw", "live", "diff"))
for (j in seq_along(targs))
    cat(sprintf("%-8s %8d %8d %6d\n", targs[j], raw_n[j], pi$n[j], pi$n[j] - raw_n[j]))
n_ok <- all(pi$n == raw_n)

## ---- (d) shipped file must equal the derived decode ----------------------
it <- read.csv(ITEMS_CSV)
ship <- unique(it[, c("item", "item_text", "correct_response")])
ship <- ship[match(targs, ship$item), ]
cat("\n-- shipped vs derived --\n")
cat(sprintf("%-8s %-32s %-32s %5s %5s\n", "item", "shipped", "derived", "s_key", "d_key"))
for (j in seq_along(targs))
    cat(sprintf("%-8s %-32s %-32s %5s %5s\n", targs[j], ship$item_text[j],
                derived_text[j], ship$correct_response[j], derived_key[j]))
text_ok <- all(ship$item_text == derived_text)
key_ok  <- all(as.character(ship$correct_response) == derived_key)
cat(sprintf("item_text matches: %d/8   correct_response matches: %d/8\n",
            sum(ship$item_text == derived_text),
            sum(as.character(ship$correct_response) == derived_key)))

## ---- (e) semantic check: the Simon effect --------------------------------
rt <- d$RT; rt[rt == 0] <- NA
cat("\n-- Simon effect implied by the decode --\n")
for (cg in c(0, 1))
    cat(sprintf("%-12s acc %.4f  RT %.1f ms  (n=%d)\n",
                if (cg == 0) "congruent" else "incongruent",
                mean(d$Acc[d$cong == cg]), mean(rt[d$cong == cg], na.rm = TRUE),
                sum(d$cong == cg)))
simon_ms <- mean(rt[d$cong == 1], na.rm = TRUE) - mean(rt[d$cong == 0], na.rm = TRUE)
cat(sprintf("Simon effect: +%.1f ms, incongruent slower\n", simon_ms))
eff_ok <- simon_ms > 0 && mean(d$Acc[d$cong == 1]) < mean(d$Acc[d$cong == 0])

cat("\nNOT established by this script: the drawn appearance of the arrow images\n",
    "(the deposit ships no stimulus files, so the glyphs render a direction, not a\n",
    "shape), and the verbatim participant instructions, which are unpublished and\n",
    "shipped blank. Everything else -- which of the 8 displays each targ code is --\n",
    "is pinned item by item.\n", sep = "")

pass <- pure_all && code_ok && mid_ok && n_ok && text_ok && key_ok && eff_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
