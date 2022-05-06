pipeline {
    agent { label 'small' }
    environment {
      imagename_dev = "registry-gitlab.indocresearch.org/pilot/service_dataops_utility"
      imagename_staging = "registry-gitlab.indocresearch.org/pilot/service_dataops_utility"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-gitlab-registry'
      dockerImage = ''
    }

    stages {
    stage('Git clone for dev') {
        when {branch "k8s-dev"}
        steps{
          script {
            git branch: "k8s-dev",
              url: 'https://git.indocresearch.org/pilot/service_dataops_utility.git',
              credentialsId: 'lzhao'
          }
        }
    }

    stage('DEV: Run unit tests') {
        when { branch 'k8s-dev' }
        steps {
            withCredentials([
                usernamePassword(credentialsId: 'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD'),
                string(credentialsId:'VAULT_TOKEN', variable: 'VAULT_TOKEN'),
                string(credentialsId:'VAULT_URL', variable: 'VAULT_URL'),
                file(credentialsId:'VAULT_CRT', variable: 'VAULT_CRT')
            ]) {
                sh """
                pip install --user poetry==1.1.12
                ${HOME}/.local/bin/poetry config virtualenvs.in-project true
                ${HOME}/.local/bin/poetry config http-basic.pilot ${PIP_USERNAME} ${PIP_PASSWORD}
                ${HOME}/.local/bin/poetry install --no-root --no-interaction
                ${HOME}/.local/bin/poetry run pytest --verbose -c tests/pytest.ini
                """
            }
        }
    }

    stage('DEV Build and push image') {
      when {branch "k8s-dev"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
                docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                    customImage = docker.build("registry-gitlab.indocresearch.org/pilot/service_dataops_utility:${env.commit}", "--build-arg PIP_USERNAME=${PIP_USERNAME} --build-arg PIP_PASSWORD=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 .")
                    customImage.push()
                }
            }
        }
      }
    }
    stage('DEV Remove image') {
      when {branch "k8s-dev"}
      steps{
        sh "docker rmi $imagename_dev:$commit"
      }
    }

    stage('DEV Deploy') {
      when {branch "k8s-dev"}
      steps{
      build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
        [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
        [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'dataops-utility' ],
        [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
    ])
      }
    }

    stage('Git clone staging') {
        when {branch "k8s-staging"}
        steps{
          script {
          git branch: "k8s-staging",
              url: 'https://git.indocresearch.org/pilot/service_dataops_utility.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push image') {
      when {branch "k8s-staging"}
      steps{
        script {
            withCredentials([usernamePassword(credentialsId:'readonly', usernameVariable: 'PIP_USERNAME', passwordVariable: 'PIP_PASSWORD')]) {
                docker.withRegistry('https://registry-gitlab.indocresearch.org', registryCredential) {
                    customImage = docker.build("registry-gitlab.indocresearch.org/pilot/service_dataops_utility:${env.commit}", "--build-arg PIP_USERNAME=${PIP_USERNAME} --build-arg PIP_PASSWORD=${PIP_PASSWORD} --add-host git.indocresearch.org:10.4.3.151 .")
                    customImage.push()
                }
            }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "k8s-staging"}
      steps{
        sh "docker rmi $imagename_staging:$commit"
      }
    }

    stage('STAGING Deploy') {
      when {branch "k8s-staging"}
      steps{
      build(job: "/VRE-IaC/Staging-UpdateAppVersion", parameters: [
        [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'staging' ],
        [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'dataops-utility' ],
        [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
    ])
      }
    }
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} ${env.commit}  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }
}
