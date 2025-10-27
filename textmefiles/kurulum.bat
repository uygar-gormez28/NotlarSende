@echo off
REM -------------------------------------------
REM  kur.bat — Proje Kökünü Bulup Kurulum Yapar
REM -------------------------------------------

REM 1) Betiğin bulunduğu dizini al
set "SCRIPT_DIR=%~dp0"

REM 2) Proje kökü: bir seviye yukarı
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM 3) Kök dizine geç
cd /d "%PROJECT_ROOT%"

REM 4) Kullanıcıdan onay iste
echo.
echo Kurulumu baslatmak istediginize emin misiniz? (Y/N)
choice /C YN /N /M "Lutfen tuslayin"
if errorlevel 2 (
  echo.
  echo Kurulum iptal edildi.
  pause
  exit /b
)

echo.
echo 💡 '%PROJECT_ROOT%' dizininde kurulum baslatiliyor...
echo.

REM 5) Python kontolü
where python >nul 2>&1
if errorlevel 1 (
  echo Python bulunamadi! Lutfen Python 3 yukleyin.
  pause
  exit /b 1
)

REM 6) virtualenv klasörü varsa atla, yoksa oluştur
if not exist venv (
  echo ✅ Virtualenv oluşturuluyor...
  python -m venv venv
) else (
  echo 🔄 Virtualenv zaten mevcut, atlanıyor.
)

REM 7) Etkinleştir
echo.
echo 🔌 Virtualenv etkinlestiriliyor...
call venv\Scripts\activate

REM 8) Gereksinimleri yükle
if exist requirements.txt (
  echo.
  echo 📦 requirements.txt'den paketler yukleniyor...
  pip install -r requirements.txt
) else (
  echo.
  echo 📦 Flask yukleniyor...
  pip install flask
)

echo.
echo 🎉 Kurulum tamamlandi! Virtualenv içindeki paketler yüklendi.
pause
