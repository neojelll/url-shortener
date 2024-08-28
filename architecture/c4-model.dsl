workspace {

    model {
        user = person "User" 
        S1 = softwareSystem "cUrl" {
            tags S1
        }
        S2 = softwareSystem "Tg Bot" {
            tags S1
        }
        S = softwareSystem "Url Shortener" {
            api = container "API" 
            EventBus = container "EventBus"
            AnalyticsServer = container "AnalyticsServer"
            AnalyticsDB = container "AnalyticsDB" {
                tags "AnalyticsDataBase"
            }
            BackEnd = container "BackEnd"
            cache = container "cache"
            DataBase = container "DataBase" {
                tags "DataBase"
            }
            
            S1 -> api "sending request"
            S2 -> api "sending request"
            api -> EventBus "sending data"
            EventBus -> AnalyticsServer "sending data"
            EventBus -> AnalyticsDB "retrieving or writing data"
            EventBus -> BackEnd "sending data"
            BackEnd -> DataBase "retrieving or writing data"
            BackEnd -> cache "checking the cache for the necessary data"
        }
        user -> S1 "Uses"
        user -> S2 "Uses"
        S1 -> S "sending requests"
        S2 -> S "sending requests"
    }

    views {
        dynamic * {
            user -> S1
            user -> S2
            S1 -> S
            S2 -> S
            autolayout tb
        } 
        
        container S {
            include *
            autolayout tb
        }
        
        styles {
            element "Element" {
                color white
            }
            element "Software System" {
                background #9c9c06
            }
            element "S1" {
                background #aa98a9
            }
            element "Person" {
                background #6b5802
                shape person
            }
            element "Container" {
                background #b8b804
            }
            element "DataBase" {
                shape cylinder
            }
            element "AnalyticsDataBase" {
                shape cylinder
            }
        }
        
        theme default
    }

}