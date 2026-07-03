# Usa uma imagem Python leve
FROM python:3.9-slim

# Instala dependências do sistema necessárias para o pyarrow
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas o requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências de uma só vez
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código da aplicação
COPY . .

# Expõe a porta do Streamlit
EXPOSE 8501

# Comando para rodar o app
CMD ["streamlit", "run", "dsa_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
