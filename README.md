# MapBuilder

The code in this repo pulls together information from Chicago and NYC Open Data Portals as well as the Yelp API. For each neighborhood in Chicago and NYC, a separate API call to Yelp is made based on longitude and latitude. The Yelp search returns up to 48 businesses (categories include restaurants, other food-related businesses, transportation, and health) per neighorhood. The Yelp business data is then merged with reformatted library and school data from the Chicago and NYC Open Data Portal as well as the SNAP/EBT dataset which comes from the U.S. Department of Agriculture website. 

Hosted on [JKAN](https://sun-kev.github.io/jkan/)

Built by [Kevin Sun](https://github.com/Sun-Kev) and [Natasha Mathur](https://github.com/natashamathur)
