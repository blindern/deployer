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

This has been built with Python 3.12.

You need Poetry. See https://python-poetry.org/docs/#installation

Copy `.env.template` to `.env` and modify it to your needs.

You need to have a SSH key active that can be used to pull and push the `drift` repo,
as well as having root access to all the servers (for Ansible).

```bash
poetry install
FLASK_APP=deployer.app poetry run flask run
```

To run tests:

```bash
poetry run pytest
```

Lint/fix all files:

```bash
poetry run pre-commit run --all-files
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
