

ENV=$1

if [ -z "${ENV}" ];
then
    echo "Usage: $0 [development|staging|production]"
    exit 1
fi

source etc/env/${ENV}.env

read -r -d '' CMD <<EOF
{
  "httpMethod": "GET",
  "path": "/status/ok/",
  "body": "",
  "headers": {
    "host": "${APPLICATION_DOMAIN_NAME}"
  }
}
EOF

echo $CMD
