# Shared verification for the two simsalRbim_* tables (#1945, batch_205).
# Sourced by the per-table wrappers, which set TB, SRC and EXPECT first.
#
# SOURCE. Pfefferle, Talbot, Kahnau, Cassidy, Brockhausen, Jaap et al. (2025),
# 'Advancing preference testing in humans and animals', Behavior Research Methods,
# doi:10.3758/s13428-025-02668-5; data at github.com/mytalbot/simsalRbim_data.
#
# THESE ARE NOT QUESTIONNAIRES, which decides the shape. Each trial presents a
# PAIR of stimuli and records a quantity for each; data/simsalRbim.R pivots
# optionA/optionB into item and quantityA/quantityB into resp, so the item code
# is the stimulus's own name in the source file and there is no question text at
# all. item_text describes the stimulus in brackets rather than inventing a
# prompt, and option_text is blank because a preference trial has no printed
# response options -- the options ARE the two stimuli, one per row of the trial.
#
# Route 1: the code set equals the distinct optionA/optionB values in the source.
# Route 2: the stimulus list matches what the paper names for this set.
# Route 3: the long table reproduced from the source file, trial by trial.
if (!file.exists(SRC)) stop("missing cached source file: ", SRC)
x <- read.table(SRC, header = TRUE, stringsAsFactors = FALSE)

d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: codes are the source file's option values ===\n")
opts <- sort(unique(c(x$optionA, x$optionB)))
r1 <- setequal(opts, unique(d$item))
cat(sprintf("  source options (%d): %s\n", length(opts), paste(opts, collapse = ", ")))
cat(sprintf("  identical to the live code set: %s\n", r1))

cat("\n=== Route 2: the stimulus list the paper names for this set ===\n")
r2 <- setequal(opts, EXPECT)
cat(sprintf("  paper's set: %s\n", paste(sort(EXPECT), collapse = ", ")))
cat(sprintf("  matches: %s\n", r2))
cat(sprintf("  %s\n", NOTE))

cat("\n=== Route 3: the long table reproduced from the source ===\n")
long <- rbind(data.frame(item = x$optionA, resp = x$quantityA),
              data.frame(item = x$optionB, resp = x$quantityB))
cat(sprintf("  source trials %d -> %d long rows; live rows %d\n", nrow(x), nrow(long), nrow(d)))
r3 <- nrow(long) == nrow(d)
ok <- TRUE
for (i in opts) {
    a <- sort(long$resp[long$item == i]); b <- sort(d$resp[d$item == i])
    same <- length(a) == length(b) && all(abs(a - b) < 1e-9)
    ok <- ok && same
    cat(sprintf("  %-12s source n=%3d live n=%3d identical: %s\n", i, length(a), length(b), same))
}
cat(sprintf("  -> every stimulus's response vector reproduced: %s\n", ok))

cat("\n=== What this does NOT establish ===\n")
cat("  Any administered wording, because there is none -- nothing was read to a\n")
cat("  subject. The bracketed item_text is this project's description of the\n")
cat("  stimulus, taken from the paper's Methods, and is marked as such.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && ok) "PASS" else "FAIL", "\n")
