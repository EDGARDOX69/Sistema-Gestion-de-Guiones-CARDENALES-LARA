name: Pruebas de Aceptación (Gestión de Tareas y Tareas Asignadas)

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  aceptacion:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping -h 127.0.0.1 -proot"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
          --sql-mode=""

    env:
      FLASK_ENV: testing
      CAPTCHA_ENABLED: "0"
      DB_HOST: 127.0.0.1
      DB_PORT: "3306"
      DB_USER: root
      DB_PASSWORD: root
      DB_NAME: estadio_db_test
      DB_SEGURIDAD_NAME: seguridad_db_test
      APP_URL: http://127.0.0.1:5001

    steps:
      - name: 1. Descargar código
        uses: actions/checkout@v4

      - name: 2. Configurar Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: 3. Instalar dependencias y Playwright
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          pip install pytest pytest-playwright
          playwright install chromium --with-deps

      - name: 4. Crear e importar bases de datos de prueba desde la raíz
        env:
          MYSQL_PWD: root
        run: |
          mysql -h 127.0.0.1 -u root -e "CREATE DATABASE IF NOT EXISTS estadio_db_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
          mysql -h 127.0.0.1 -u root -e "CREATE DATABASE IF NOT EXISTS seguridad_db_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
          mysql -h 127.0.0.1 -u root estadio_db_test -e "SET SESSION sql_mode = ''; SOURCE estadio_db_test.sql;"
          mysql -h 127.0.0.1 -u root seguridad_db_test -e "SET SESSION sql_mode = ''; SOURCE seguridad_db_test.sql;"

      - name: 5. Levantar servidor Flask + SocketIO en segundo plano
        run: |
          python -c "from app import create_app, socketio; app = create_app(); socketio.run(app, debug=False, host='127.0.0.1', port=5001, use_reloader=False, allow_unsafe_werkzeug=True)" > /tmp/flask_test.log 2>&1 &
          for i in $(seq 1 30); do
            if curl -sf http://127.0.0.1:5001/auth/login > /dev/null; then
              echo "Servidor listo en http://127.0.0.1:5001"
              break
            fi
            sleep 1
          done

      - name: 6. Ejecutar Pruebas de Aceptación
        run: pytest test/aceptacion/ -v
