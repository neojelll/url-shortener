from diagrams import Diagram
from diagrams.c4 import Person, Container, Relationship, SystemBoundary, System, Database


graph_attr = {
	"splines": "spline",
}


with Diagram(show=False, direction='TB', graph_attr=graph_attr):
	user = Person(
		name='User for URL Shortener',
	)

	curl = System(
			name='curl',
			description='',
			external=True
		)


	with SystemBoundary('URL Shortener'):
		telegram_bot = System(
			name='Telegram Bot',
			description='',
			external=True,
		)


		with SystemBoundary('Containers'):
			api = Container(
				name='APIGateway',
				technology='FastAPI',
				description='Handles and routes [HTTP] requests',
			)

			broker = Container(
				name='Message Queue',
				technology='Kafka',
				description='Handles event routing and delivery\nProcesses URL generation requests',
			)

			shortener_service = Container(
				name='Shortener Service',
				technology='Python',
				description='Shorten URLs\nRedirect URLs',
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

			analytics_service = Container(
				name='Analytics Service',
				technology='Python',
				description='Track usage\nGenerate reports',
			)

			analytics_database = Container(
				name='Analytics Database',
				technology='Prometheus',
				description='Stores usage data'
			)


		user >> Relationship('Uses URL Shortener') << telegram_bot \
		>> Relationship('sending data') << api

		user >> Relationship('Uses URL Shortener') << curl \
		>> Relationship('sending data') << api \
		>> Relationship('sending data') << broker

		api >> Relationship('try to request long url from db cache') << database

		api >> Relationship('try to request long url from db cache') << cache

		broker >> Relationship('sending data') << shortener_service

		shortener_service >> Relationship('retrieving or writing data') << database \
		>> Relationship('deleted continue expirated URLs') << expiration_manager

		shortener_service >> Relationship('checking the cache for the necessary data') << cache

		broker >> Relationship('sending data') << analytics_service \
		>> Relationship('select data') << analytics_database
