FROM odoo:19.0

USER root

RUN pip install --break-system-packages --no-cache-dir pdfplumber>=0.11

USER odoo
