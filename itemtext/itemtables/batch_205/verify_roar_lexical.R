# Verification for roar_lexical (#1945, batch_205).
#
# SOURCE. Yeatman, Tang, Donnelly, Yablonski, Ramamurthy, Karipidis et al. (2021),
# 'Rapid online assessment of reading ability', Scientific Reports 11:6396, CC BY.
#
# THE ITEM CODE IS THE STIMULUS. data/lexical_roar.R sets item <- x$word, so the
# code is the word or pseudoword that was flashed on screen; item_text is that
# same string, which is a transcription rather than a label.
#
# THE KEY IS IN THE RESPONSE TABLE, which is why this ships fully addressable.
# The live data carries realpseudo per item, and the paper fixes the response
# mapping outright: "Participants pressed 'right' for a real word or 'left' for a
# pseudoword." So each of the two option rows per item carries the resp it scores
# (1 for the correct button, 0 for the other), its raw_resp key, and the item's
# correct_response.
#
# Route 1: 500 codes, split 250 real / 250 pseudo as the paper states.
# Route 2: correct_response agrees with realpseudo for every item.
# Route 3: accuracy behaves as a lexical decision task should.
d <- as.data.frame(irw::irw_fetch("roar_lexical"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item); d$realpseudo <- as.character(d$realpseudo)
items <- read.csv("itemtables/batch_205/roar_lexical__items.csv", stringsAsFactors = FALSE)

cat("=== Route 1: the stimulus set ===\n")
m <- unique(d[, c("item", "realpseudo")])
n_real <- sum(m$realpseudo == "real"); n_ps <- sum(m$realpseudo == "pseudo")
cat(sprintf("  %d distinct codes, %d real / %d pseudo\n", nrow(m), n_real, n_ps))
r1 <- nrow(m) == 500 && n_real == 250 && n_ps == 250 && !any(duplicated(m$item))
cat(sprintf("  matches the paper's '250 real words and 250 pseudowords': %s\n", r1))

cat("\n=== Route 2: correct_response agrees with the data's own key ===\n")
key <- setNames(ifelse(m$realpseudo == "real", "real word", "pseudoword"), m$item)
sh  <- unique(items[, c("item", "correct_response")])
r2 <- nrow(sh) == 500 && all(sh$correct_response == key[sh$item])
cat(sprintf("  %d items checked, all agree: %s\n", nrow(sh), r2))
opt <- items[!is.na(items$option_text), ]
r2b <- all(tapply(opt$resp, opt$item, function(v) identical(sort(as.numeric(v)), c(0, 1))))
cat(sprintf("  every item carries exactly one resp=1 option and one resp=0 option: %s\n", r2b))
cat("  So option_text joins to the response data: resp=1 rows name the button a\n")
cat("  correct answer required, resp=0 rows the button that scored wrong.\n")

cat("\n=== Route 3: does accuracy behave like a lexical decision task? ===\n")
acc <- tapply(d$resp, d$realpseudo, mean)
cat(sprintf("  mean accuracy  real %.3f | pseudo %.3f\n", acc[["real"]], acc[["pseudo"]]))
sub <- tapply(d$resp, d$id, mean)
cat(sprintf("  per-participant accuracy: median %.3f, range %.3f-%.3f over %d participants\n",
            median(sub), min(sub), max(sub), length(sub)))
r3 <- acc[["real"]] > 0.5 && acc[["pseudo"]] > 0.5 && median(sub) > 0.6
cat(sprintf("  -> both stimulus classes above chance and participants mostly accurate: %s\n", r3))
cat("  A mislabelled realpseudo would push one class below chance, since resp is\n")
cat("  scored against it. This is a weak check by design -- Route 2 is the one\n")
cat("  that pins the key, and it reads the same column the score was computed from.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  That the shipped word list is the paper's version-1 list rather than a\n")
cat("  later revision -- the GitHub repository the processing script cites now\n")
cat("  returns 404, so the stimulus file could not be re-read. The codes ARE the\n")
cat("  stimuli, though, so the item text cannot drift from them.\n")
cat("\nVERDICT:", if (r1 && r2 && r2b && r3) "PASS" else "FAIL", "\n")
