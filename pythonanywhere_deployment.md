# PythonAnywhere'de Uygulama Yayınlama Kılavuzu

Bu kılavuz, Python Pro Level Instructor Exam uygulamasını [PythonAnywhere](https://www.pythonanywhere.com/) üzerinde yayınlama adımlarını içerir.

## 1. PythonAnywhere Hesabı Oluşturma

1. [PythonAnywhere](https://www.pythonanywhere.com/) adresine gidin ve bir hesap oluşturun (ücretsiz hesap yeterli olacaktır).
2. Hesap oluşturduktan sonra kontrol paneline erişin.

## 2. Kod Yükleme

### GitHub Üzerinden Kodu Yükleme (Tercih Edilen Yöntem)

1. PythonAnywhere kontrol panelinde "Bash Console" seçin ve açın.
2. Konsolda şu komutu çalıştırın:
   ```bash
   git clone https://github.com/KULLANICI_ADI/chatbotpy.git
   ```
   (GitHub repository URL'nizi kullanın)

### Manuel Olarak Dosya Yükleme (Alternatif)

1. PythonAnywhere kontrol panelinde "Files" sekmesine gidin.
2. Kod dosyalarını yerel bilgisayarınızdan yükleyin veya zip olarak yükleyip çıkartın.

## 3. Sanal Ortam Oluşturma

1. PythonAnywhere konsolunda, aşağıdaki komutları çalıştırın:
   ```bash
   cd chatbotpy
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 4. Web Uygulaması Oluşturma

1. PythonAnywhere kontrol panelinde "Web" sekmesine gidin.
2. "Add a new web app" düğmesine tıklayın.
3. Prompta yanıt olarak "Next" tıklayın ve "Manual Configuration" seçin.
4. Python sürümünü seçin (Python 3.8+ önerilir).
5. WSGI yapılandırma dosyasını aşağıdaki içerikle güncelleyin:
   ```python
   import sys
   import os
   
   # Proje yolunuzu buraya ekleyin
   path = '/home/KULLANICI_ADI/chatbotpy'
   if path not in sys.path:
       sys.path.append(path)
   
   from run import app as application
   ```
   (KULLANICI_ADI'nızı PythonAnywhere kullanıcı adınızla değiştirin)

## 5. Uygulama Yapılandırması

1. PythonAnywhere kontrol panelinde "Web" sekmesinde, web uygulamanızı seçin.
2. "Virtualenv" bölümünde, oluşturduğunuz sanal ortamın yolunu belirtin:
   ```
   /home/KULLANICI_ADI/chatbotpy/venv
   ```
3. "Static Files" bölümünde, statik dosyaların URL ve dizin yapılandırmasını ekleyin:
   ```
   URL: /static/
   Directory: /home/KULLANICI_ADI/chatbotpy/app/static
   ```

## 6. Veritabanı Hazırlama

1. PythonAnywhere konsolunda şu komutları çalıştırın:
   ```bash
   cd chatbotpy
   source venv/bin/activate
   python -c "from app import create_app; from app.models.models import db; app = create_app(); app.app_context().push(); db.create_all()"
   python -m app.models.seed_data
   ```

## 7. Uygulamayı Başlatma

1. PythonAnywhere kontrol panelinde "Web" sekmesine gidin.
2. "Reload" düğmesine tıklayarak web uygulamanızı yeniden başlatın.
3. Uygulama URL'nizi açın (genellikle `http://KULLANICI_ADI.pythonanywhere.com` şeklindedir).

## 8. Sorun Giderme

Eğer uygulamanız düzgün çalışmıyorsa, şu adımları izleyin:

1. PythonAnywhere kontrol panelinde "Web" sekmesinde "Error log" bağlantısına tıklayın.
2. Log dosyasını inceleyin ve hataları tespit edin.
3. Yaygın hatalar şunları içerir:
   - Yanlış yol yapılandırması
   - Eksik bağımlılıklar
   - Yanlış izinler
   - Veritabanı bağlantı sorunları

## 9. Ücretsiz Hesap Kısıtlamaları

PythonAnywhere'ın ücretsiz hesapları bazı kısıtlamalara sahiptir:

1. Günlük CPU ve I/O sınırlamaları
2. Yalnızca belirli bir alt etki alanı kullanılabilir
3. Uygulamanız belirli bir süre kullanılmazsa uyku moduna geçebilir

Eğer uygulamanızı daha fazla kullanıcı için hizmet verecek şekilde ölçeklendirmek istiyorsanız, ücretli bir plan düşünebilirsiniz. 