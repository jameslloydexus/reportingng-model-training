pipeline {
    agent any

    environment {
        MS_TEAMS_WEBHOOK = 'https://exodusgr.webhook.office.com/webhookb2/a7bf68fb-c785-41b8-a949-96d43cc1db36@c93840a1-e2d5-4283-a50f-0f380d5c6bbe/JenkinsCI/f5bdd1153cef477e8e96d19276c684a0/46ac2356-009c-4125-9672-fd086c8256c7'
    }

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('pre-commit') {
            steps {
                precommit()
            }
        }
        stage('build-master') {
            when {
                branch 'master'
            }
            environment {
                MAVEN_SETTINGS = '.github/workflows/settings.xml'
                MAVEN_USERNAME = credentials('nexus-username')
                MAVEN_PASSWORD = credentials('nexus-password')
                MAVEN_REPO_ID = 'repo-id'
                POST_SONARQUBE = 'true'
                SONAR_URL = 'https://sonarqube-ailabs.exus.co.uk'
                SONAR_TOKEN = credentials('sonarqube-token')
                PUSH = 'true'
                DOCKER_REGISTRY_URL = 'harbor-ailabs.exus.co.uk'
                PUSH_EXTRA_TAGS = 'latest'
            }
            steps {
                withDockerRegistry([credentialsId: 'harbor', url: 'https://harbor-ailabs.exus.co.uk']) {
                    sh './build.sh'
                }
            }
        }
        stage('build-dev') {
            when {
                branch 'dev'
            }
            environment {
                MAVEN_SETTINGS = '.github/workflows/settings.xml'
                MAVEN_USERNAME = credentials('nexus-username')
                MAVEN_PASSWORD = credentials('nexus-password')
                MAVEN_REPO_ID = 'repo-id'
                POST_SONARQUBE = 'false'
                SONAR_URL = 'https://sonarqube-ailabs.exus.co.uk'
                SONAR_TOKEN = credentials('sonarqube-token')
                PUSH = 'true'
                DOCKER_REGISTRY_URL = 'harbor-ailabs.exus.co.uk'
                PUSH_EXTRA_TAGS = 'dev'
            }
            steps {
                withDockerRegistry([credentialsId: 'harbor', url: 'https://harbor-ailabs.exus.co.uk']) {
                    sh './build.sh'
                }
            }
        }
    }

    post {
        always {
            sendEmailNotification()
            sendOffice365Notification(env.MS_TEAMS_WEBHOOK)
        }
    }
}
