require(dplyr)

input_fp <- 'Seattle_Police_Department_Police_Report_Incident.csv'

seattle_df <- read.csv( file = input_fp, stringsAsFactors = F )

# look at a quick summary of the data
glimpse( seattle_df )

"
from glimpse, there are two fields which seem useful to easily discern homicides:
Office.Type and Summarized.Offense.Description

It looks like Summarized.Offense.Description is more coarse, so let's see what
the fields are
"
unique( seattle_df$Summarized.Offense.Description )

"
We see that 'HOMICIDE' is one of the descriptors in Summarized.Offense.Description,
so we will collect all events with this description
"
seattle_homicides <- subset( seattle_df, Summarized.Offense.Description == 'HOMICIDE' )

# let's look at this new df again
glimpse( seattle_homicides )

"
The column Offense.Type no further stratifies into types, since
we've pulled out only homicides, this will have a homicide type
associated. It is possible that Offense.Code is an even better
choice for stratifying by type, so let's look at each to see if they
match
"
unique( seattle_homicides$Offense.Type )
unique( seattle_homicides$Offense.Code )

"
it's clear from this that Offense.Type is better for stratifying homicides
by type. It appears that we could get the same information from considering
both Offense.Code along with Offense.Code.Extension, but that's extra work
we don't need to do. For example, it seems that Offense.Code = 911 always
refers to premeditated with gun, but 999 with extension 5 is neg-mans-gun
(ostensibly: neglect or manslaughter involving a firearm) whereas 999 with 
extension 6 is premeditated using bodyforce. 
"
seattle_homicides$Offense.Code[c(1,2,25)]
seattle_homicides$Offense.Code.Extension[c(1,2,25)]
seattle_homicides$Offense.Type[c(1,2,25)]

# create the homicide counts
# change the character date format to a date object
seattle_homicides$Date <- as.POSIXlt( seattle_homicides$Date.Reported, 
                                      tz="America/Los_Angeles",
                                      format = '%m/%d/%Y %H:%M' )

# get the year and month
yr <- function( date ){
     # date$year gives years since 1900
     return( date$year + 1900 )
}
mn <- function( date ){
     # january is indexed as 0, so need to add 1
     # this is a really stupid convention, IMO
     return( date$mon + 1 )
}

"
It seems that for date objects, using apply methods isn't
great... I'd really like to write 
seattle_homicides$year <- sapply( seattle_homicides, FUN = yr )
but this doesn't work because of the way POSIXlt is stored...
Will use a less efficient for loop in the following functions
"

get_years <- function( dates ){
     years <- integer()
     for( i in seq_along(dates) ){
          years <- c(years, yr( dates[i] ) )
     }
     return( years )
}
get_months <- function( dates ){
     months <- integer()
     for( i in seq_along(dates) ){
          months <- c(months, mn( dates[i] ) )
     }
     return( months )
}

# create year and month columns for easy grouping
seattle_homicides$year <- get_years( seattle_homicides$Date )
seattle_homicides$month <- get_months( seattle_homicides$Date )

# groupby year, month, and homicide type
seattle_hcnts <- seattle_homicides %>% 
                 select(year, month, Offense.Type) %>% 
                 group_by( year, month, homicide_type = Offense.Type ) %>% 
                 dplyr::summarise( counts = n() )

# add city and state
seattle_hcnts$city <- 'seattle'
seattle_hcnts$state <- 'washington'

# add ucr_homicide (blank for now)
seattle_hcnts$ucr_homicide <- ''

# sort rows nicely by year and month
seattle_hcnts <- seattle_hcnts[ order(seattle_hcnts$year, seattle_hcnts$month), ]

# save as csv
output_fp <- paste0( substr(input_fp, 1, nchar(input_fp) - 4), '_homicide_counts.csv')
write.csv( seattle_hcnts, file = output_fp, row.names = F )
