# verify_klatt_2016_speed_estimation.R
#
# What is at stake. The 48 item codes have the shape
# @<front-surface-px>_<car>_<actual-speed>_<position>, and the shipped table
# claims (in its public_note) that each of those four fields means what it looks
# like: "insel" = the pedestrian centre island, "trottoir" = the pavement, the
# 45/50/55 token is the car's ACTUAL speed (so resp = estimate - actual), the
# @ prefix is the car's measured front-surface area in pixels, and the car
# abbreviations are the eight vehicles Klatt, Chesham & Lobmaier (2016) name.
# item_text is blank by design (a virtual-reality picture-stimulus task, no
# published per-trial wording), so this script verifies the CODE SEMANTICS -- the
# only mapping claim the table makes.
#
# The falsifiable predictions are the paper's own Results (PLOS ONE 11(7):
# e0159455, "Speed estimations"). Each is recomputed from the live data after
# undoing the processing script's transform, est = resp + actual_speed.

suppressMessages(library(irw))
TABLE <- "klatt_2016_speed_estimation"

d <- irw::irw_fetch(TABLE)
m <- regmatches(d$item, regexec("^@([0-9]+)_([a-z]+)_([0-9]+)_(insel|trottoir)$", d$item))
stopifnot(all(lengths(m) == 5))
d$px    <- as.numeric(sapply(m, `[`, 2))
d$car   <-            sapply(m, `[`, 3)
d$speed <- as.numeric(sapply(m, `[`, 4))
d$pos   <-            sapply(m, `[`, 5)
d$est   <- d$resp + d$speed          # undo resp = estimate - actual speed

# Paper's classification of the eight vehicles (Materials):
#   high power = BMW 6 E63, Alfa Romeo 147, Mercedes SLK R171, Chrysler Crossfire
#   low  power = Nissan Micra K12, VW New Beetle 9C, Kia Picanto BA, Toyota Prius II
#   big  = Alfa, BMW (high) and Toyota, VW (low); small = Chrysler, Mercedes, Kia, Nissan
LOW   <- c("nis", "vw", "kia", "toy")
SMALL <- c("nis", "kia", "merc", "chr")
d$power <- ifelse(d$car %in% LOW,   "low",   "high")
d$size  <- ifelse(d$car %in% SMALL, "small", "big")

chk <- function(label, published, observed, tol = 0.05) {
    ok <- abs(observed - published) <= tol
    cat(sprintf("%-42s published %7.2f   observed %7.2f   diff %6.3f  %s\n",
                label, published, observed, observed - published,
                if (ok) "ok" else "MISS"))
    ok
}

cat("=== Klatt et al. (2016), Results / 'Speed estimations' vs live IRW data ===\n")
pass <- c(
  chk("overall mean estimate (km/h)",            45.2, mean(d$est), 0.05),
  chk("centre island  (item code 'insel')",      44.2, mean(d$est[d$pos == "insel"])),
  chk("pavement       (item code 'trottoir')",   46.2, mean(d$est[d$pos == "trottoir"])),
  chk("actual speed token 45",                   40.7, mean(d$est[d$speed == 45])),
  chk("actual speed token 50",                   45.4, mean(d$est[d$speed == 50])),
  chk("actual speed token 55",                   49.5, mean(d$est[d$speed == 55])),
  chk("low-power cars  {nis,vw,kia,toy}",        45.7, mean(d$est[d$power == "low"])),
  chk("high-power cars {bmw,alf,merc,chr}",      44.7, mean(d$est[d$power == "high"])),
  chk("small front surface {nis,kia,merc,chr}",  46.9, mean(d$est[d$size == "small"])),
  chk("big front surface  {vw,toy,bmw,alf}",     43.5, mean(d$est[d$size == "big"]))
)

cat(sprintf("\nestimate range: observed %d-%d km/h, paper 'ranged between 10 and 100'\n",
            min(d$est), max(d$est)))
pass <- c(pass, min(d$est) == 10 && max(d$est) == 100)

# The @ prefix is claimed to be the car's front-surface area in pixels; the paper
# reports r = -.848, p = .008 between front surface and mean speed estimate (n = 8 cars).
per_car <- aggregate(est ~ car + px, d, mean)
per_car <- per_car[order(per_car$px), ]
cat("\nper-car mean estimate against the @ prefix:\n")
print(data.frame(car = per_car$car, px = per_car$px,
                 mean_est = sprintf("%.3f", per_car$est)), row.names = FALSE)
ct <- cor.test(per_car$px, per_car$est)
cat(sprintf("r = %.3f (paper -.848), p = %.4f (paper .008)\n", ct$estimate, ct$p.value))
pass <- c(pass, abs(ct$estimate - (-0.848)) <= 0.002)

# How much of the labelling this pins: over all 8! relabellings of the car token,
# how many reproduce the four published class means AND the published r?
mm <- per_car$est[match(c("nis","kia","merc","chr","vw","toy","bmw","alf"), per_car$car)]
px <- c(44898, 47862, 53543, 55023, 60036, 65383, 67786, 68619)
lowi <- c(TRUE,TRUE,FALSE,FALSE,TRUE,TRUE,FALSE,FALSE)
smli <- c(TRUE,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE)
perms <- function(v) if (length(v) == 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i)
        lapply(perms(v[-i]), function(p) c(v[i], p))))
n_ok <- 0
for (p in perms(1:8)) {
    x <- mm[p]
    if (abs(mean(x[lowi]) - 45.7) < 0.05 && abs(mean(x[!lowi]) - 44.7) < 0.05 &&
        abs(mean(x[smli]) - 46.9) < 0.05 && abs(mean(x[!smli]) - 43.5) < 0.05 &&
        abs(cor(px, x) + 0.848) < 0.0005) n_ok <- n_ok + 1
}
cat(sprintf("\nrelabellings of the eight car tokens consistent with all five published\nstatistics: %d of 40320\n", n_ok))

cat("\nWhat this does NOT establish: item_text is blank for every row, so no wording\n",
    "mapping is at stake here. Of the two surviving relabellings, the rival swaps\n",
    "nis<->merc and permutes vw/alf/bmw; it is excluded only because the car tokens\n",
    "are self-describing abbreviations of the paper's eight named vehicles.\n", sep = "")

cat(if (all(pass) && n_ok <= 2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
