FROM nginx
COPY . /usr/share/nginx/html
WORKDIR /usr/share/nginx/html
RUN apt update && apt install -y python python-pip python-dev-all python-numpy python-pandas
RUN pip install -r requirements.txt
RUN python metaprojects_report.py

