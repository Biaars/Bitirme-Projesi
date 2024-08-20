class Config:
    DEBUG = False
    SECRET_KEY = 'your_secret_key'
    # Diğer yapılandırma ayarlarını buraya ekleyebilirsiniz

class DevelopmentConfig(Config):
    DEBUG = True
    # Geliştirme ortamı için özel yapılandırma ayarlarını buraya ekleyebilirsiniz

class ProductionConfig(Config):
    DEBUG = False
    # Üretim ortamı için özel yapılandırma ayarlarını buraya ekleyebilirsiniz
