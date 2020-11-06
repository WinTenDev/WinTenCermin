FROM goldsaja/megasdk-winten:latest

COPY requirements.txt .
COPY extract /usr/local/bin
RUN chmod +x /usr/local/bin/extract
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x aria.sh

CMD ["bash","start.sh"]
