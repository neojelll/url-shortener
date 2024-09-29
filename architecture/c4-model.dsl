workspace {

    model {

        User = person "User" "URL Shortener user" 

        SoftwareSystem = softwareSystem "URL Shortener" "Shorten URLs\nRedirect URLs" {

            Api = container "API Gateway" "Handles and routes HTTP requests" "FastAPI"

            EventBus = container "EventBus" "Handles event routing and delivery\nProcesses URL generation requests" "Kafka" {
                tags "EventBusForm"
            }

            AnalyticsService = container "AnalyticsService" "Track usage\nGenerate reports" "Python"

            AnalyticsDB = container "AnalyticsDatabase" "Stores usage data" "Prometheus" {
                tags "DatabaseForm"
            }

            BackEnd = container "URL Shortener Service" "Shorten URLs\nRedirect URLs" "Python"
            Cache = container "URL Cache" "Stored frequently requested URLs" "Redis"

            DataBase = container "URL DataBase" "Stores original and shortened URLs\nStores expiration" "PostrgeSQL" {
                tags "DatabaseForm"
            }

            ExpirationManager = container "Expiration Manager" "Checks for expired URLs in URL Database\nRemoves them" "Python"
            FirstExternalSystem = container "Telegram Bot" {
                tags "ExternalSystem"
            }

            SecondExternalSystem = container "WebUI" {
                tags "ExternalSystem"
            }
            

            User -> FirstExternalSystem "uses"
            User -> SecondExternalSystem "uses"
            FirstExternalSystem -> Api "sending data"
            SecondExternalSystem -> Api "sending data"
            Api -> EventBus "sending data"
            Api -> DataBase "try to request long url from db cache"
            Api -> Cache "try to request long url from db cache"
            EventBus -> AnalyticsService "sending data"
            EventBus -> BackEnd "sending data"
            AnalyticsService -> AnalyticsDB "select data"
            BackEnd -> DataBase "retrieving or writing data"
            BackEnd -> Cache "checking the cache for the necessary data"
            ExpirationManager -> DataBase "select data"

        }
    }

    views {

        systemContext SoftwareSystem {
            include *
            autolayout tb
        } 
        
        container SoftwareSystem {
            include *
            autolayout tb
        }
        

        styles {

            element "Element" {
                color white
            }

            element "Person" {
                background #0d1701
                shape Person
                stroke white
                metadata False
                strokeWidth 4
            }

            element "Software System" {
                shape RoundedBox
                background #244003
                stroke white
                metadata False
                strokeWidth 4
            }

            element "ExternalSystem" {
                shape Box
                background #2e3329
                shape WebBrowser
            }

            element "Container" {
                shape RoundedBox
                background #244003
                stroke white
                strokeWidth 4
            }

            element "DatabaseForm" {
                shape cylinder
            }
            
            element "EventBusForm" {
                shape pipe
            }

        }
        
    }

}