# Sirve el explorador (un único HTML estático) con nginx.
# El HTML se genera con el pipeline (python run_pipeline.py) y está versionado
# en outputs/explorador.html; la imagen no corre Python.
FROM nginx:1.27-alpine

COPY outputs/explorador.html /usr/share/nginx/html/index.html

EXPOSE 80
