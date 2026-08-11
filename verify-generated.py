#!/usr/bin/env python3

import argparse
import pathlib
import subprocess

import yaml


GENERATED_CHARTS = (
    "cluster-api-core",
    "cluster-api-bootstrap-kubeadm",
    "cluster-api-control-plane-kubeadm",
    "cluster-api-provider-openstack",
    "openstack-resource-controller",
    "cluster-api",
)

CAPI_CRD_DIRECTORIES = (
    pathlib.Path("charts/cluster-api-core/crds"),
    pathlib.Path("charts/cluster-api-bootstrap-kubeadm/crds"),
    pathlib.Path("charts/cluster-api-control-plane-kubeadm/crds"),
)

ORC_CRD_DIRECTORY = pathlib.Path("charts/openstack-resource-controller/crds")

ORC_CRD_NAMES = frozenset({
    "addressscopes.openstack.k-orc.cloud",
    "applicationcredentials.openstack.k-orc.cloud",
    "domains.openstack.k-orc.cloud",
    "endpoints.openstack.k-orc.cloud",
    "flavors.openstack.k-orc.cloud",
    "floatingips.openstack.k-orc.cloud",
    "groups.openstack.k-orc.cloud",
    "images.openstack.k-orc.cloud",
    "keypairs.openstack.k-orc.cloud",
    "networks.openstack.k-orc.cloud",
    "ports.openstack.k-orc.cloud",
    "projects.openstack.k-orc.cloud",
    "roles.openstack.k-orc.cloud",
    "routerinterfaces.openstack.k-orc.cloud",
    "routers.openstack.k-orc.cloud",
    "securitygroups.openstack.k-orc.cloud",
    "servergroups.openstack.k-orc.cloud",
    "servers.openstack.k-orc.cloud",
    "services.openstack.k-orc.cloud",
    "subnets.openstack.k-orc.cloud",
    "trunks.openstack.k-orc.cloud",
    "users.openstack.k-orc.cloud",
    "volumes.openstack.k-orc.cloud",
    "volumetypes.openstack.k-orc.cloud",
})

ORC_CRD_API_VERSION = "v1alpha1"

MANAGEMENT_KUBERNETES_VERSION = ">=1.32.0-0 <1.37.0-0"


def load_yaml(path):
    with path.open() as stream:
        return yaml.safe_load(stream)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def feature_gates(chart, values=None):
    command = [
        "helm",
        "template",
        f"charts/{chart}",
        "--kube-version",
        "1.36.0",
    ]

    for name, value in (values or {}).items():
        command.extend(("--set", f"{name}={str(value).lower()}"))

    output = subprocess.check_output(command, text=True)
    documents = yaml.safe_load_all(output)
    arguments = []

    for document in documents:
        if not document or document.get("kind") != "Deployment":
            continue

        containers = document["spec"]["template"]["spec"]["containers"]
        for container in containers:
            arguments.extend(
                argument
                for argument in container.get("args", [])
                if argument.startswith("--feature-gates=")
            )

    require(len(arguments) == 1, f"expected one feature-gates argument for {chart}")

    return dict(
        gate.split("=", 1)
        for gate in arguments[0].removeprefix("--feature-gates=").split(",")
    )


def verify_chart_metadata(args):
    for chart in GENERATED_CHARTS:
        metadata = load_yaml(pathlib.Path(f"charts/{chart}/Chart.yaml"))
        require(metadata["version"] == args.chart_version,
                f"unexpected chart version for {chart}")
        require(metadata["kubeVersion"] == MANAGEMENT_KUBERNETES_VERSION,
                f"unexpected Kubernetes version constraint for {chart}")

    expected_app_versions = {
        "cluster-api-core": args.capi_version,
        "cluster-api-bootstrap-kubeadm": args.capi_version,
        "cluster-api-control-plane-kubeadm": args.capi_version,
        "cluster-api-provider-openstack": args.capo_version,
        "openstack-resource-controller": args.orc_version,
        "cluster-api": args.capi_version,
    }

    for chart, expected in expected_app_versions.items():
        metadata = load_yaml(pathlib.Path(f"charts/{chart}/Chart.yaml"))
        require(metadata["appVersion"] == expected,
                f"unexpected application version for {chart}")


def verify_images(args):
    expected_images = {
        "cluster-api-core": f"registry.k8s.io/cluster-api/cluster-api-controller:{args.capi_version}",
        "cluster-api-bootstrap-kubeadm": f"registry.k8s.io/cluster-api/kubeadm-bootstrap-controller:{args.capi_version}",
        "cluster-api-control-plane-kubeadm": f"registry.k8s.io/cluster-api/kubeadm-control-plane-controller:{args.capi_version}",
        "cluster-api-provider-openstack": f"registry.k8s.io/capi-openstack/capi-openstack-controller:{args.capo_version}",
        "openstack-resource-controller": f"quay.io/orc/openstack-resource-controller:{args.orc_version}",
    }

    for chart, expected in expected_images.items():
        values = load_yaml(pathlib.Path(f"charts/{chart}/values.yaml"))
        require(values["image"] == expected, f"unexpected image for {chart}")


def verify_feature_gates():
    core = feature_gates("cluster-api-core")
    require(core["MachineSetPreflightChecks"] == "true",
            "MachineSetPreflightChecks must default to true in core")
    require(core["MachineTaintPropagation"] == "true",
            "MachineTaintPropagation must default to true in core")
    require(core["PriorityQueue"] == "true",
            "PriorityQueue must default to true in core")
    require(core["ReconcilerRateLimiting"] == "true",
            "ReconcilerRateLimiting must default to true in core")
    require(core["InPlaceUpdates"] == "false",
            "InPlaceUpdates must default to false in core")

    core_disabled = feature_gates("cluster-api-core", {
        "exp_machine_set_preflight_checks": False,
        "exp_machine_taint_propagation": False,
    })
    require(core_disabled["MachineSetPreflightChecks"] == "false",
            "MachineSetPreflightChecks override was not rendered")
    require(core_disabled["MachineTaintPropagation"] == "false",
            "MachineTaintPropagation override was not rendered in core")

    control_plane = feature_gates("cluster-api-control-plane-kubeadm")
    require(control_plane["MachineTaintPropagation"] == "true",
            "MachineTaintPropagation must default to true in KCP")
    require(control_plane["PriorityQueue"] == "true",
            "PriorityQueue must default to true in KCP")
    require(control_plane["ReconcilerRateLimiting"] == "true",
            "ReconcilerRateLimiting must default to true in KCP")
    require(control_plane["InPlaceUpdates"] == "false",
            "InPlaceUpdates must default to false in KCP")

    control_plane_disabled = feature_gates(
        "cluster-api-control-plane-kubeadm",
        {"exp_machine_taint_propagation": False},
    )
    require(control_plane_disabled["MachineTaintPropagation"] == "false",
            "MachineTaintPropagation override was not rendered in KCP")


def verify_crds():
    for directory in CAPI_CRD_DIRECTORIES:
        for path in directory.glob("*.yaml"):
            crd = load_yaml(path)
            versions = {version["name"]: version for version in crd["spec"]["versions"]}
            name = crd["metadata"]["name"]

            require("v1alpha3" not in versions and "v1alpha4" not in versions,
                    f"{name} still contains a removed alpha version")
            require("v1beta2" in versions and versions["v1beta2"]["served"],
                    f"{name} must serve v1beta2")
            require(versions["v1beta2"]["storage"],
                    f"{name} must store v1beta2")
            require(sum(version["storage"] for version in versions.values()) == 1,
                    f"{name} must have exactly one storage version")

            if crd["spec"]["group"] != "runtime.cluster.x-k8s.io":
                require("v1beta1" in versions and versions["v1beta1"]["served"],
                        f"{name} must serve v1beta1")


def verify_orc_crds():
    names = {path.stem for path in ORC_CRD_DIRECTORY.glob("*.yaml")}
    require(names == ORC_CRD_NAMES,
            f"unexpected ORC CRD set: missing {ORC_CRD_NAMES - names}, extra {names - ORC_CRD_NAMES}")

    for path in ORC_CRD_DIRECTORY.glob("*.yaml"):
        crd = load_yaml(path)
        name = crd["metadata"]["name"]
        versions = {version["name"]: version for version in crd["spec"]["versions"]}

        require(versions.keys() == {ORC_CRD_API_VERSION},
                f"{name} must serve only {ORC_CRD_API_VERSION}")
        require(versions[ORC_CRD_API_VERSION]["served"],
                f"{name} must serve {ORC_CRD_API_VERSION}")
        require(versions[ORC_CRD_API_VERSION]["storage"],
                f"{name} must store {ORC_CRD_API_VERSION}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-version", required=True)
    parser.add_argument("--capi-version", required=True)
    parser.add_argument("--capo-version", required=True)
    parser.add_argument("--orc-version", required=True)
    args = parser.parse_args()

    verify_chart_metadata(args)
    verify_images(args)
    verify_feature_gates()
    verify_crds()
    verify_orc_crds()


if __name__ == "__main__":
    main()
