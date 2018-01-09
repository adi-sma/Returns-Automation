library(grid)
library(gridExtra)
library(ggplot2)
library(reshape2)

RETURNS_DATA_PATH = "/home/sma-analytics/Data/Returns/returns_data.txt"
SAVE_PATH = "/home/sma-analytics/Data/Returns/"

ret_data <- read.table(RETURNS_DATA_PATH, sep = "\t", colClasses = "character", header = T)


table_plot_ret<-function(plot,title,n="",freq,type)
{
  
  plot$Date <- as.Date(plot$Date)
  for (ix in 2:ncol(plot)){
    plot[,ix] <- as.numeric(plot[,ix])
  }
  
  
  dailyret <- plot
  dailyret2<-data.frame()
  dailyret2<-data.frame(`S-Score`=colnames(dailyret[2:ncol(dailyret)]),Return=scales::percent(freq*colMeans(dailyret[2:ncol(dailyret)],na.rm=T)))
  
  for(i in 2:ncol(dailyret))
  {
    dailyret2$Vol[i-1]<-scales::percent(sqrt(freq)*sd(dailyret[,i],na.rm = T))
    dailyret2$Sharpe[i-1]<-round(sqrt(freq)*(mean(dailyret[,i],na.rm = T)/sd(dailyret[,i],na.rm = T)),2)
  }
  colnames(dailyret2)[1]<-"S-Score"
  
  for (ix in 2:ncol(plot)){
    plot[,ix] <- cumprod(plot[,ix] + 1) - 1
  }

  breaks<-paste0(round(nrow(plot)/freq,0)," months")
  if (nrow(plot)<freq)
  breaks<-paste0(round(freq/7,0)," days")
  
  if(ncol(plot)==4){colors=c("red","black","yellowgreen")
  sizes=c(1,0.5,0.5)}
  if(ncol(plot)==5){colors=c("red","black","yellowgreen","navyblue")
  sizes=c(1,0.5,0.5,0.5)}
  if(ncol(plot)==6){colors=c("red","purple","yellowgreen","navyblue","black")
  sizes=c(0.5,0.5,0.5,0.5,1)}
  if(ncol(plot)==7){colors=c("red","purple","blue","orange","yellowgreen","black")
  sizes=c(0.5,0.5,0.5,0.5,0.5,1)}
 
  lsplot<- melt(plot, id.vars="Date")
  lplot<-ggplot(data=lsplot, aes(x=Date, y=value,group=variable,color=variable,size=variable)) +
    geom_line()+
    ggtitle(paste0("Cumulative ",type," Returns \n Eq. Wt. ",title," ",n," \n ",plot$Date[1]," to ", plot$Date[nrow(plot)]))+
    labs(x="Date",y="Cumulative Returns (in %)") +
    scale_x_date(date_labels = "%m/%Y",date_breaks = breaks )+
    theme(axis.text.x = element_text(angle = 270, hjust = 1),legend.position="bottom", legend.title = element_blank(), plot.title = element_text(hjust=0.5))+
    scale_y_continuous(labels = scales::percent,breaks = seq(min(plot[2:ncol(plot)]),max(plot[2:ncol(plot)]),0.1*(max(plot[2:ncol(plot)])-min(plot[2:ncol(plot)]))))+
    scale_color_manual(values=colors)+ scale_size_manual(values=sizes)
  
  th<-ttheme_default(base_size = 7)
  
  return(arrangeGrob(lplot, tableGrob(dailyret2,rows=NULL,theme = th), nrow=2, as.table=T, heights=c(3,1)))
}


colnames(ret_data) <- c("Date", "S-Score < -2", "SPY", "S-Score > 2", "LongShort")

#Full History
ret <- ret_data
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'FullHistory_LS.png'), p, units = "in", width=10, height=6.75)

#Full History (Long Only)
ret <- ret[c("Date", "S-Score < -2", "SPY", "S-Score > 2")]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'FullHistory_Long.png'), p, units = "in", width=10, height=6.75)


max_date <- max(ret_data$Date)



#Rolling 1 Year
prev_year <- paste0(as.character(as.numeric(substring(max_date, 1, 4)) - 1), substring(max_date, 5, 10))
ret <- ret_data[ret_data$Date > prev_year, ]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'Rolling_LS.png'), p, units = "in", width=10, height=6.75)

#Rolling 1 Year (Long Only)
ret <- ret[c("Date", "S-Score < -2", "SPY", "S-Score > 2")]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'Rolling_Long.png'), p, units = "in", width=10, height=6.75)

#2016 to Current
ret <- ret_data[ret_data$Date >= 2016, ]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, '2016plus_LS.png'), p, units = "in", width=10, height=6.75)

#2016 to Current (Long Only)
ret <- ret[c("Date", "S-Score < -2", "SPY", "S-Score > 2")]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, '2016plus_Long.png'), p, units = "in", width=10, height=6.75)

#YTD
ret <- ret_data[ret_data$Date >= paste(substr(max_date, 1, 4), "01-01", sep="-"),]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'YTD_LS.png'), p, units = "in", width=10, height=6.75)

#YTD (Long Only)
ret <- ret[c("Date", "S-Score < -2", "SPY", "S-Score > 2")]
p <- table_plot_ret(ret, "Twitter Derived 09:10 AM Sentiment", n="", 252, "OC")
ggsave(paste0(SAVE_PATH, 'YTD_Long.png'), p, units = "in", width=10, height=6.75)

