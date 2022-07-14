pipeline {
    agent { label 'small' }
    environment {
      imagename = "ghcr.io/pilotdataplatform/dataops"  
      imagename_staging = "ghcr.io/pilotdataplatform/dataops"
      commit = sh(returnStdout: true, script: 'git describe --always').trim()
      registryCredential = 'pilot-ghcr'
      dockerImage = ''
    }

    stages {
    stage('Git clone for dev') {
        when {branch "develop"}
        steps{
          script {
            git branch: "develop",
              url: 'https://github.com/PilotDataPlatform/dataops.git',
              credentialsId: 'lzhao'
          }
        }
    }

    stage('DEV Build and push image') {
      when {branch "develop"}
      steps{
        script {
                docker.withRegistry('https://ghcr.io', registryCredential) {
                    customImage = docker.build('$imagename:alembic-$commit', '--target alembic-image .')
                    customImage.push()
                }
                docker.withRegistry('https://ghcr.io', registryCredential) {
                    customImage = docker.build('$imagename:dataops-$commit', '--target dataops-image .')
                    customImage.push()
                }
        }
      }
    }
    stage('DEV Remove image') {
      when {branch "develop"}
      steps{
        sh 'docker rmi $imagename:alembic-$commit'
        sh 'docker rmi $imagename:dataops-$commit'
      }
    }

    stage('DEV Deploy') {
      when {branch "develop"}
      steps{
      build(job: "/VRE-IaC/UpdateAppVersion", parameters: [
        [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'dev' ],
        [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'dataops-utility' ],
        [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
    ])
      }
    }
/**
    stage('Git clone staging') {
        when {branch "main"}
        steps{
          script {
          git branch: "main",
              url: 'https://github.com/PilotDataPlatform/dataops.git',
              credentialsId: 'lzhao'
            }
        }
    }

    stage('STAGING Building and push image') {
      when {branch "main"}
      steps{
        script {
                docker.withRegistry('https://ghcr.io', registryCredential) {
                    customImage = docker.build("$imagename_staging:${env.commit}", ".")
                    customImage.push()
                }
        }
      }
    }

    stage('STAGING Remove image') {
      when {branch "main"}
      steps{
        sh "docker rmi $imagename_staging:$commit"
      }
    }

    stage('STAGING Deploy') {
      when {branch "main"}
      steps{
      build(job: "/VRE-IaC/Staging-UpdateAppVersion", parameters: [
        [$class: 'StringParameterValue', name: 'TF_TARGET_ENV', value: 'staging' ],
        [$class: 'StringParameterValue', name: 'TARGET_RELEASE', value: 'dataops-utility' ],
        [$class: 'StringParameterValue', name: 'NEW_APP_VERSION', value: "$commit" ]
    ])
      }
    }
**/
  }
  post {
      failure {
        slackSend color: '#FF0000', message: "Build Failed! - ${env.JOB_NAME} ${env.commit}  (<${env.BUILD_URL}|Open>)", channel: 'jenkins-dev-staging-monitor'
      }
  }
}
