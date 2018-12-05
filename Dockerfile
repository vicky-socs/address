FROM address-service:base-latest
ADD latest.tar .
ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION
EXPOSE 5000
CMD ["python","api.py"]
