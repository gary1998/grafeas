  pipeline {
    parameters {
      // A boolean parameter that governs whether or not stages will get executed, based on the e2e status.
      booleanParam(defaultValue: true, description: 'Execute pipeline?', name: 'shouldBuild')
    }

    // Constants.
    environment {
      JENKINSBOT = credentials("${JENKINSBOT_GHE_ACCESS_TOKEN}")
      DEVELOPMENT_DOCKER_TOKEN = credentials("${security_advisor_docker_token_dev}")
      PRODUCTION_DOCKER_TOKEN = credentials("${security_advisor_docker_token_prod}")
      iamConfig = credentials("security-advisor-iamconfig-dev")
      root_cert = credentials("${cloudcerts_root_cert}")
      tls_cert = credentials("${cloudcerts_tls_cert}")
      tls_key = credentials("${cloudcerts_tls_key}")
      kafkaSaslUsername = credentials("security_advisor_kafka_username")
      kafkaSaslPassword = credentials("security_advisor_kafka_password")
      redis_auth = credentials("${cloudcerts_redis_auth_dev}")
      xforceToken = credentials("security-advisor-xforce-token")
      GRAFEAS_URL = credentials("security_advisor_cloudant_url_dev")
      GRAFEAS_USERNAME = credentials("security_advisor_cloudant_username_dev")
      GRAFEAS_PASSWORD = credentials("security_advisor_cloudant_password_dev")
      IAM_BEARER_TOKEN = credentials("security_advisor_iam_bearer_token_dev")
      IAM_API_BASE_URL = credentials("security_advisor_iam_api_base_url_dev")
      IAM_API_KEY = credentials("security_advisor_iam_api_key_dev")
      IAM_BASE_URL = credentials("security_advisor_iam_base_url")
    }

    // Defines which build machines group is used.
    agent {
      label 'security_advisor'
    }

    // Pipeline options.
    options {
      ansiColor('xterm')
      skipDefaultCheckout()
      disableConcurrentBuilds()
      buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
      // Verify e2e status is green before starting the job.
      // stage ("Check for E2E Status") {
      //   steps {
      //     script {
      //       STAGE_NAME = "Check for E2E Status"
      //
      //       sh "curl -H 'Authorization: token $JENKINSBOT_PSW' -H 'Accept: application/vnd.github.v3.raw' https://github.ibm.com/api/v3/repos/security-services/security-advisor-devops/contents/e2e-status.txt?ref=master > e2e-status.txt"
      //
      //       def e2eStatus = readFile('e2e-status.txt').trim()
      //       if (e2eStatus == "red") {
      //         currentBuild.result = "FAILURE"
      //         env.shouldBuild = "false"
      //         slackSend (color: '#F01717', message: "@channel *$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER> disabled due to e2e failure.")
      //       }
      //     }
      //   }
      // }

      stage ("Checkout SCM") {
        when {
          expression {
            return env.shouldBuild != "false"
          }
        }

        steps {
          script {
            STAGE_NAME = "Checkout SCM"

            checkout scm

            // Check for "[ci skip]" in the git log. If exists then skip the build.
            result = sh (script: "git log -1 | grep '.*\\[ci skip\\].*'", returnStatus: true)
            if (result == 0) {
              echo ("This build should be skipped. Aborting.")
              currentBuild.result = "SUCCESS"
              env.shouldBuild = "false"
            }
          }
        }
      }

      stage ("Setup") {
        when {
          expression {
            return env.shouldBuild != "false"
          }
        }

        steps {
          script {
            STAGE_NAME = "Setup"

            // Get the current repository name.
            if (JOB_NAME.contains("/")) {
              // This is a PR, the job name is a bit different, e.g. security-advisor-ingest-api/PR-2.
              str = JOB_NAME.split("/")
              repositoryName = str[0]
            } else {
              repositoryName = JOB_NAME
            }

            // Obtain the name of the current micro-service being built.
            file = findFiles(glob: '**/values.yaml')
            values = readYaml file: "${file[0].path}"
            microServiceName = values.global.name

            // Obtain common values configuration files.
            sh """
              curl -H 'Authorization: token $JENKINSBOT_PSW' -H 'Accept: application/vnd.github.v3.raw' https://github.ibm.com/api/v3/repos/security-services/security-advisor-devops/contents/kubernetes/helm/common-values.yaml?ref=master > config/helm/${microServiceName}/common-values.yaml
              curl -H 'Authorization: token $JENKINSBOT_PSW' -H 'Accept: application/vnd.github.v3.raw' https://github.ibm.com/api/v3/repos/security-services/security-advisor-devops/contents/kubernetes/helm/_common-configmap.tpl?ref=master > config/helm/${microServiceName}/templates/_common-configmap.tpl
            """

            // Set required pipeline values.
            commonValues = readYaml file: "config/helm/${microServiceName}/common-values.yaml"
            if (BRANCH_NAME == "develop") {
              registryNamespace = commonValues.global.registryNamespace.development
              clusterNamespace = commonValues.global.clusterNamespace.development
              dockerLogin = DEVELOPMENT_DOCKER_TOKEN
              environment = "development"
              kube = "/home/bluemix/.bluemix/plugins/container-service/clusters/cert-mgmt-dev-admin/kube-config-dal10-cert-mgmt-dev.yml"
            } else if (BRANCH_NAME == "master") {
              registryNamespace = values.global.registryNamespace.production
              clusterNamespace = values.global.clusterNamespace.production
              dockerLogin = PRODUCTION_DOCKER_TOKEN
              environment = "production"
              kube = "/home/bluemix/.bluemix/plugins/container-service/clusters/security-advisor-prod-dal12-admin/kube-config-dal12-security-advisor-prod-dal12.yml"
            }
          }
        }
      }

      stage ("Verify Kubernetes resources syntax") {
        when {
          allOf {
            not { branch "develop" }
            not { branch "master" }

            expression {
              return env.shouldBuild != "false"
            }
          }
        }

        steps {
          script {
            STAGE_NAME = "Verify Kubernetes resources syntax"

            lintResults = sh(script: "cd config/helm/${microServiceName};helm lint -f common-values.yaml || true", returnStdout:true)
            if ((lintResults.contains("[ERROR]")) || (lintResults.contains("[WARNING]"))) {
              currentBuild.result = "FAILURE"
              env.shouldBuild = "false"
              slackSend (channel: 'secadvisor-health', color: '#F01717', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER>, '$STAGE_NAME' stage failed.\n\n${lintResults}")
            }
          }
        }
      }

      stage ("Unit & Integration tests") {
        when {
          not { branch "master" }
          expression {
            return env.shouldBuild != "false"
          }
        }

        steps {
          script {
            STAGE_NAME = "Unit & Integration tests"

            sh """
              pip3.6 install --no-cache-dir -r requirements.txt
              mv test/unit-tests/test_security_findings.py test/unit-tests/test_security_findings.py_back
              mv test/unit-tests/test_dict_merge.py test/unit-tests/test_dict_merge.py_back
              coverage-3.6 run --source=. -m unittest discover -s test
              coverage-3.6 xml -o test/coverage.xml
            """
          }
        }
      }

      stage ("SonarQube analysis") {
        options {
          timeout(time: 5, unit: 'MINUTES')
        }

        when {
          allOf {
            not { branch "develop" }
            not { branch "master" }
            expression {
              return env.shouldBuild != "false"
            }
          }
        }

        steps {
          script {
            STAGE_NAME = "SonarQube analysis"

            withSonarQubeEnv('SecurityAdvisor') {
              sh "../../../sonar-scanner/bin/sonar-scanner"
            }

            try {
              // Check whether coverage threshold is met, otherwise fail the job.
              qualitygate = waitForQualityGate()
              if (qualitygate.status != "OK") {
                currentBuild.result = "FAILURE"
                env.shouldBuild = "false"
                slackSend (channel: 'secadvisor-health', color: '#F01717', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER>, '$STAGE_NAME' stage failed.")
              }
            } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
              currentBuild.result = "FAILURE"
              env.shouldBuild = "false"
              slackSend (channel: 'secadvisor-health', color: '#F01717', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER>, '$STAGE_NAME' stage timed out. Re-run the job.")
            }
          }
        }
      }

      stage ("Merge pull request") {
        when {
          expression {
            return env.shouldBuild != "false"
          }

          allOf {
            not { branch "develop" }
            not { branch "master" }
          }
        }

        steps {
          script {
            STAGE_NAME = "Merge pull request"

            // Check if the Pull Request requires a review.
            isMergeable = sh(script: "curl -s https://github.ibm.com/api/v3/repos/oneibmcloud/${repositoryName}/pulls/$CHANGE_ID?access_token=$JENKINSBOT_PSW | jq '.mergeable_state' | tr -d '\"'", returnStdout:true).trim()

            if (isMergeable == "blocked") {
              env.shouldBuild = "false"
              slackSend (channel: "secadvisor-health", color: '#e9a820', message: "*${repositoryName}*/<$CHANGE_URL|PR-$CHANGE_ID>: Pull Request review required.")
            } else {
              // Attempt merging the Pull Request.
              isMerged = sh(script: "curl -s -o /dev/null -w '%{http_code}' -X PUT -d '{\"commit_title\": \"Merge pull request\"}'  https://github.ibm.com/api/v3/repos/oneibmcloud/${repositoryName}/pulls/$CHANGE_ID/merge?access_token=$JENKINSBOT_PSW", returnStdout:true).trim()

              if (isMerged != "200") {
                currentBuild.result = "FAILURE"
                env.shouldBuild = "false"
                slackSend (channel: "secadvisor-health", color: '#F01717', message: "*${repositoryName}*/<$CHANGE_URL|PR-$CHANGE_ID>: Failed while attempting to merge. Review the Pull Request.")
              } else {
                slackSend (channel: "secadvisor-health", color: '#199515', message: "*${repositoryName}*/<$CHANGE_URL|PR-$CHANGE_ID>: <$BUILD_URL|Build #$BUILD_NUMBER> passed successfully.")
              }
            }
          }
        }
      }

      stage ("Build Docker container image") {
        when {
          expression {
            return env.shouldBuild != "false"
          }

          anyOf {
            branch "develop"
            branch "master"
          }
        }

        steps {
          script {
            STAGE_NAME = "Build Docker container image"

            // Build the Docker container image and push to Bluemix Container Registry.
            sh """
              # dos2unix environment.sh
              docker login -u token -p ${dockerLogin} registry.ng.bluemix.net
              docker build -t registry.ng.bluemix.net/${registryNamespace}/${microServiceName}:0.0.$BUILD_NUMBER .
              docker push registry.ng.bluemix.net/${registryNamespace}/${microServiceName}:0.0.$BUILD_NUMBER
            """

            // Delete the built image from the build machine.
            sh "docker rmi registry.ng.bluemix.net/${registryNamespace}/${microServiceName}:0.0.$BUILD_NUMBER"
          }
        }
      }

      stage ("Publish to Kubernetes") {
        when {
          expression {
            return env.shouldBuild != "false"
          }

          anyOf {
            branch "develop"
            branch "master"
          }
        }

        steps {
          script {
            STAGE_NAME = "Publish to Kubernetes"

            // Check if the release exists at all.
            isReleaseExists = sh(script: "export KUBECONFIG=${kube};helm list -q | tr '\\n' ','", returnStdout: true)
            if (isReleaseExists.contains("${microServiceName}")) {
              // The release exist, check its status.
              helmStatus = sh(script: "export KUBECONFIG=${kube};helm status ${microServiceName} -o json | jq '.info.status.code'", returnStdout: true)
              if (helmStatus.trim() != "1") {
                // The release is in Failed state, remove it to reinstall and continue to re-install.
                sh "export KUBECONFIG=${kube};helm del --purge ${microServiceName}"
              }
            } else {
              // The release doesn't exist, install it.
            }

            // Upgrade a micro-service release or install it if doesn't exist.
            sh """
              export KUBECONFIG=${kube}
              ../../../yaml w -i config/helm/${microServiceName}/values.yaml global.tag 0.0.$BUILD_NUMBER
              ../../../yaml w -i config/helm/${microServiceName}/Chart.yaml version 0.0.$BUILD_NUMBER

              helm upgrade --set "global.env=${environment}" --values config/helm/${microServiceName}/common-values.yaml ${microServiceName} config/helm/${microServiceName} --namespace ${clusterNamespace} --install --force --wait --timeout 300 --recreate-pods || true
            """

            // Verify whether the deployment passed or not.
            helmStatus = sh(script: "export KUBECONFIG=${kube};helm status ${microServiceName} -o json | jq '.info.status.code'", returnStdout: true)
            if (helmStatus.trim() != "1") {
              currentBuild.result = "FAILURE"
              env.shouldBuild = "false"

              // Notify about the failed operation.
              slackSend (channel: "secadvisor-health", color: '#F01717', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER> failed deploying to _backend ${environment} cluster_.")
            } else {
              // Notify about the successful operation.
              slackSend (channel: "secadvisor-health", color: '#199515', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER> deployed successfully to _backend ${environment} cluster_.")
            }
          }
        }
      }

      stage ("Generate release changelog") {
        when {
          branch "master"
          expression {
            return env.shouldBuild != "false"
          }
        }

        steps {
          script {
            STAGE_NAME = "Generate release changelog"

            // Generate changelog and tag the release.
            sh '''
              changelog=\$(git log `git describe --tags --abbrev=0 HEAD^`..HEAD --oneline --no-merges)
              jq -n --arg tagname "v0.0.$BUILD_NUMBER" \
              --arg name "Release v0.0.$BUILD_NUMBER"  \
              --arg body "$changelog"                  \
              '{"tag_name": $tagname, "target_commitish": "master", "name": $name, "body": $body, "draft": false, "prerelease": false}' |
              curl -d@- https://github.ibm.com/api/v3/repos/security-services/$JOB_NAME/releases?access_token=$JENKINSBOT_PSW
            '''
          }
        }
      }
    }

    post {
      always {
        deleteDir()
      }

      success {
        script {
          //Run end-to-end tests, if requested.
          if (BRANCH_NAME == "develop") {
            // runE2E = sh (script: "git log -1 | grep '.*\\[e2e\\].*'", returnStatus: true)
            // if (runE2E == 0) {
            //   build job: 'security-advisor-e2e-dev', wait: false
            // }
          }
        }
      }

      failure {
        script {
          // Notify on failure.
          if (env.shouldBuild != "false") {
            slackSend (channel: 'secadvisor-health', color: '#F01717', message: "*$JOB_NAME*: <$BUILD_URL|Build #$BUILD_NUMBER>, '$STAGE_NAME' stage failed.")
          }

          // Send an email if the failure occurance as part of te Pull Request.
          emailext (
            attachLog: true,
            subject: '[Jenkins] $PROJECT_NAME job failed',
            to: "$env.CHANGE_AUTHOR_EMAIL",
            replyTo: 'ashishth@in.ibm.com',
            body: '''<p>You are receiving this email because <a href="$CHANGE_URL">your pull request</a> failed during a job execution. <a href="$BUILD_URL">Review the build logs</a> to debug the reason for the failure and submit a fix.'''
          )
        }
      }
    }
  }
