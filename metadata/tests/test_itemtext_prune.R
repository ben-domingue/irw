## Run from metadata/: Rscript tests/test_itemtext_prune.R
## Base R only; synthetic frames, no credentials or network.
source("itemtext_prune.R")

quiet <- function(...) invisible(NULL)
live <- paste0("t", 1:100)
frame <- function(tables) data.frame(table = tables, stringsAsFactors = FALSE)

## A row whose table is no longer served goes.
out <- prune_unserved_itemtext(frame(c(live, paste0("gone", 1:7))), live,
                               announce = quiet)
stopifnot(nrow(out) == 100L, !any(grepl("^gone", out$table)))

## Nothing to do leaves the frame alone, and every column survives.
wide <- data.frame(table = live, FK_grade = seq_along(live),
                   stringsAsFactors = FALSE)
stopifnot(identical(prune_unserved_itemtext(wide, live, announce = quiet), wide))

## Case-only difference is ALIVE, not gone: the published names and the listing
## disagree on case for a handful of tables (review R-31), and an exact match
## would delete a row whose table is there under another capitalisation.
mixed <- frame(c(toupper(live[1]), live[-1]))
stopifnot(nrow(prune_unserved_itemtext(mixed, live, announce = quiet)) == 100L)

## A listing that came back empty is a failed read, not a withdrawn corpus.
stopifnot(inherits(try(prune_unserved_itemtext(frame(live), character(0),
                                               announce = quiet),
                       silent = TRUE), "try-error"))

## ...and so is one that came back short. 25 of 125 is 20%, over the ceiling.
err <- try(prune_unserved_itemtext(frame(c(live, paste0("gone", 1:25))), live,
                                   announce = quiet), silent = TRUE)
stopifnot(inherits(err, "try-error"),
          grepl("failed listing", conditionMessage(attr(err, "condition"))))

## The ceiling is a parameter, so a real large withdrawal round can be let
## through deliberately rather than by editing the guard out.
ok <- prune_unserved_itemtext(frame(c(live, paste0("gone", 1:25))), live,
                              max_share = 0.5, announce = quiet)
stopifnot(nrow(ok) == 100L)

## The announcement names the tables, because a silent deletion of published
## rows is not reviewable.
said <- character(0)
invisible(prune_unserved_itemtext(frame(c(live, "gone1")), live,
                                  announce = function(x) said <<- c(said, x)))
stopifnot(any(grepl("gone1", said)), any(grepl("dropping 1 row", said)))

cat("test_itemtext_prune.R: all assertions passed\n")
