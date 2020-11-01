FROM python:3-slim-buster
RUN apt-get -qq update

RUN apt-get -qq install -y git g++ gcc autoconf automake \
    m4 libtool qt4-qmake make libqt4-dev libcurl4-openssl-dev \
    libcrypto++-dev libsqlite3-dev libc-ares-dev \
    libsodium-dev libnautilus-extension-dev \
    libssl-dev libfreeimage-dev swig

# Installing mega sdk python binding
ENV MEGA_SDK_VERSION '3.7.4'
RUN git clone https://github.com/meganz/sdk.git sdk && cd sdk &&\
    git checkout v$MEGA_SDK_VERSION && ./autogen.sh && \
    ./configure --disable-silent-rules --enable-python --disable-examples && \
    make -j$(nproc --all) && cd bindings/python/ && \
    python3 setup.py bdist_wheel && cd dist/ && \
    pip3 install --no-cache-dir megasdk-$MEGA_SDK_VERSION-*.whl

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN apt-get -qq update && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    apt-add-repository non-free && \
    apt-get -qq update && \
    apt-get -qq install -y p7zip-full p7zip-rar aria2 curl pv jq ffmpeg locales python3-lxml && \
    apt-get purge -y software-properties-common
    
COPY requirements.txt .
COPY extract /usr/local/bin
RUN chmod +x /usr/local/bin/extract
RUN pip3 install --no-cache-dir -r requirements.txt
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
COPY . .
RUN chmod +x aria.sh

CMD ["bash","start.sh"]
