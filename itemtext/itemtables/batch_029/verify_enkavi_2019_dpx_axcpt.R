# verify_enkavi_2019_dpx_axcpt.R
#
# This table is BLOCKED: no item text was shipped, so there is no item->wording
# mapping to verify. What IS verifiable, and what the block rests on, is the
# claim that the `probeN` half of each item code names a dot-pattern IMAGE whose
# role is randomised per participant -- so no single item_text could state what
# probe4.png "is". This script re-runs that claim against the raw SRO data.
#
# Claim (falsifiable):
#   A. Within a worker, each probeN plays exactly ONE role (valid "X" or invalid
#      "Y") -- nunique(condition[2]) == 1 for every worker x probe cell.
#   B. Pooled across workers, EVERY probeN appears under ALL FOUR conditions
#      AX / AY / BX / BY -- i.e. the role is assigned per session, not per image.
#   Together: probeN is a shuffled image label, not stable stimulus content.
#   Matches expfactory-experiments/dot_pattern_expectancy/experiment.js:
#     var probes = jsPsych.randomization.shuffle(['probe1.png', ... 'probe6.png'])
#     var valid_probe = probes.pop()
#
# What this does NOT establish: anything about item_text, because none exists.
# It establishes that the block is determinate rather than an unlocated source.

URL <- paste0("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/",
              "master/Data/Complete_02-16-2019/Individual_Measures/dot_pattern_expectancy.csv.gz")

tmp <- tempfile(fileext = ".csv.gz")
download.file(URL, tmp, quiet = TRUE, mode = "wb")
d <- read.csv(gzfile(tmp), stringsAsFactors = FALSE)
d <- d[d$exp_stage == "test", ]

d$probe <- sub(".*(probe[0-9])\\.png.*", "\\1", d$stimulus)
d$role  <- substr(d$condition, 2, 2)   # "X" (valid probe) or "Y" (invalid)

cat(sprintf("test-stage trials: %d | workers: %d | probes: %s\n",
            nrow(d), length(unique(d$worker_id)),
            paste(sort(unique(d$probe)), collapse = ",")))

# --- A. within-worker role uniqueness -------------------------------------
cells <- tapply(d$role, list(d$worker_id, d$probe), function(x) length(unique(x)))
cells <- cells[!is.na(cells)]
cat(sprintf("\nA. worker x probe cells: %d | cells with exactly 1 role: %d | with 2 roles: %d\n",
            length(cells), sum(cells == 1), sum(cells > 1)))
A_ok <- all(cells == 1)

# --- B. across-worker role variation --------------------------------------
tab <- table(d$probe, d$condition)
cat("\nB. probe x condition counts (pooled across workers):\n")
print(tab)
per_probe <- apply(tab > 0, 1, sum)
cat(sprintf("\n   distinct conditions per probe: %s (4 = role is randomised per session)\n",
            paste(sprintf("%s=%d", names(per_probe), per_probe), collapse = " ")))
B_ok <- all(per_probe == 4)

# --- also: the stimulus field is an image tag, never text ------------------
img <- mean(grepl("<img src", d$stimulus, fixed = TRUE))
cat(sprintf("\nC. share of test trials whose `stimulus` field is an <img> tag: %.4f\n", img))
C_ok <- img == 1

cat("\nNote: this verifies the BASIS OF THE BLOCK, not a mapping. No item text was\n",
    "shipped for this table, so there is no item_text<->item correspondence to test.\n", sep = "")

cat(if (A_ok && B_ok && C_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
