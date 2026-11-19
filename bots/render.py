#!/usr/bin/env python3
"""Render k8s/bots/<bot>.yaml for every bot (stdlib only).

Each file is a multi-document stream of JSON objects, which is valid YAML and
which kubectl accepts. Re-run after editing bots/, bots/personas/ or the constants below.

  python3 bots/render.py                  write k8s/bots/*.yaml
  python3 bots/render.py --tools-check ada   print the one-off tools check Job to stdout
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "k8s", "bots")

IMAGE = "node:22-bookworm-slim"
def _setting(key):
    """Env var, else KEY=value from the gitignored ./settings.env (see settings.env.example)."""
    if os.environ.get(key):
        return os.environ[key]
    try:
        for line in open(os.path.join(ROOT, "settings.env")):
            k, _, v = line.split("#")[0].strip().partition("=")
            if k == key and v:
                return v.strip().strip('"')
    except FileNotFoundError:
        pass
    sys.exit(f"set {key} in settings.env or the environment")


API_NODE_CIDR = _setting("PI_NODE_IP") + "/32"   # k3s API server on the Pi (post-DNAT address)
POD_CIDR = "10.42.0.0/16"
SVC_CIDR = "10.43.0.0/16"
PRIVATE = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
PATH = ("/opt/tools/bin:/opt/tools/python/bin:/usr/local/sbin:/usr/local/bin:"
        "/usr/sbin:/usr/bin:/sbin:/bin")

# Chronicler runs daily at 21:00. Everyone else averages a run every 90 minutes:
# 16 runs a day, alternating 2h and 1h gaps, staggered by 10 minutes per bot.
HOURS_90MIN = "0,2,3,5,6,8,9,11,12,14,15,17,18,20,21,23"

BOTS = [
    {"name": "ada", "runtime": "claude", "minute": 0},
    {"name": "marvin", "runtime": "claude", "minute": 10},
    {"name": "iris", "runtime": "claude", "minute": 20},
    {"name": "rex", "runtime": "codex", "minute": 30},
    {"name": "juno", "runtime": "codex", "minute": 40},
    {"name": "chronicler", "runtime": "claude", "schedule": "0 21 * * *"},
]


def read(path):
    with open(path) as f:
        return f.read()


def meta(name, ns):
    return {"name": name, "namespace": ns}


def pvc(name, ns, size):
    return {"apiVersion": "v1", "kind": "PersistentVolumeClaim", "metadata": meta(name, ns),
            "spec": {"accessModes": ["ReadWriteOnce"],
                     "resources": {"requests": {"storage": size}}}}


def pod_spec(bot, job_command=None):
    ns, runtime = f"bot-{bot['name']}", bot["runtime"]
    env = [
        {"name": "BOT_NAME", "value": bot["name"]},
        {"name": "BOT_RUNTIME", "value": runtime},
        {"name": "PATH", "value": PATH},
        {"name": "HOME", "value": "/home/bot"},
    ]
    main_env_from = [{"secretRef": {"name": "forum-cred", "optional": True}}]
    if runtime == "claude":
        env.append({"name": "CLAUDE_CODE_OAUTH_TOKEN", "valueFrom": {"secretKeyRef": {
            "name": "claude-auth", "key": "CLAUDE_CODE_OAUTH_TOKEN", "optional": True}}})
    mounts = [
        {"name": "workspace", "mountPath": "/work"},
        {"name": "home", "mountPath": "/home/bot"},
        {"name": "tools", "mountPath": "/opt/tools", "readOnly": True},
        {"name": "bot-code", "mountPath": "/opt/agent-town/bots", "readOnly": True},
        {"name": "persona", "mountPath": "/persona", "readOnly": True},
    ]
    if runtime == "codex":
        mounts.append({"name": "codex-auth", "mountPath": "/secrets/codex", "readOnly": True})
    main = {
        "name": "bot",
        "image": IMAGE,
        "command": job_command or ["bash", "/opt/agent-town/bots/turn.sh"],
        "workingDir": "/work",
        "env": env,
        "envFrom": main_env_from,
        "securityContext": {"runAsUser": 1000, "runAsGroup": 1000,
                            "allowPrivilegeEscalation": False},
        "resources": {"requests": {"cpu": "100m", "memory": "256Mi"},
                      "limits": {"cpu": "1", "memory": "1Gi"}},
        "volumeMounts": mounts,
    }
    init = {
        "name": "install-tools",
        "image": IMAGE,
        "command": ["bash", "/opt/agent-town/bots/tools-install.sh"],
        "securityContext": {"runAsUser": 0},
        "resources": {"requests": {"cpu": "50m", "memory": "128Mi"},
                      "limits": {"cpu": "500m", "memory": "512Mi"}},
        "volumeMounts": [
            {"name": "tools", "mountPath": "/opt/tools"},
            {"name": "bot-code", "mountPath": "/opt/agent-town/bots", "readOnly": True},
        ],
    }
    vols = [
        {"name": "workspace", "persistentVolumeClaim": {"claimName": "workspace"}},
        {"name": "home", "persistentVolumeClaim": {"claimName": "home"}},
        {"name": "tools", "persistentVolumeClaim": {"claimName": "tools"}},
        {"name": "bot-code", "configMap": {"name": "bot-code", "defaultMode": 493}},
        {"name": "persona", "configMap": {"name": "persona", "defaultMode": 420}},
    ]
    if runtime == "codex":
        vols.append({"name": "codex-auth", "secret": {"secretName": "codex-auth",
                                                       "optional": True}})
    return {
        "serviceAccountName": "bot",
        "restartPolicy": "Never",
        "securityContext": {"fsGroup": 1000},
        "initContainers": [init],
        "containers": [main],
        "volumes": vols,
    }


def bot_docs(bot):
    name = bot["name"]
    ns = f"bot-{name}"
    docs = []
    docs.append({"apiVersion": "v1", "kind": "ConfigMap", "metadata": meta("bot-code", ns),
                 "data": {"forum.py": read(os.path.join(ROOT, "bots", "forum.py")),
                          "turn.sh": read(os.path.join(ROOT, "bots", "turn.sh")),
                          "tools-install.sh": read(os.path.join(ROOT, "bots", "tools-install.sh"))}})
    docs.append({"apiVersion": "v1", "kind": "ConfigMap", "metadata": meta("persona", ns),
                 "data": {"AGENTS.md": read(os.path.join(ROOT, "bots", "personas", f"{name}.md"))}})
    docs += [pvc("workspace", ns, "2Gi"), pvc("home", ns, "1Gi"), pvc("tools", ns, "2Gi")]
    docs.append({"apiVersion": "v1", "kind": "ServiceAccount", "metadata": meta("bot", ns)})
    docs.append({"apiVersion": "rbac.authorization.k8s.io/v1", "kind": "Role",
                 "metadata": meta("bot-admin", ns),
                 "rules": [{"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]}]})
    docs.append({"apiVersion": "rbac.authorization.k8s.io/v1", "kind": "RoleBinding",
                 "metadata": meta("bot-admin", ns),
                 "roleRef": {"apiGroup": "rbac.authorization.k8s.io", "kind": "Role",
                             "name": "bot-admin"},
                 "subjects": [{"kind": "ServiceAccount", "name": "bot", "namespace": ns}]})
    docs.append({"apiVersion": "v1", "kind": "ResourceQuota", "metadata": meta("bot-quota", ns),
                 "spec": {"hard": {"requests.cpu": "1", "limits.cpu": "1",
                                   "requests.memory": "1536Mi", "limits.memory": "1536Mi",
                                   "requests.storage": "6Gi", "persistentvolumeclaims": "3",
                                   "pods": "10"}}})
    docs.append({"apiVersion": "v1", "kind": "LimitRange", "metadata": meta("bot-limits", ns),
                 "spec": {"limits": [{"type": "Container",
                                      "default": {"cpu": "500m", "memory": "512Mi"},
                                      "defaultRequest": {"cpu": "50m", "memory": "128Mi"},
                                      "max": {"cpu": "1", "memory": "1Gi"}}]}})
    docs.append({"apiVersion": "networking.k8s.io/v1", "kind": "NetworkPolicy",
                 "metadata": meta("bot-netpol", ns),
                 "spec": {
                     "podSelector": {},
                     "policyTypes": ["Ingress", "Egress"],
                     "ingress": [
                         {"from": [{"podSelector": {}}]},
                         {"from": [{"namespaceSelector": {"matchLabels": {
                             "kubernetes.io/metadata.name": "kube-system"}}}]},
                     ],
                     "egress": [
                         {"to": [{"namespaceSelector": {"matchLabels": {
                             "kubernetes.io/metadata.name": "kube-system"}}}],
                          "ports": [{"port": 53, "protocol": "UDP"},
                                    {"port": 53, "protocol": "TCP"}]},
                         {"to": [{"namespaceSelector": {"matchLabels": {
                             "kubernetes.io/metadata.name": "town-square"}}}]},
                         {"to": [{"ipBlock": {"cidr": API_NODE_CIDR}}],
                          "ports": [{"port": 6443, "protocol": "TCP"}]},
                         {"to": [{"ipBlock": {"cidr": POD_CIDR}},
                                 {"ipBlock": {"cidr": SVC_CIDR}}]},
                         {"to": [{"ipBlock": {"cidr": "0.0.0.0/0", "except": PRIVATE}}]},
                     ],
                 }})
    schedule = bot.get("schedule") or f"{bot['minute']} {HOURS_90MIN} * * *"
    docs.append({
        "apiVersion": "batch/v1", "kind": "CronJob", "metadata": meta(f"{name}-turn", ns),
        "spec": {
            "schedule": schedule,
            "suspend": False,
            "concurrencyPolicy": "Forbid",
            "startingDeadlineSeconds": 300,
            "successfulJobsHistoryLimit": 2,
            "failedJobsHistoryLimit": 3,
            "jobTemplate": {"spec": {
                "activeDeadlineSeconds": 1200,
                "backoffLimit": 0,
                "template": {"spec": pod_spec(bot)},
            }},
        },
    })
    return docs


def tools_check_job(name):
    """One-off Job: runs the tools initContainer, then proves each tool works."""
    bot = next(b for b in BOTS if b["name"] == name)
    check = ("set -x; claude --version; codex --version; kubectl version --client; "
             "python3 /opt/agent-town/bots/forum.py selftest")
    return {"apiVersion": "batch/v1", "kind": "Job",
            "metadata": meta("tools-check", f"bot-{name}"),
            "spec": {"backoffLimit": 0, "ttlSecondsAfterFinished": 600,
                     "template": {"spec": pod_spec(bot, job_command=["bash", "-c", check])}}}


def dump(docs):
    return "\n---\n".join(json.dumps(d, indent=2) for d in docs) + "\n"


def main(argv):
    if len(argv) == 2 and argv[0] == "--tools-check":
        sys.stdout.write(dump([tools_check_job(argv[1])]))
        return
    os.makedirs(OUT, exist_ok=True)
    for bot in BOTS:
        path = os.path.join(OUT, f"{bot['name']}.yaml")
        with open(path, "w") as f:
            f.write(f"# Generated by bots/render.py. Edit the source, then re-render.\n")
            f.write(dump(bot_docs(bot)))
        print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
