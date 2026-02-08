# deployer

This is a service that automates deployment of our services
so that the services themself can trigger a deployment while still
preserving least privileges (e.g. not having root accesses).

It will update and deploy the Ansible playbook defined in
https://github.com/blindern/drift/tree/main/ansible

The service exposes a JSON API that is used like this:

```text
POST /deploy
{
  "service": "service-name",
  "attributes": {
    "image": "hello-world"
  },
  "forceDeploy": false
}
```

Configured services is located at
https://github.com/blindern/drift/blob/main/ansible/roles/service-deployer/files/services.json

The request will block until it has completed deployment.
On failure a 500 error will be given.

Authorization is based on pre-configured tokens.

## Development

This has been built with Python 3.13.

You need `uv`. See https://docs.astral.sh/uv/

Copy `.env.template` to `.env` and modify it to your needs.

### GitHub App setup

Git auth uses a GitHub App that generates short-lived HTTPS tokens.

Two apps exist:
- **fbs-deployer** (app ID `2824237`, installation `108887063`) — installed on `blindern/drift` (production)
- **fbs-deployer-test** (app ID `2824239`, installation `108886929`) — installed on `blindern/deployer-test` (CI/testing)

To set up locally:
1. Download the private key PEM file for the relevant GitHub App
2. Set env vars in `.env`:
   - `GITHUB_APP_ID` — the App ID
   - `GITHUB_APP_PRIVATE_KEY_PATH` — path to the PEM file
   - `GITHUB_APP_INSTALLATION_ID` — the installation ID
3. Required App permission: **Contents: Read & write**

You also need root access to all the servers (for Ansible).

```bash
uv sync
FLASK_APP=deployer.app uv run flask run
```

To run tests:

```bash
uv run pytest
```

Lint/fix all files:

```bash
uv run pre-commit run --all-files
```

### Testing locally

```bash
curl -i -H "authorization: bearer abc" -H "content-type: application/json" -X POST http://localhost:5000/deploy -d '
{
  "service": "CHANGEME",
  "attributes": {
    "image": "CHANGEME"
  }
}'
```

## How a deployment is done

When the application is invoked it will:

1. Pull `drift` repo
1. Check if config actually changes - abort if not (same version) - this will give a OK response
1. Bump config value
1. Deploy Ansible playbook with specific tag
1. Commit and push changes

The application is run as a single instance, and keeps a lock
to prevent concurrent deployments of the same service.
