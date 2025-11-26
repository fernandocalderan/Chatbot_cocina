# Backups (Manual & Policy Reference)

Este directorio documenta comandos manuales de backup/restore y las políticas declaradas en Terraform (infra/aws).

## Backups manuales (local/staging)

Requiere `pg_dump`, `psql` y variables de entorno: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`.

```bash
# Backup completo
pg_dump -Fc -h "$PGHOST" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" > backup_$(date +%Y%m%d_%H%M).dump

# Restaurar desde backup
pg_restore -c -h "$PGHOST" -p "${PGPORT:-5432}" -U "$PGUSER" -d "$PGDATABASE" backup_YYYYMMDD_HHMM.dump
```

Redis (AOF/RDB) se maneja desde configuración del servicio; no copiar claves sensibles.

## S3 / archivos

Para copiar backups locales a un bucket (usar credenciales AWS válidas):

```bash
aws s3 cp backup_YYYYMMDD_HHMM.dump s3://<bucket>/db-backups/
```

## Políticas automatizadas (Terraform, referencias)

- RDS: `backup_retention_period`, `backup_window` declarados en `infra/aws/main.tf` (comentado, activar en despliegue).
- S3: versionado habilitado y `lifecycle_rule` para pdfs (180 días), temp (30 días), logs (14 días).

## Restauración básica (RDS)

Usar snapshot RDS desde consola/CLI, o descargar `.dump` y restaurar con `pg_restore` apuntando al endpoint RDS.

> Nota: No incluir credenciales reales aquí. Configurar en el entorno seguro (AWS/Render/GitHub Secrets).
