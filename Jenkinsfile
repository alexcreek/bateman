pipeline {
  agent any
  stages {
    stage('Test') {
      agent {
        dockerfile true
      }
      steps {
        sh 'make test'
        junit testResults: 'reports/pytest.xml', skipPublishingChecks: true
        recordIssues tool: pyLint(pattern: 'reports/pylint.log'), enabledForFailure: true, skipPublishingChecks: true
        cleanWs()
      }
    }
    stage('Build') {
      steps {
        script {
          def image = docker.build("192.168.1.10:4000/bateman:latest")
          image.tag("$GIT_BRANCH")
          image.push("latest")
          image.push("$GIT_BRANCH")
        }
      }
    }
  }
  post {
    always {
      cleanWs()
    }
  }
}
