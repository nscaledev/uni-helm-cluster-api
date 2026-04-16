<!-- THIS FILE IS AUTO-GENERATED. DO NOT EDIT -->

# Installing an OpenStack Cluster

... is quite involved!

## Configuration Variables

Please consult the [`values.yaml`](values.yaml) file for some basic examples.
The [`values.schema.json`](values.schema.json) file documents structure, types and required fields further.

## Helm

When using Helm directly, deprovisioning will delete the identity secret used to access OpenStack immediately and result in a deadlock.
Don't use this :smile:

## ArgoCD

Unlike Helm, ArgoCD can provision and deprovision in "waves", thus we can keep the identity secret alive for the duration of deprovisioning.
This is the only supported method of operation.

Here's an example application:

```yaml
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: foo
  namespace: argocd
spec:
  destination:
    server: https://kubernetes.default.svc
    namespace: foo
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api-cluster-openstack
    targetRevision: 0.7.0
    helm:
      releaseName: foo
      # Remove the default work queue.
      parameters:
      - name: workload.default
        value: null
      values: |-
        openstack:
          cloud: REDACTED
          cloudsYAML: REDACTED
          ca: REDACTED
          sshKeyName: REDACTED
          region: en-west-1
          failureDomain: eu-west-1a
          externalNetworkID: dadfef54-d1c5-447a-8933-f515eeadd822
        api:
          allowList:
          - 123.45.67.89
          certificateSANs:
          - kubernetes.my-domain.com
        controlPlane:
          version:  v1.30.2
          replicas: 3
          skipKubeProxy: false
          machine:
            imageID: 7a517603-aa70-47a9-a6f3-c102d30e67c0
            flavorID: 061f0cf2-2503-4005-89ed-ff1dc217874f
            diskSize: 40
        workloadPools:
          general-purpose:
            replicas: 3
            version:  v1.30.2
            machine:
              imageID: 7a517603-aa70-47a9-a6f3-c102d30e67c0
              flavorID: 061f0cf2-2503-4005-89ed-ff1dc217874f
              diskSize: 100
            autoscaling:
              limits:
                minReplicas: 3
                maxReplicas: 10
              scheduler:
                cpu: 4
                memory: 16G
          gpu:
            version: v1.30.2
            replicas: 3
            machine:
              imageID: 7a517603-aa70-47a9-a6f3-c102d30e67c0
              flavorID: 061f0cf2-2503-4005-89ed-ff1dc217874f
              diskSize: 100
            autoscaling:
              limits:
                minReplicas: 3
                maxReplicas: 10
              scheduler:
                cpu: 4
                memory: 32G
                gpu:
                  type: nvidia.com/gpu
                  count: 1
        network:
          nodeCIDR: 192.168.0.0/12
          serviceCIDRs:
          - 172.16.0.0/12
          podCIDRs:
          - 10.0.0.0/8
          dnsNameservers:
          - 1.1.1.1
          - 8.8.8.8
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

This by itself will not actually provision a working cluster.
See below for more details.

### Getting Working Cluster

To achieve a working cluster that is correctly scaled and works, you will also need to concurrently install:

* A CNI
* [The Openstack cloud provider](https://github.com/kubernetes/cloud-provider-openstack)

To do this, grab the kubeconfig file, subsituting the correct namespace and release name:

```shell
kubectl -n foo foo-kubeconfig -o 'jsonpath={.data.value}' | base64 -d
```

Then use Helm of similar to provision against that kubeconfig.
