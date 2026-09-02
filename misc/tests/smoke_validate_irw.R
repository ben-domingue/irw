## Smoke test for misc/validate_irw.R -- the copy external contributors source
## from a raw GitHub URL. Nothing in this repo imports it, so without this it
## could stop being valid R and no one would find out until a stranger tried it.
##
## The check vocabulary is guarded separately, by the R/Python parity test in
## irw_validate/tests/, which asserts the file's `# @check` markers match
## irw_validate.model.CORE_CHECKS.
here <- dirname(sub("^--file=", "",
                    grep("^--file=", commandArgs(FALSE), value = TRUE)[1]))
source(file.path(here, "..", "validate_irw.R"))

clean <- data.frame(id = c(1, 2), item = c("a", "b"), resp = c(1, 2))
stopifnot(validate_irw_status(validate_irw(clean, "clean")) == 0L)

## a documented column must not trip the covariate-prefix note
with_treat <- cbind(clean, treat = c(0, 1))
stopifnot(length(validate_irw(with_treat, "treat")$notes) == 0L)

## and a real violation must be reported AND set a non-zero status
broken <- data.frame(id = c(1, 2), item = c("a", "b"), resp = c("x", "y"))
stopifnot(validate_irw_status(validate_irw(broken, "broken")) == 1L)

cat("validate_irw.R OK\n")
