library(randomForest)
library(caret)

data <- read.csv(file = "/Users/hyunsukbang/Desktop/Personal/Project/lol_data.csv")
data <- subset(data, select=-c(teamId, gameDuration))
data <- na.omit(data)


#split data into two sets (70% for training and 30% for testing)
part <- createDataPartition(data$win, p= 0.7)
idx <- as.vector(part[[1]])
train <- data[idx, ]
test <- data[-idx,]

train$win <- as.character(train$win)
train$win <- as.factor(train$win)
test$win <- as.character(test$win)
test$win <- as.factor(test$win)

sum(train$win == 'True')
sum(train$win == 'False')
sum(test$win == 'True')
sum(test$win == 'False')

learn_model <- function(train_set, ntree.param, mtry.param){
  model <- randomForest (
    win~.,
    method = "class",
    ntree = ntree.param,
    mtry = mtry.param,
    data = train_set)
  model
}

get_results <- function(model, pred, test){
  a <- confusionMatrix(pred, as.factor(test$win))
  num.tree <- model$ntree
  mtry.param <- model$mtry
  
  a
  
  acc <- a$overall[1] #accuracy
  error <- 1.0 - acc
  sens <- a$byClass[1] #sensitivity
  spec <- a$byClass[2] #Specificty
  prec <- a$byClass[5] #Precision
  bal.acc <- a$byClass[11] #balanced Accurary
  
  oob <- mean(model$err.rate[,1])
  
  results.df <- data.frame(ntree=num.tree,
                           mtry = mtry.param,
                           acc = acc,
                           bal.acc = bal.acc,
                           error = error,
                           spec = spec,
                           sens = sens,
                           prec = prec,
                           oob = oob)
  rm(a)
  results.df
}

ntree.range <- c(250, 500, 750, 1000, 2000)
mtry.range <- c(sqrt(12), sqrt(12)+1, sqrt(12)+2, sqrt(12)+3)
results.df <- data.frame(ntree=0,
                         mtry=0,
                         acc=0,
                         bal.acc=0,
                         error=0,
                         spec=0,
                         sens=0,
                         prec=0,
                         oob=0)
model_list <- c()
model <- NULL
  
for (i in ntree.range){
  for (j in mtry.range){
    str <- paste(Sys.time(), ": Starting model training on", i, "trees, and",
                 floor(j), "attributes.\n")
    cat(str)
    model <- NULL
    model <- learn_model(train, i, j)
    model_list = c(model_list, model)
    str <- paste(Sys.time(), ": Done.\n")
    cat(str)
    
    pred <- predict(model, newdata = test, type= "class")
    tmp.df <- get_results(model, pred, test)
    results.df <- rbind(results.df, tmp.df)
    rm(tmp.df)
  }
}



rownames(results.df) <- c()
results.df <- results.df[-1, ] # Remove the first row (used to prime the frame)
results.df <- round(results.df, 3)
results.df

prt <- function(result){
  str <- paste("\nGrid search resulted in the best model at ntree =", result$ntree, 
               "and mtry =", result$mtry, ".\n")
  cat(str)
  str<- paste("Accuracy =", result$acc,
              "\nBalanced Accuracy =", result$bal.acc,
              "\nSensitivty =", result$sens,
              "\nSpecificity =", result$spec,
              "\n OOB=", result$oob,
              "\n---------------------------------------------")
  cat(str)
}
max_bal.acc <- results.df[which.max(results.df$bal.acc),]
prt(max_bal.acc)
min_obb <- results.df[which.min(results.df$oob),]
prt(min_obb)

importance(model)
varImpPlot(model)
confusionMatrix(pred, test$win)


