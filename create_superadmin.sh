#!/bin/bash

set -e

TENANT_ID="11111111-1111-1111-1111-111111111111"
EMAIL="fernandocalderan@gmail.com"
PASSWORD_RAW="e42f9a93c0ed1c29b3aa4d5aa5d2b514"

PY_BIN="python3"
if [ -x "backend/.venv/bin/python3" ]; then
  PY_BIN="backend/.venv/bin/python3"
fi

echo "🔧 Generando hash bcrypt..."
HASH=$($PY_BIN - <<PY
import bcrypt
pw = b"$PASSWORD_RAW"
print(bcrypt.hashpw(pw, bcrypt.gensalt()).decode())
PY
)

echo "🔐 Hash generado:"
echo "$HASH"
echo ""

echo "🏗️  Creando tenant si no existe..."
docker exec chatbot_db psql -U postgres -d chatbot -c "
insert into tenants (id, name, plan)
values ('$TENANT_ID','Tenant Demo','BASE')
on conflict (id) do nothing;
"

echo "👤 Insertando usuario superadmin..."

docker exec chatbot_db psql -U postgres -d chatbot -c "
insert into users (tenant_id, email, hashed_password, role)
values ('$TENANT_ID', '$EMAIL', '$HASH', 'ADMIN')
on conflict (tenant_id, email) do nothing;
"

echo ""
echo "🎉 SUPERADMIN CREADO CON ÉXITO"
echo "--------------------------------------------"
echo "Email:       $EMAIL"
echo "Password:    $PASSWORD_RAW"
echo "Tenant ID:   $TENANT_ID"
echo "User ID:     user-superadmin"
echo "--------------------------------------------"
echo "Ahora puedes iniciar sesión en el panel."
