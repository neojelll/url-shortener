workspace {

    model {
        user = person "User" 
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
            
            api -> EventBus
            EventBus -> AnalyticsServer
            EventBus -> AnalyticsDB
            EventBus -> BackEnd
            BackEnd -> DataBase
            BackEnd -> cache
        }
        user -> S "Uses"
    }

    views {
        systemContext S {
            include *
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
                background #2D882D
            }
            element "Person" {
                background #116611
                shape person
            }
            element "Container" {
                background #55aa55
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