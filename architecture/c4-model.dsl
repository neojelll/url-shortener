workspace {

    model {
        User = person "User" "URL Shortener user"
        FirstExternalSystem = softwareSystem "cURL" "external system" {
            tags "ExternalSystemColor"
        }
        SecondExternalSystem = softwareSystem "Telegram Bot" "external system" {
            tags "ExternalSystemColor"
        }
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
            
            FirstExternalSystem -> Api "sending request"
            SecondExternalSystem -> Api "sending request"
            Api -> EventBus "sending data"
            EventBus -> AnalyticsService "sending data"
            EventBus -> AnalyticsDB "retrieving or writing data"
            EventBus -> BackEnd "sending data"
            AnalyticsService -> AnalyticsDB "select data"
            BackEnd -> DataBase "retrieving or writing data"
            BackEnd -> Cache "checking the cache for the necessary data"
            ExpirationManager -> DataBase "sending data"
        }
        User -> FirstExternalSystem "uses"
        User -> SecondExternalSystem "uses"
        FirstExternalSystem -> SoftwareSystem "sending requests"
        SecondExternalSystem -> SoftwareSystem "sending requests"
    }

    views {
        dynamic * {
            User -> FirstExternalSystem "uses"
            User -> SecondExternalSystem "uses"
            FirstExternalSystem -> SoftwareSystem "sending requests"
            SecondExternalSystem -> SoftwareSystem "sending requests"
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
                shape person
            }

            element "Software System" {
                background #8000ff
            }

            element "ExternalSystemColor" {
                background #b094d6
            }

            element "Container" {
                background #8000ff
            }

            element "DatabaseForm" {
                shape cylinder
            }

        }
        
        theme default
    }

}