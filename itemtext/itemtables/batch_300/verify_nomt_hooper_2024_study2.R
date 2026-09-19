# Verification for nomt_hooper_2024_study2 (#2228, batch_300).  STATUS: PARTIAL.
#
# SOURCE. Hooper, Tomarken & Gauthier (2024), 'Measuring visual ability in
# linguistically diverse populations', Behavior Research Methods 57:36, CC BY;
# data at doi:10.6084/m9.figshare.24395098.v2.
#
# THE STIMULI ARE PICTURES, so there is no administered item wording to
# transcribe. Each trial shows three novel objects and the participant picks the
# one studied earlier; item_text describes that in brackets and says outright
# that the stimuli are images. The instruction text in `instructions` is the
# paper's description of the procedure, not screen text.
#
# WHAT IS AND IS NOT PINNED. The item code is the trial number --
# data/nomt_hooper_2024.R does item <- str_extract(item_obj, "\\d+") over column
# names like "Accurate 12". The paper says the test used Greebles, Ziggerins and
# Sheinbugs, and that Study 2 combined two of them, but the trial numbers here
# do not divide into the paper's blocks cleanly (see Route 2), so no NOMT is
# assigned to any item. That is why this is PARTIAL.
#
# Route 1: the item set, and that the gaps are the unscored learning trials.
# Route 2: the attempted split into the paper's two 72-trial tests, and why it
#   is not shipped.
# Route 3: the key is exactly recoverable from the data -- reported, not shipped.
d <- as.data.frame(irw::irw_fetch("nomt_hooper_2024_study2"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
it <- sort(as.integer(unique(d$item)))

cat("=== Route 1: the scored trials ===\n")
cat(sprintf("  %d items, trial numbers %d to %d\n", length(it), min(it), max(it)))
gaps <- setdiff(min(it):max(it), it)
cat(sprintf("  %d numbers in that span carry no item\n", length(gaps)))
cat("  The paper explains the gaps: each NOMT has a study phase and then test\n")
cat("  trials ('In the following 54 test phase trials'), and only test trials are\n")
cat("  scored. The unscored study trials are the missing numbers.\n")
r1 <- length(it) == 144
cat(sprintf("  -> 144 scored trials, as the paper's '72 trials with Ziggerins and 72\n     with Greebles' implies: %s\n", r1))

cat("\n=== Route 2: can the two tests be told apart? Not from this data ===\n")
for (cut in c(106, 107, 108))
    cat(sprintf("  split at %3d: %3d below, %3d above\n", cut, sum(it <= cut), sum(it > cut)))
cat("  No cut gives 72/72, so the trial numbering is not two clean 72-trial\n")
cat("  blocks -- it runs to 212 with its own internal gaps. Rather than guess a\n")
cat("  boundary, section_prompt is left empty and no item is labelled Greebles,\n")
cat("  Ziggerins or Sheinbugs. This is the open step and the reason for PARTIAL.\n")
r2 <- TRUE   # reported, not a pass/fail condition

cat("\n=== Route 3: the key is recoverable, and is deliberately not shipped ===\n")
ok <- d[!is.na(d$resp) & d$resp == 1 & !is.na(d$resp_raw), ]
n1 <- tapply(ok$resp_raw, ok$item, function(v) length(unique(v)))
cat(sprintf("  items where every correct response used the same alternative: %d of %d\n",
            sum(n1 == 1), length(n1)))
r3 <- all(n1 == 1)
cat(sprintf("  -> the correct position (1, 2 or 3) is determined exactly for every item: %s\n", r3))
cat("  It is NOT shipped in correct_response. Deriving it would make this project\n")
cat("  the author of the key, which owes an entry on the public issues page under\n")
cat("  the 2026-09-03 ruling (key_source=derived_from_responses), and the value is\n")
cat("  small without the images. Recorded here so a later pass can add it cheaply.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Anything about the objects themselves. The stimuli ship in the deposit as\n")
cat("  JPEG archives; this table names none of them, and item_text is this\n")
cat("  project's description of the trial format rather than administered text.\n")
cat("  The two instruction-language groups (English, Spanish) sat the same\n")
cat("  nonverbal trials, so the language does not vary by item.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
