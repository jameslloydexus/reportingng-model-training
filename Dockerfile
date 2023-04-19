# syntax=docker/dockerfile:1.4
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY ./pom.xml ./pom.xml
COPY ./src ./src
ARG MAVEN_GOAL="clean package"
RUN --mount=type=secret,id=maven,target=/app/settings.xml,required=true \
    --mount=type=secret,id=MAVEN_USERNAME,required=false \
    --mount=type=secret,id=MAVEN_PASSWORD,required=false \
    --mount=type=secret,id=MAVEN_REPO_ID,required=false \
    --mount=type=secret,id=SONAR_URL,required=false \
    --mount=type=secret,id=SONAR_TOKEN,required=false \
    --mount=type=cache,target=/root/.m2/ \
    MAVEN_USERNAME=$(if [ -f /run/secrets/MAVEN_USERNAME ]; then cat /run/secrets/MAVEN_USERNAME; fi)\
    MAVEN_PASSWORD=$(if [ -f /run/secrets/MAVEN_PASSWORD ]; then cat /run/secrets/MAVEN_PASSWORD; fi)\
    MAVEN_REPO_ID=$(if [ -f /run/secrets/MAVEN_REPO_ID ]; then cat /run/secrets/MAVEN_REPO_ID; fi) \
    SONAR_URL=$(if [ -f /run/secrets/SONAR_URL ]; then cat /run/secrets/SONAR_URL; fi) \
    SONAR_TOKEN=$(if [ -f /run/secrets/SONAR_TOKEN ]; then cat /run/secrets/SONAR_TOKEN; fi) \
    mvn --batch-mode --update-snapshots --settings /app/settings.xml ${MAVEN_GOAL}
RUN mvn -q help:evaluate -Dexpression=project.version -Doutput=VERSION && \
    mvn -q help:evaluate -Dexpression=project.artifactId -Doutput=ARTIFACT_ID && \
    cp "/app/target/$(cat ARTIFACT_ID)-$(cat VERSION).jar" /app/target/app.jar

FROM eclipse-temurin:17-jre-alpine as run
# hadolint ignore=DL3018
RUN set -eu && \
    apk update && \
    apk add --no-cache tini && \
    rm -rf /var/cache/apk/* && \
    tini --version

ARG USER=notroot
RUN adduser -D ${USER}
WORKDIR /home/${USER}
USER ${USER}

COPY --chown=${USER}:${USER} --from=build /app/target/app.jar .

# https://github.com/krallin/tini#remapping-exit-codes
ENTRYPOINT ["tini", "-e", "143", "--", "java", "-jar", "app.jar"]
