from diagrams import Diagram
from diagrams.c4 import (
    Person,
    Container,
    Relationship,
    SystemBoundary,
    System,
    Database,
)


graph_attr = {
    'splines': 'spline',
}


file_path = '/Users/timofei/My_Project/architecture/diagrams/container-diagram'


with Diagram(filename=file_path, show=False, direction='TB', graph_attr=graph_attr):
    user = Person(
        name='URL Shortener user',
        description='user who wants to shorten the URL',
    )

    curl = System(
        name='curl',
        description='utility for sending [HTTP] requests, the user will need to directly interact with the URL Shortener API',
        external=True,
    )

    with SystemBoundary('URL Shortener'):
        telegram_bot = System(
            name='Telegram Bot',
            description='Telegram bot for a user-friendly interface for using URL Shortener',
            external=True,
        )

        with SystemBoundary('Containers'):
            api = Container(
                name='APIGateway',
                technology='FastAPI',
                description='Handles and routes [HTTP] requests\nRedirect URLs',
            )

            broker = Container(
                name='Message Queue',
                technology='Kafka',
                description='Handles event routing and delivery\nProcesses URL generation requests',
            )

            shortener_service = Container(
                name='Shortener Service',
                technology='Python',
                description='Shorten URLs',
            )

            database = Database(
                name='Databse',
                technology='PostgreSQL',
                description='Stores original and shortened URLs\nStores expiration',
            )

            cache = Container(
                name='Cache',
                technology='Redis',
                description='Stored frequently requested URLs',
            )

            expiration_manager = Container(
                name='Expiration Manager',
                technology='Python',
                description='Checks for expired URLs in URL Database\nRemoves them',
            )

        (
            user
            >> Relationship('Uses URL Shortener', style='bold')
            << telegram_bot
            >> Relationship('sending long URL')
            << api
        )

        (
            user
            >> Relationship('Uses URL Shortener', style='bold')
            << curl
            >> Relationship('sending long URL')
            << api
            >> Relationship('sending long URL in topic and consume long URL for topic')
            << broker
        )

        api >> Relationship('try to request long url from db cache') << database

        api >> Relationship('try to request long url from db cache') << cache

        (
            broker
            >> Relationship('consume long URL for topic and send short URL in topic')
            << shortener_service
        )

        (
            shortener_service
            >> Relationship('create records with long URL, short URL, expiration')
            >> database
            << Relationship('deleted continue expirated URLs')
            << expiration_manager
        )

        (
            shortener_service
            >> Relationship('create records and checking the short URL for existence')
            << cache
        )
        