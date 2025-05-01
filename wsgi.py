import sys
import os

# Proje yolunuzu buraya ekleyin
path = '/home/KULLANICI_ADI/chatbotpy'
if path not in sys.path:
    sys.path.append(path)

# Ortam değişkenlerini yapılandırma
from dotenv import load_dotenv
dotenv_path = os.path.join(path, '.env')
load_dotenv(dotenv_path)

# Flask uygulamasını içe aktarma
from run import app as application

# WSGI sunucusu bunu otomatik olarak algılayacaktır 