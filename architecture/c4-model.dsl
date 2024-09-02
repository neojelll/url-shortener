workspace {

    model {

        User = person "User" "URL Shortener user" 

        SoftwareSystem = softwareSystem "URL Shortener" "Shorten URLs\nRedirect URLs" {

            Api = container "API Gateway" "Handles and routes HTTP requests" "FastAPI"

            EventBus = container "EventBus" "Handles event routing and delivery\nProcesses URL generation requests" "Kafka"

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
                background #52327a
                shape Person
                stroke white
                metadata False
            }

            element "Software System" {
                shape RoundedBox
                background #8000ff
                stroke white
                metadata False
            }

            element "ExternalSystem" {
                shape Box
                background #b094d6
            }

            element "Container" {
                shape RoundedBox
                background #8000ff
                stroke white
            }

            element "DatabaseForm" {
                shape cylinder
                icon "icons/Database.png"
            }

        }
        
    }

}