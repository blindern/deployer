from dataclasses import dataclass


@dataclass
class Service:
    service_name: str
    ansible_tag: str
    ansible_host: str
    # Entries that belong to this service.
    # api-value => deployer.json key
    mappings: dict[str, str]


SERVICES: dict[str, Service] = {
    "confluence": Service(
        service_name="confluence",
        ansible_tag="service-confluence",
        ansible_host="fcos-1",
        mappings={
            "image": "deployer_confluence_image",
        },
    ),
    "deployer-primary": Service(
        service_name="deployer-primary",
        ansible_tag="service-deployer-primary",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_deployer_primary_image",
        },
    ),
    "deployer-secondary": Service(
        service_name="deployer-secondary",
        ansible_tag="service-deployer-secondary",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_deployer_secondary_image",
        },
    ),
    "dugnaden": Service(
        service_name="dugnaden",
        ansible_tag="service-dugnaden",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_dugnaden_image",
        },
    ),
    "ldap-master": Service(
        service_name="ldap-master",
        ansible_tag="service-ldap-master",
        ansible_host="fcos-2",
        mappings={
            "image": "deployer_ldap_master_image",
        },
    ),
    "ldap-slave": Service(
        service_name="ldap-slave",
        ansible_tag="service-ldap-slave",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_ldap_slave_image",
        },
    ),
    "nginx-front-1": Service(
        service_name="nginx-front-1",
        ansible_tag="service-nginx-front-1",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_nginx_front_1_image",
        },
    ),
    "okoreports": Service(
        service_name="okoreports",
        ansible_tag="service-okoreports",
        ansible_host="fcos-2",
        mappings={
            "backend_image": "deployer_okoreports_backend_image",
            "frontend_image": "deployer_okoreports_frontend_image",
        },
    ),
    "simplesamlphp": Service(
        service_name="simplesamlphp",
        ansible_tag="service-simplesamlphp",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_simplesamlphp_image",
        },
    ),
    "slack-invite-automation": Service(
        service_name="slack-invite-automation",
        ansible_tag="service-slack-invite-automation",
        ansible_host="fcos-2",
        mappings={
            "image": "deployer_slack_invite_automation_image",
        },
    ),
    "smaabruket-availability-api": Service(
        service_name="smaabruket-availability-api",
        ansible_tag="service-smaabruket-availability-api",
        ansible_host="fcos-2",
        mappings={
            "image": "deployer_smaabruket_availability_api_image",
        },
    ),
    "uka-billett": Service(
        service_name="uka-billett",
        ansible_tag="service-uka-billett",
        ansible_host="fcos-1",
        mappings={
            "proxy_image": "deployer_uka_billett_proxy_image",
            "fpm_image": "deployer_uka_billett_fpm_image",
            "frontend_image": "deployer_uka_billett_frontend_image",
        },
    ),
    "uka-webserver": Service(
        service_name="uka-webserver",
        ansible_tag="service-uka-webserver",
        ansible_host="fcos-1",
        mappings={
            "image": "deployer_uka_webserver_image",
        },
    ),
    "users-api": Service(
        service_name="users-api",
        ansible_tag="service-users-api",
        ansible_host="fcos-2",
        mappings={
            "image": "deployer_users_api_image",
        },
    ),
    "web-1": Service(
        service_name="web-1",
        ansible_tag="service-web-1",
        ansible_host="fcos-3",
        mappings={
            "image": "deployer_web_1_image",
        },
    ),
}
