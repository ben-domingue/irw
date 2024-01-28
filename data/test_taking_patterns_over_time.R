#Read original data
data <- read.csv('FE_1933_2006_data.csv', header = TRUE, sep = ';')

###### Group 1 ######
#Get all group 1 data
data_group1 <- data[1:889,]

#ordering data in ascending ID number
data_by_id1 <- data_group1[with(data_group1, order(data_group1$X607), decreasing = FALSE),]

#create 'id' column
id_group1 <- as.data.frame(rep(paste0('A.', data_by_id1$X607), 284))

#create 'subtest' column
subnames_group1 <- as.data.frame(rep(c('A1', 'A2', 'A3', 'A4', 
                                       'B1', 'B2', 'B3', 'B4', 'B5'),
                                     times = c(14224, 17780, 21336, 35560, 
                                               19558, 35560, 35560, 28448, 44450)))

#create 'item' column
subtest_nums1 <- c(paste0('A1.', 1:16), paste0('A2.', 1:20), paste0('A3.', 1:24), paste0('A4.', 1:40), 
                 paste0('B1.', 1:22), paste0('B2.', 1:40), paste0('B3.', 1:40), paste0('B4.', 1:32), paste0('B5.', 1:50))
item_num_group1 <- as.data.frame(rep(subtest_nums1, each = 889))

#create 'resp' column
resp_data_total1 <- data.frame()

for (i in 6:292){
  if (i %in% c(106:108)) next
  resp_data1 <- data.frame(data_by_id1[i])
  colnames(resp_data1) <- c('resp')
  resp_data_total1 <- rbind(resp_data_total1, resp_data1)
}

#combine columns together and output the data file
final_group1 <- cbind(item_num_group1, id_group1, resp_data_total1, subnames_group1)
colnames(final_group1) <- c('item', 'id', 'resp', 'subtest')
final_group1$resp[final_group1$resp == c(-9, 9)] <- NA
write.csv(final_group1, file = 'Form 1934-36.csv', row.names = FALSE)

###### Group 2 ######
data_group2 <- data[890:1802,]

data_by_id2 <- data_group2[with(data_group2, order(data_group2$X607), decreasing = FALSE),]

#create 'ID' column
id_group2 <- as.data.frame(rep(paste0('B.', data_by_id2$X607), 284))

#create 'subtest' column
subnames_group2 <- as.data.frame(rep(c('A1', 'A2', 'A3', 'A4', 
                                       'B1', 'B2', 'B3', 'B4', 'B5'),
                                     times = c(14608, 18260, 21912, 36520, 
                                               20086, 36520, 36520, 29216, 45650)))

#create 'Item' column
subtest_nums2 <- c(paste0('A1.', 1:16), paste0('A2.', 1:20), paste0('A3.', 1:24), paste0('A4.', 1:40), 
                 paste0('B1.', 1:22), paste0('B2.', 1:40), paste0('B3.', 1:40), paste0('B4.', 1:32), paste0('B5.', 1:50))
item_num_group2 <- as.data.frame(rep(subtest_nums2, each = 913))


#create 'Resp' column
resp_data_total2 <- data.frame()

for (i in 6:292){
  if (i %in% c(106:108)) next
  resp_data2 <- data.frame(data_by_id2[i])
  colnames(resp_data2) <- c('resp')
  resp_data_total2 <- rbind(resp_data_total2, resp_data2)
}             

#combine columns together and output the data file
final_group2 <- cbind(item_num_group2, id_group2, resp_data_total2, subnames_group2)
colnames(final_group2) <- c('item', 'id', 'resp', 'subtest')
final_group2$resp[final_group2$resp == c(-9, 9)] <- NA
write.csv(final_group2, file = 'Form 2006.csv', row.names = FALSE)

######Put Group 1 & 2 together######
#bind group 1 & 2
overall_data <- rbind(final_group1, final_group2)

#create group name
group_name <- as.data.frame(rep(c('1', '2'), times = c(252476, 259292)))

#add group name and output the data set
output_final <- cbind(group_name, overall_data)
colnames(output_final) <- c('form', 'item', 'id', 'resp', 'subtest')
write.csv(output_final, file = 'Changes in test-taking patterns over time.csv', row.names = FALSE)
