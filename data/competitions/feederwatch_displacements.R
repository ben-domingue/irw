##Interspecific displacements at bird feeders across North America, reported by Project
##FeederWatch participants. Miller, E., Bonter, D., Eldermire, C., Freeman, B., Greig, E.,
##Harmon, L., Lisle, C., & Hochachka, W. (2017). Fighting over food
##unites the birds of North America in a continental dominance hierarchy. Behavioral
##Ecology, 28(6), 1454-1463. https://doi.org/10.1093/beheco/arx108
##Data: Dryad doi:10.5061/dryad.49vj1, read from its Zenodo mirror, record 4997232
##(https://zenodo.org/records/4997232), file forDryad.csv.
##Licence: Zenodo API for the record, "license": {"id": "cc-zero"} (CC0 1.0), checked
##2026-10-01. (The deposit is the paper's authors'. Project FeederWatch's own terms were not
##checked; the CC0 dedication is the authors'.)
##
##The agents are species, not individual birds: each row is one reported displacement of a
##bird of one species by a bird of another. One row per displacement, in source order.
##agent_a = source (the displacing species), agent_b = target (the displaced species), so
##winner is always "agent_a". The file has no date, observer or location. homefield is
##blank.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/4997232")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
f <- file.path(cache, "forDryad.csv")
if (!file.exists(f))
  download.file("https://zenodo.org/api/records/4997232/files/forDryad.csv/content", f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "5c24794dce2908ae32c9d72fec8cb86a")
x <- read.csv(f, stringsAsFactors = FALSE)

df <- data.frame(agent_a = x$source, agent_b = x$target, homefield = "", winner = "agent_a")
stopifnot(!anyNA(df), df$agent_a != df$agent_b)
out <- "feederwatch_species_displacements.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "displacements,", length(unique(c(df$agent_a, df$agent_b))), "species\n")
