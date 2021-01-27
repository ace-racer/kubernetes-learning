FROM python:3.6
EXPOSE 8501
WORKDIR /app

RUN mkdir -p dashboard
COPY requirements.txt ./requirements.txt
COPY dashboard/*.py dashboard/
COPY Indian_MF_generic_dashboard.py ./Indian_MF_generic_dashboard.py

RUN pip3 install -r requirements.txt
RUN ls
CMD streamlit run Indian_MF_generic_dashboard.py