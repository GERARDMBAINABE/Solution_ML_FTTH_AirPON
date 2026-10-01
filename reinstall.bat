@echo off
echo ============================================
echo  Reinstallation FTTH AirPON ML
echo  Correction incompatibilite scikit-learn
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Suppression ancien environnement...
if exist .venv rmdir /s /q .venv
if exist venv  rmdir /s /q venv

echo [2/4] Creation nouvel environnement...
python -m venv .venv

echo [3/4] Installation des dependances...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install scikit-learn==1.6.1 --quiet
pip install streamlit pandas joblib plotly --quiet

echo [4/4] Verification...
python -c "import sklearn; print('scikit-learn:', sklearn.__version__)"
python -c "import streamlit; print('streamlit:', streamlit.__version__)"
python -c "import joblib; print('joblib:', joblib.__version__)"

echo.
echo ============================================
echo  Installation terminee !
echo  Lancement de l'application...
echo ============================================
echo.
streamlit run app\streamlit_app.py
pause
