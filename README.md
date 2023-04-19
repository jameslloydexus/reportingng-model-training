# ailabs-templates-spring-boot

[![OpenJDK](https://img.shields.io/badge/Java-17-blue.svg?logo=openjdk)](https://openjdk.org/)
[![Apache Maven](https://img.shields.io/badge/Maven-3.8.5-blue.svg?logo=apachemaven)](https://maven.apache.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2.7.4-brightgreen.svg?logo=springboot)](https://spring.io/projects/spring-boot/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-FAB040.svg?logo=precommit)](https://pre-commit.com/)
[![Quality Gate Status](https://sonarqube-ailabs.exus.co.uk/api/project_badges/measure?project=uk.co.exus.templates%3Aspring-boot-template&metric=alert_status&token=squ_3a84c523e94a46c3d5b6e58fe4f3b6d79f5e575f)](https://sonarqube-ailabs.exus.co.uk/dashboard?id=uk.co.exus.templates%3Aspring-boot-template)
[![CI](https://github.com/EXUS-AI-Labs/ailabs-templates-spring-boot/actions/workflows/master.yml/badge.svg)](https://github.com/EXUS-AI-Labs/ailabs-templates-spring-boot/actions)

A template for Spring Boot applications.

## Description

This repository can be optionally used as a template when creating new
repositories in GitHub for Spring Boot applications.
It contains the following:

* Maven project
  * Source code (`src` directory)
  * Project Object Model (`pom.xml`)
* `.gitignore`
* `.gitattributes`
* `Dockerfile`
* `build.sh` that may be used locally to build the Docker image
* GitHub Action workflows in `.github/workflows` directory
* Jenkins pipelines in `Jenkinsfile`

Any of the above contents may be kept, removed or modified.

## build.sh

The `build.sh` file is a [bash](https://www.gnu.org/software/bash/) script
which builds the application and optionally performs some additional steps.
By default, this script searches for
[Maven settings](https://maven.apache.org/settings.html) at `/~.m2/settings.xml`
and mounts them as a secret during the build stage. You may point to a different
Maven settings file via the `MAVEN_SETTINGS` environment variable
(e.g. `MAVEN_SETTINGS=.github/workflows/settings.xml`).

To simply build the application using [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
execute the script.

To run SonarScanner plugin for Maven and post the results on SonarQube make sure that
you have properly configured Maven settings as described in
[SonarQube Docs](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner-for-maven/).
To enable this make sure that you have set the `POST_SONARQUBE` environment variable
to `true` (i.e. `POST_SONARQUBE=true`).

Also, you may push the image to a Docker registry by setting the `PUSH` environment variable
to `true` (i.e. `PUSH=true`). You may push several tags for the same image by setting the
`PUSH_EXTRA_TAGS` environment variable (e.g. `PUSH_EXTRA_TAGS="0.0.1 latest"`). By default,
the script uses the [AI Labs' Harbor](https://harbor-ailabs.exus.co.uk) Docker registry.
You may override it via the `DOCKER_REGISTRY_URL` environment variable.
Make sure that you have logged in to the Docker registry if it requires authentication.

### Requirements

Before executing the script, make sure that the following have been installed:

* [mandatory] Docker with [Buildx plugin](https://github.com/docker/buildx).
* [optional] Maven installation.
If Maven installation is missing then Maven commands will be executed in a Docker container.

## GitHub Actions

The GitHub Actions worfklows perform the following steps:

* When `dev` branch is pushed:
  * Runs [pre-commit](https://pre-commit.com/)
  * Builds the Docker image
  * Pushes the Docker image in a Docker registry
    * Tags the image with the version found in `pom.xml`
    * Optionally creates an additional tag (e.g. `dev`)
* When `master` branch is pushed:
  * Runs [pre-commit](https://pre-commit.com/)
  * Builds the Docker image
  * Analyzes code with [SonarScanner](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
    and posts the results to [AI Labs' SonarQube](https://sonarqube-ailabs.exus.co.uk)
  * Pushes the Docker image in a Docker registry
    * Tags the image with the version found in `pom.xml`
    * Optionally creates an additional tag (e.g. `dev`)
  * Creates a git tag with the version found in `pom.xml`
    * The tag is overwritten if it already exists
* When any other branch is pushed:
  * Runs [pre-commit](https://pre-commit.com/)
  * Builds the Docker image

### GitHub Actions secrets

The following secrets shall be set:

* NEXUS_USERNAME
* NEXUS_PASSWORD
* HARBOR_USERNAME
* HARBOR_PASSWORD
* SONARQUBE_TOKEN

## Jenkins

The Jenkins pipelines perform the following steps:

* Runs [pre-commit](https://pre-commit.com/)
* Builds the Docker image
* Analyzes code with [SonarScanner](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
and posts the results to [AI Labs' SonarQube](https://sonarqube-ailabs.exus.co.uk)
* Pushes the Docker image in a Docker registry
  * Tags the image with the version found in `pom.xml`
  * Optionally creates an additional tag (e.g. `dev`)

### Jenkins credentials

The following credentials shall be set:

* nexus-username (secret text)
* nexus-password (secret text)
* harbor-username (secret text)
* harbor-password (secret text)
* sonarqube-token (secret text)

## CI Requirements

For GitHub Actions worfklows and Jenkins pipelines to succeed,
the following requirements shall be satisfied:

* pre-commit configuration file exists in the root directory (`.pre-commit-config.yaml`)
* A Maven project exists in the root directory (`pom.xml` and `src`)
* A `Dockerfile` exists
* `build.sh` exists
* The name of the repo has a prefix with the project name and a dash
  (e.g. andromeda-ewe, ailabs-templates-spring-boot).
* [AI Labs' Harbor](https://harbor-ailabs.exus.co.uk) has a corresponding
  project in place.
