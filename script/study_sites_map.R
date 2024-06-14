library(data.table)
library(leaflet)

df <- fread("ignore/study_sites.csv")

df[, c('Longitude', 'Latitude', 'Dummy') := tstrsplit(Coord, ',', fixed = TRUE)]

df[, Longitude := as.numeric(Longitude)]
df[, Latitude := as.numeric(Latitude)]
df$Dummy <- NULL
df$Coord <- NULL

df[, NodeID := .I]

study_area_icons <- iconList(
    Southwest = makeIcon(iconUrl = "https://maps.google.com/mapfiles/ms/icons/red-dot.png"),
    Kierland = makeIcon(iconUrl = "https://maps.google.com/mapfiles/ms/icons/green-dot.png"),
    Thomas = makeIcon(iconUrl = "https://maps.google.com/mapfiles/ms/icons/blue-dot.png")
)

leaflet(df) %>%
    addTiles() %>%
    addMarkers(
        lng = ~Longitude, lat = ~Latitude,
        icon = ~study_area_icons[`Study Area`],
        label = ~paste("Node:", Node, "<br>Study Area:", `Study Area`)
    )
