## dd_rotation: diffIRT's `rotation` data (van der Maas, Molenaar, Maris,
## Kievit & Borsboom, 2011; from Kievit, 2010 and Borst, Kievit, Thompson &
## Kosslyn, 2011). 121 people, 10 binary mental rotation items (same/different
## judgements on two 3D objects), with response times in seconds.
##
## itemcov_angle (added 2026-11-25): each item's rotation angle in degrees, as
## listed in the diffIRT documentation (?rotation, "The specific rotation
## angles of the different items are: ..."). The data themselves do not
## record it.
##
## Usage: Rscript diffIRT_dat.R [out.csv]  (needs the diffIRT package, or set
## DIFFIRT_RDA to the path of its data/rotation.rda)

args <- commandArgs(trailingOnly = TRUE)
out <- if (length(args) >= 1) args[1] else "dd_rotation.csv"
rda <- Sys.getenv("DIFFIRT_RDA", "")
if (nzchar(rda)) load(rda) else { library(diffIRT); data(rotation) }

acc <- rotation[, 1:10]
rt <- rotation[, 11:20]
angle <- c(150, 50, 100, 150, 50, 100, 150, 50, 150, 100)

id <- 1:nrow(rt)
item <- 1:ncol(rt)
L <- list()
for (i in 1:ncol(rt)) {
  L[[i]] <- data.frame(id = id, item = item[i], resp = acc[, i], rt = rt[, i],
                       itemcov_angle = angle[i])
}
x <- data.frame(do.call("rbind", L))
df <- x[!is.na(x$rt), ]
write.csv(df, out, row.names = FALSE)
