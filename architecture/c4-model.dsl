workspace {

    model {
        user = person "User" "Url Shortener user"
        S1 = softwareSystem "cUrl" "external system" {
            tags S1
        }
        S2 = softwareSystem "Tg Bot" "external system" {
            tags S1
        }
        S = softwareSystem "Url Shortener" "Shorten URLs\nRedirect URLs" {
            api = container "API" "Handles and routes HTTP requests" "FastAPI"
            EventBus = container "EventBus" "Handles event routing and delivery\nProcesses URL generation requests" "Kafka"
            AnalyticsServer = container "AnalyticsServer" "Track usage\nGenerate reports"
            AnalyticsDB = container "AnalyticsDatabase" "Stores usage data" "Prometheus" {
                tags "AnalyticsDataBase"
            }
            BackEnd = container "BackEnd"
            cache = container "Cache" "Stored frequently requested URLs" "Redis"
            DataBase = container " Url DataBase" "Stores original and shortened URLs\nStores expiration" "PostrgeSQL" {
                tags "DataBase"
            }
            ExpirationManager = container "Expiration Manager" "Checks for expired URLs in URL Database\nRemoves them"
            
            S1 -> api "sending request"
            S2 -> api "sending request"
            api -> EventBus "sending data"
            EventBus -> AnalyticsServer "sending data"
            EventBus -> AnalyticsDB "retrieving or writing data"
            EventBus -> BackEnd "sending data"
            EventBus -> ExpirationManager "sending data"
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
                background #8000ff
            }
            element "S1" {
                background #b094d6
            }
            element "Person" {
                background #52327a
                shape person
            }
            element "Container" {
                background #8000ff
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