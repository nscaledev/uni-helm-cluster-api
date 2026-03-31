<!-- THIS FILE IS AUTO-GENERATED. DO NOT EDIT -->

# Installing Cluster API Provider OpenStack

<details>
<summary>Helm</summary>

```shell
helm repo add unikorn-cloud-capi https://unikorn-cloud.github.io/helm-cluster-api
helm repo update
helm upgrade --install cluster-api-provider-openstack unikorn-cloud-capi/cluster-api-provider-openstack -n cluster-api --create-namespace --version v0.2.7
```
</details>

<details>
<summary>ArgoCD</summary>

```yaml
---

apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster-api-provider-openstack
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api-provider-openstack
    targetRevision: v0.2.7
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-api
  ignoreDifferences:
    - group: apiextensions.k8s.io
      kind: CustomResourceDefinition
      jsonPointers:
        - /spec/conversion/webhook/clientConfig/caBundle
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
      - RespectIgnoreDifferences=true
      - CreateNamespace=true
```
</details>

