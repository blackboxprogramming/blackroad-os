from __future__ import annotations

import re
from typing import Any


STRATEGIES: dict[str, dict[str, Any]] = {
    "host_managed_oauth": {
        "secret_visibility": "host_only",
        "rotation": "reauthorize through the connector host; never scrape or export its OAuth token",
        "overlap_required": False,
    },
    "short_lived_federation": {
        "secret_visibility": "ephemeral",
        "rotation": "replace long-lived keys with workload identity, an app installation, or another short-lived exchange",
        "overlap_required": True,
    },
    "dual_token": {
        "secret_visibility": "secret_manager_only",
        "rotation": "issue a second least-privilege token, canary consumers, then revoke the old token by provider id",
        "overlap_required": True,
    },
    "versioned_secret": {
        "secret_visibility": "secret_manager_only",
        "rotation": "create a new version, deploy it, verify, make it current, then retire the prior version",
        "overlap_required": True,
    },
    "dual_database_identity": {
        "secret_visibility": "secret_manager_only",
        "rotation": "create a replacement login or alternate password, migrate clients, then remove the old login",
        "overlap_required": True,
    },
    "authorized_key_overlap": {
        "secret_visibility": "private_key_local_only",
        "rotation": "generate a new keypair, install the public key, verify a new session, then remove the old public key",
        "overlap_required": True,
    },
    "certificate_overlap": {
        "secret_visibility": "private_key_local_only",
        "rotation": "issue and deploy a new certificate, verify the served chain, then revoke or retire the old certificate",
        "overlap_required": True,
    },
    "dual_validation_window": {
        "secret_visibility": "secret_manager_only",
        "rotation": "accept old and new signatures during a bounded window, switch senders, verify, then reject the old secret",
        "overlap_required": True,
    },
    "key_ring_migration": {
        "secret_visibility": "hardware_or_secret_manager_only",
        "rotation": "add a new key version, re-encrypt or re-sign data, verify recovery, then retire the old version",
        "overlap_required": True,
    },
}


HOST_MANAGED_CONNECTORS = (
    "Ace Knowledge Graph",
    "AI Task Brief Builder",
    "AI Voice Generator",
    "Airtable",
    "Alpaca",
    "Amplitude",
    "AppDeploy",
    "Apple Music",
    "Asana",
    "AT&T",
    "Base44",
    "BioRender",
    "Calendly",
    "CALL-E",
    "Caveman Mode",
    "ConsentLayer",
    "Data Analytics",
    "DC PASS Contracts",
    "DigitalOcean",
    "Docusign",
    "Figma",
    "Finances",
    "Fireflies",
    "Formula Genius",
    "GitBook",
    "GitHub",
    "Gmail",
    "GoDaddy",
    "Google Calendar",
    "Google Contacts",
    "Google Drive",
    "Granola",
    "GSC Wizard",
    "Hugging Face",
    "Intuit QuickBooks",
    "Jotform",
    "Linear",
    "Malwarebytes",
    "MeetGeek",
    "Netlify",
    "Neura Relay MCP",
    "Notion",
    "OpenAI Developers",
    "OpenAI Library",
    "Outlook Email",
    "PandaDoc",
    "Pathors",
    "Pets",
    "Plugin Management",
    "PostHog",
    "Quicknode",
    "QRCM",
    "Railway",
    "Remote Desktop Commander",
    "Resend",
    "Retell AI",
    "Semrush",
    "SharePoint",
    "Sites",
    "Slack",
    "Stripe",
    "Supabase",
    "Todoist: To Do List & Calendar",
    "Vercel",
    "Webflow",
    "Windsor.ai",
    "WorkOS",
    "Zoho CRM",
    "Zoom",
)


USER_MANAGED_CONNECTORS: tuple[tuple[str, str, str], ...] = (
    ("github", "GitHub / GitHub App", "short_lived_federation"),
    ("forgejo", "Forgejo", "dual_token"),
    ("gitea", "Gitea", "dual_token"),
    ("cloudflare", "Cloudflare", "dual_token"),
    ("stripe", "Stripe", "dual_token"),
    ("digitalocean", "DigitalOcean", "dual_token"),
    ("tailscale", "Tailscale", "short_lived_federation"),
    ("netlify", "Netlify", "dual_token"),
    ("vercel", "Vercel", "dual_token"),
    ("railway", "Railway", "dual_token"),
    ("supabase", "Supabase", "dual_token"),
    ("openai", "OpenAI", "dual_token"),
    ("huggingface", "Hugging Face", "dual_token"),
    ("slack", "Slack", "short_lived_federation"),
    ("resend", "Resend", "dual_token"),
    ("posthog", "PostHog", "dual_token"),
    ("quicknode", "Quicknode", "dual_token"),
    ("godaddy", "GoDaddy", "dual_token"),
    ("npm", "npm", "dual_token"),
    ("pypi", "PyPI", "dual_token"),
    ("docker", "Docker / OCI registry", "dual_token"),
    ("aws", "AWS", "short_lived_federation"),
    ("google-cloud", "Google Cloud", "short_lived_federation"),
    ("azure", "Microsoft Azure", "short_lived_federation"),
    ("ssh", "SSH", "authorized_key_overlap"),
    ("wireguard", "WireGuard", "authorized_key_overlap"),
    ("postgres", "PostgreSQL", "dual_database_identity"),
    ("mysql", "MySQL", "dual_database_identity"),
    ("mongodb", "MongoDB", "dual_database_identity"),
    ("redis", "Redis", "dual_database_identity"),
    ("oauth2", "OAuth 2.0 client", "short_lived_federation"),
    ("webhook", "Webhook signing secret", "dual_validation_window"),
    ("x509", "X.509 / TLS certificate", "certificate_overlap"),
    ("jwt-signing", "JWT signing key", "key_ring_migration"),
    ("encryption-key", "Encryption key", "key_ring_migration"),
    ("application-secret", "Application-owned symmetric secret", "versioned_secret"),
    ("custom", "Custom connector adapter", "dual_token"),
)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def connector_catalog() -> dict[str, Any]:
    managed = [
        {
            "id": f"app:{_slug(name)}",
            "name": name,
            "authority": "host_managed",
            "strategy": "host_managed_oauth",
            "risk_default": "high",
            "local_rotation": "prohibited",
            "execution_plane": "connector_host",
        }
        for name in HOST_MANAGED_CONNECTORS
    ]
    user_managed = [
        {
            "id": connector_id,
            "name": name,
            "authority": "user_managed",
            "strategy": strategy,
            "risk_default": "critical" if connector_id in {"github", "cloudflare", "stripe", "aws", "encryption-key", "jwt-signing"} else "high",
            "local_rotation": "prohibited",
            "execution_plane": "connector_adapter",
        }
        for connector_id, name, strategy in USER_MANAGED_CONNECTORS
    ]
    return {
        "schema_version": 2,
        "catalog_date": "2026-09-09",
        "strategies": STRATEGIES,
        "managed_connectors": managed,
        "user_managed_connectors": user_managed,
        "counts": {"managed": len(managed), "user_managed": len(user_managed)},
    }


def known_user_connector_ids() -> set[str]:
    return {item[0] for item in USER_MANAGED_CONNECTORS}
