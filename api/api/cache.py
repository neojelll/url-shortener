from redis import Redis


class Cache(object):
	def __init__(self):
		self.cache = Redis(
    		host='localhost',
    		port=6379,
    		db=0,# Номер базы данных (по умолчанию 0)
    		decode_responses=True# Автоматически декодировать байтовые строки в строки
    		)
		
	async def check(self, short_url):
		if self.cache.exists(short_url):
			return self.cache.get(short_url)
		else:
			return None
	
	async def set(self, short_url, long_url):
		self.cache.set(short_url, long_url)

	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.cache.close()
