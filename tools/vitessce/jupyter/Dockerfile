FROM jupyter/datascience-notebook:latest

USER root
# Installation des dépendances pour les images et les widgets
RUN apt-get update && apt-get install -y libblosc-dev && apt-get clean
USER ${NB_UID}

RUN pip install --no-cache-dir \
    vitessce[all] \
    jupyter-server-proxy \
    ipywidgets \
    zarr \
    anndata \
    'lamindb[bionty]'