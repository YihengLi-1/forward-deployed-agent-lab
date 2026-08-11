from pathlib import Path

import yaml


def test_kubernetes_manifest_has_required_workloads_and_probes() -> None:
    path = Path(__file__).resolve().parents[1] / "deployment" / "k8s.yaml"
    resources = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    kinds = {resource["kind"] for resource in resources}
    assert {"ConfigMap", "Deployment", "Service", "HorizontalPodAutoscaler", "NetworkPolicy"} <= kinds
    deployment = next(resource for resource in resources if resource["kind"] == "Deployment")
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    assert container["readinessProbe"]["httpGet"]["path"] == "/readyz"
    assert container["livenessProbe"]["httpGet"]["path"] == "/healthz"

