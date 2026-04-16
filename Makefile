# Update this for every tagged release.
CHART_VERSION = 0.2.7

# Defines the versions to use for cluster API components.
CAPI_VERSION = v1.11.7
CAPO_VERSION = v0.13.5

# CAPO requires ORC.
ORC_VERSION = v1.0.2

# All the charts we can generate.
CHARTS = cluster-api-core \
	 cluster-api-bootstrap-kubeadm \
	 cluster-api-control-plane-kubeadm \
	 cluster-api-provider-openstack \
	 openstack-resource-controller

# These charts are hand crafted, but still valid for things like
# validation.
USER_CHARTS = cluster-api \
	      cluster-api-cluster-openstack \
	      cluster-api-cluster-autoscaler-openstack

# Generator script location.
GENERATE = ./generate.py

all: cluster-api

.PHONY: cluster-api
cluster-api: $(CHARTS)
	./generate-capi.py -v $(CHART_VERSION) -c $(CAPI_VERSION) $(CHARTS)

.PHONY: cluster-api-core
cluster-api-core:
	$(GENERATE) --chart $@ --version $(CHART_VERSION) --app-version $(CAPI_VERSION) --path https://github.com/kubernetes-sigs/cluster-api/config/default?ref=$(CAPI_VERSION) --image registry.k8s.io/cluster-api/cluster-api-controller:$(CAPI_VERSION)

.PHONY: cluster-api-bootstrap-kubeadm
cluster-api-bootstrap-kubeadm:
	$(GENERATE) --chart $@ --version $(CHART_VERSION) --app-version $(CAPI_VERSION) --path https://github.com/kubernetes-sigs/cluster-api/bootstrap/kubeadm/config/default?ref=$(CAPI_VERSION) --image registry.k8s.io/cluster-api/kubeadm-bootstrap-controller:$(CAPI_VERSION)

.PHONY: cluster-api-control-plane-kubeadm
cluster-api-control-plane-kubeadm:
	$(GENERATE) --chart $@ --version $(CHART_VERSION) --app-version $(CAPI_VERSION) --path https://github.com/kubernetes-sigs/cluster-api/controlplane/kubeadm/config/default?ref=$(CAPI_VERSION) --image registry.k8s.io/cluster-api/kubeadm-control-plane-controller:$(CAPI_VERSION)

.PHONY: cluster-api-provider-openstack
cluster-api-provider-openstack:
	$(GENERATE) --chart $@ --version $(CHART_VERSION) --app-version $(CAPO_VERSION) --path https://github.com/kubernetes-sigs/cluster-api-provider-openstack/config/default?ref=$(CAPO_VERSION) --image registry.k8s.io/capi-openstack/capi-openstack-controller:$(CAPO_VERSION)

.PHONY: openstack-resource-controller
openstack-resource-controller:
	$(GENERATE) --chart $@ --version $(CHART_VERSION) --app-version $(ORC_VERSION) --path https://github.com/k-orc/openstack-resource-controller/config/default?ref=$(ORC_VERSION) --image quay.io/orc/openstack-resource-controller:$(ORC_VERSION)

.PHONY: test
test:
	set -e; \
	for chart in $(CHARTS) $(USER_CHARTS); do \
		helm dependency update charts/$${chart}; \
		helm lint --strict charts/$${chart}; \
		helm template charts/$${chart} > /dev/null; \
	done

.PHONY: docs
docs:
	@go install github.com/unikorn-cloud/core/hack/docs-generate@main
	docs-generate
