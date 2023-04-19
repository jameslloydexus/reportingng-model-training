#!/bin/bash
set -eux

trap "rm -f TAG" EXIT INT

CI=${CI:-false}
GIT_SUFFIX=.git
REPO_NAME=$(basename "$(git remote get-url origin)")
IMAGE_NAME=${REPO_NAME%"$GIT_SUFFIX"}
PROJECT_NAME=$(cut -d '-' -f1 <<<"${IMAGE_NAME}")

if ! command -V mvn; then
    IMAGE_TAG=${IMAGE_TAG:-$(
        docker run \
            --rm \
            -v "$(pwd):/app" \
            -w "/app" \
            maven:3.8.5-openjdk-17 \
            mvn -q help:evaluate -Dexpression=project.version -Doutput=TAG
        cat TAG
    )}
else
    IMAGE_TAG=${IMAGE_TAG:-$(
        mvn -q help:evaluate -Dexpression=project.version -Doutput=TAG
        cat TAG
    )}
fi

MAVEN_SETTINGS=${MAVEN_SETTINGS:-${HOME}/.m2/settings.xml}
MAVEN_GOAL=${MAVEN_GOAL:-"clean package"}

SONAR_URL=${SONAR_URL:-https://sonarqube-ailabs.exus.co.uk}
POST_SONARQUBE=${POST_SONARQUBE:-false}
if [[ "${POST_SONARQUBE}" == "true" ]]; then
    MAVEN_GOAL="${MAVEN_GOAL} org.sonarsource.scanner.maven:sonar-maven-plugin:sonar"
fi

PUSH=${PUSH:-false}
DOCKER_REGISTRY_URL=${DOCKER_REGISTRY_URL:-harbor-ailabs.exus.co.uk}
PUSH_EXTRA_TAGS=${PUSH_EXTRA_TAGS:-}

BUILDX_BUILD_CACHE_ARGS=""
if [[ "${CI}" == "true" ]]; then
    echo "Running in GitHub Actions..."
    BUILDX_BUILD_CACHE_ARGS=(
        "--cache-from"
        "type=gha"
        "--cache-to"
        "type=gha"
    )
fi

# shellcheck disable=SC2068
MAVEN_USERNAME=${MAVEN_USERNAME:-} \
    MAVEN_PASSWORD=${MAVEN_PASSWORD:-} \
    MAVEN_REPO_ID=${MAVEN_REPO_ID:-} \
    SONAR_URL="${SONAR_URL}" \
    SONAR_TOKEN=${SONAR_TOKEN:-} \
    docker buildx build \
    --pull \
    --build-arg MAVEN_GOAL="${MAVEN_GOAL}" \
    --secret id=maven,src="${MAVEN_SETTINGS}" \
    --secret id=MAVEN_USERNAME \
    --secret id=MAVEN_PASSWORD \
    --secret id=MAVEN_REPO_ID \
    --secret id=SONAR_URL \
    --secret id=SONAR_TOKEN \
    --tag "${DOCKER_REGISTRY_URL}/${PROJECT_NAME}/${IMAGE_NAME}:${IMAGE_TAG}" \
    --load \
    ${BUILDX_BUILD_CACHE_ARGS[@]} \
    .

if [[ "${PUSH}" == "true" ]]; then
    echo "Pushing to Docker registry..."
    docker push "${DOCKER_REGISTRY_URL}/${PROJECT_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

    for tag in $PUSH_EXTRA_TAGS; do
        docker tag \
            "${DOCKER_REGISTRY_URL}/${PROJECT_NAME}/${IMAGE_NAME}:${IMAGE_TAG}" \
            "${DOCKER_REGISTRY_URL}/${PROJECT_NAME}/${IMAGE_NAME}:${tag}"
        docker push "${DOCKER_REGISTRY_URL}/${PROJECT_NAME}/${IMAGE_NAME}:${tag}"
    done
fi
