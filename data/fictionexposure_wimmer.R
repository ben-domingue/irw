# fictionexposure_wimmer: Author Recognition Test (Wimmer & Ferguson, 2023,
# Behav Res 55, 103-134; OSF ytudn, AssessmentFictionExposure.sav).
# Items are the ART's authors (Business1.., Domestic1.., ..., Suspense25)
# and its 40 foils (FOILS1..FOILS40); resp = 1 if ticked, 0 if not.
# Selected by name (irw#2506 follow-up, 2026-10-05). The build had taken
# positions 3:200 of the two-valued columns, which dropped FOILS1 (ticked by
# 4 of 337). FOILS31 is still left out: nobody ticked it.
library(foreign)
x <- read.spss("AssessmentFictionExposure.sav", to.data.frame = TRUE)
art <- grep("^(Business|Domestic|Foreign|PhilosophyPsychology|Romance|SciFiFantasy|Science|SelfHelp|SocialPoliticalCommentary|Suspense|FOILS)[0-9]+$",
            names(x), value = TRUE)
stopifnot(length(art) == 200)
art <- art[sapply(x[art], function(v) length(unique(v)) == 2)]  # drops FOILS31 (constant)
z <- x[, art]
for (i in 1:ncol(z)) z[, i] <- ifelse(z[, i] == 0, 0, 1)
x <- z

id <- 1:nrow(x)
L <- list()
for (i in 1:ncol(x)) L[[i]] <- data.frame(id = id, item = names(x)[i], resp = x[, i])
df <- data.frame(do.call("rbind", L))
write.csv(df, "fictionexposure_wimmer.csv", row.names = FALSE)
