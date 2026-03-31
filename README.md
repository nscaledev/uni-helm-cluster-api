<!-- THIS FILE IS AUTO-GENERATED. DO NOT EDIT -->

# Helm Charts to Deploy Cluster API

## Why?

`clusterctl` is very opinionated, it will pull down some kustomize generated manifests, then do some environment substitution on them.
This isn't compatible with ArgoCD for example, hence this project.

## How

In simple terms, we run `kubectl kustomize`, chop up the manifests and auto generate templates.
When we encounter one of the annoying environment variables, we replace it with Go templating, then add the replacement into `values.yaml`.

## Deploying Prerequisites

This chart requires the following to be installed on the target cluster first:

* [Jetstack cert-manager](https://cert-manager.io/)

## Deploying One-Shot

There is a top level chart-of-charts that will just install everything as a big bang operation.

<details>
<summary>Helm</summary>

```shell
helm repo add unikorn-cloud-capi https://unikorn-cloud.github.io/helm-cluster-api
helm repo update
helm upgrade --install cluster-api unikorn-cloud-capi/cluster-api -n cluster-api --create-namespace --version 0.2.7
```
</details>

<details>
<summary>ArgoCD</summary>

```yaml
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api
    targetRevision: 0.2.7
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-api
  ignoreDifferences:
  # Aggregated roles are mangically updated by the API.
  - group: rbac.authorization.k8s.io
    kind: ClusterRole
    name: capi-aggregated-manager-role
    jsonPointers:
    - /rules
  - group: rbac.authorization.k8s.io
    kind: ClusterRole
    name: capi-kubeadm-control-plane-aggregated-manager-role
    jsonPointers:
    - /rules
  # CA certs are injected by cert-manager mutation
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

## Deploying Main Components

You may want to be a little less gung-ho and deploy the pieces as separate applications.

### Core

<details>
<summary>Helm</summary>

```shell
helm repo add unikorn-cloud-capi https://unikorn-cloud.github.io/helm-cluster-api
helm repo update
helm upgrade --install cluster-api-core unikorn-cloud-capi/cluster-api-core -n cluster-api --create-namespace --version 0.2.7
```
</details>

<details>
<summary>ArgoCD</summary>

```yaml
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  generateName: cluster-api-core-
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api-core
    targetRevision: 0.2.7
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-api
  ignoreDifferences:
  # Aggregated roles are mangically updated by the API.
  - group: rbac.authorization.k8s.io
    kind: ClusterRole
    name: capi-aggregated-manager-role
    jsonPointers:
    - /rules
  # CA certs are injected by cert-manager mutation
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

### Bootstrap

<details>
<summary>Helm</summary>

```shell
helm repo add unikorn-cloud-capi https://unikorn-cloud.github.io/helm-cluster-api
helm repo update
helm upgrade --install cluster-api-bootstrap-kubeadm unikorn-cloud-capi/cluster-api-bootstrap-kubeadm -n cluster-api --create-namespace --version 0.2.7
```
</details>

<details>
<summary>ArgoCD</summary>

```yaml
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  generateName: cluster-api-bootstrap-kubeadm-
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api-bootstrap-kubeadm
    targetRevision: 0.2.7
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-api
  ignoreDifferences:
  - group: apiextensions.k8s.io
    jsonPointers:
    - /spec/conversion/webhook/clientConfig/caBundle
    kind: CustomResourceDefinition
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
    - RespectIgnoreDifferences=true
    - CreateNamespace=true
```
</details>

### Control Plane

<details>
<summary>Helm</summary>

```shell
helm repo add unikorn-cloud-capi https://unikorn-cloud.github.io/helm-cluster-api
helm repo update
helm upgrade --install cluster-api-control-plane-kubeadm unikorn-cloud-capi/cluster-api-control-plane-kubeadm -n cluster-api --create-namespace --version 0.2.7
```
</details>

<details>
<summary>ArgoCD</summary>

```yaml
---
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  generateName: cluster-api-control-plane-kubeadm-
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://unikorn-cloud.github.io/helm-cluster-api
    chart: cluster-api-control-plane-kubeadm
    targetRevision: 0.2.7
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-api
  ignoreDifferences:
  - group: rbac.authorization.k8s.io
    jsonPointers:
    - /rules
    kind: ClusterRole
    name: capi-kubeadm-control-plane-aggregated-manager-role
  - group: apiextensions.k8s.io
    jsonPointers:
    - /spec/conversion/webhook/clientConfig/caBundle
    kind: CustomResourceDefinition
  syncPolicy:
    automated:
      selfHeal: true
    syncOptions:
    - RespectIgnoreDifferences=true
    - CreateNamespace=true
```
</details>

## Deploying Infrastructure Providers and Clusters

Add providers to allow CAPI to talk to various cloud providers.

### OpenStack

* [Install the provider](README.provider-openstack.md)
* [Install a cluster](charts/cluster-api-cluster-openstack/README.md)

## Developers

It's a simple as:

* Bump the versions in `Makefile` and `charts/cluster-api/Chart.yaml`
* Run `make`
* Commit and merge.
