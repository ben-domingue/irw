## nbashots_sim: simulated NBA-style shot data (trials in which respondents choose their trials)
##
## Stand-in for the NBA.com shot data (e.g., github.com/DomSamangy/NBA_Shots_04_23), which
## carry no license and can't be redistributed; see data/trials/nba_shots.R. Nothing here is
## read from those data. The zone make rates and shot mix are set by hand to resemble
## published league-wide figures from recent NBA seasons.
##
## The point of the table: shooters choose their shots, and better shooters choose harder
## ones. Raw accuracy therefore mixes skill with shot selection. Each shooter's true skill is
## in cov_true_theta, so an analysis can check what adjusting for the shot recovers.
##
## Model, for shot j by shooter i:
##   theta_i ~ N(0, 0.35^2)                         shooting skill, logits
##   role_i in {big, wing, guard}                   sets baseline shot preferences
##   zone_ij ~ multinomial logit, a[role, z] + g[z]*theta_i   better shooters take more
##                                                            midrange and threes
##   dist_ij drawn within the zone's range
##   logit P(make) = theta_i + alpha[z] - 0.08*(dist - zone mean dist) - 0.25*late
##   late = shot in the last 2 minutes of a quarter; better shooters take more of these

set.seed(20260926)

n_players <- 400
roles <- c("big", "wing", "guard")
zones <- c("restricted_area", "paint", "midrange", "corner_three", "above_break_three")

## shooters
role <- sample(roles, n_players, replace = TRUE, prob = c(0.3, 0.4, 0.3))
theta <- rnorm(n_players, 0, 0.35)
## better shooters get more shots
n_shots <- rnbinom(n_players, mu = exp(log(330) + 0.8 * theta), size = 4)
n_shots <- pmax(n_shots, 20)

## zone choice: baseline log-odds vs. the restricted area, by role
a <- rbind(
    big   = c(0,  -0.4, -1.0, -3.0, -2.5),
    wing  = c(0,  -1.0, -0.5,  -0.9,  0.3),
    guard = c(0,  -1.1, -0.4, -1.5,  0.4)
)
colnames(a) <- zones
g <- c(0, 0.3, 1.2, 1.8, 2.0) # skill -> harder shots

## make rates: zone intercepts (logits, at theta = 0)
alpha <- c(restricted_area = 0.55, paint = -0.35, midrange = -0.40,
           corner_three = -0.55, above_break_three = -0.72)

## distance (feet from the hoop) within each zone
draw_dist <- function(zone) {
    n <- length(zone)
    d <- numeric(n)
    k <- zone == "restricted_area";   d[k] <- runif(sum(k), 0, 4)
    k <- zone == "paint";             d[k] <- runif(sum(k), 4, 14)
    k <- zone == "midrange";          d[k] <- runif(sum(k), 8, 23)
    k <- zone == "corner_three";      d[k] <- runif(sum(k), 22, 23.5)
    k <- zone == "above_break_three"; d[k] <- 23.75 + rexp(sum(k), 1 / 2)
    d
}
zone_mean_dist <- c(restricted_area = 2, paint = 9, midrange = 15.5,
                    corner_three = 22.75, above_break_three = 25.75)

L <- list()
for (i in 1:n_players) {
    n <- n_shots[i]
    u <- a[role[i], ] + g * theta[i]
    p <- exp(u) / sum(exp(u))
    zone <- sample(zones, n, replace = TRUE, prob = p)
    dist <- draw_dist(zone)
    ## court location: hoop at (0, 0); x is sideline to sideline, y toward half court
    ang <- runif(n, 0, pi)
    ang[zone == "corner_three"] <- sample(c(0.05, pi - 0.05), sum(zone == "corner_three"), replace = TRUE)
    locx <- dist * cos(ang)
    locy <- dist * sin(ang)
    ## game clock, minutes elapsed (0-48); better shooters take more late shots
    late <- rbinom(n, 1, plogis(qlogis(2 / 12) + 1.0 * theta[i]))
    quarter <- sample(1:4, n, replace = TRUE)
    in_q <- ifelse(late == 1, runif(n, 10, 12), runif(n, 0, 10))
    gameclock <- 12 * (quarter - 1) + in_q
    eta <- theta[i] + alpha[zone] - 0.08 * (dist - zone_mean_dist[zone]) - 0.25 * late
    resp <- rbinom(n, 1, plogis(eta))
    L[[i]] <- data.frame(id = i, item = zone, resp = resp,
                         cov_role = role[i], cov_true_theta = round(theta[i], 4),
                         trial_number = 1:n,
                         trial_dist = round(dist, 1), trial_locx = round(locx, 1),
                         trial_locy = round(locy, 1), trial_three = as.integer(grepl("three", zone)),
                         trial_gameclock = round(gameclock, 2), trial_late = late)
}
df <- do.call("rbind", L)
rownames(df) <- NULL

write.csv(df, file = "nbashots_sim.csv", quote = FALSE, row.names = FALSE)
