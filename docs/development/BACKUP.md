# Database backup and restore

CORE-01 uses PostgreSQL 18 tools already present in the Compose `db` service. `scripts/db-backup.sh` runs `pg_dump` in custom format. `scripts/db-restore.sh` runs `pg_restore` into a different, empty database. There is no scheduler, cloud storage, or external backup service.

## What is stored

Dump files are written where the command says, usually under `backups/` in the repository. That directory is gitignored. A dump contains the chosen database at the moment of the backup. It does not contain the deployment secret or the contents of `.env`.

## Credentials

The scripts talk to the database through `docker compose exec` on the `db` container. PostgreSQL reads `POSTGRES_USER` and the local socket inside that container. The scripts do not take a password argument and do not print one. Keep `.env` uncommitted. Do not paste a connection URL into a ticket or a shell history you intend to share.

## Create a backup

From the repository root, with Compose up:

```bash
scripts/db-backup.sh monteiro backups/monteiro-$(date +%Y%m%d).dump
```

Replace `monteiro` if `POSTGRES_DB` is different. The file is a PostgreSQL custom-format dump produced by the same major version as the server.

## Restore into an empty database

Restoration refuses the primary application database (`POSTGRES_DB`, default `monteiro`) and the maintenance databases `postgres`, `template0`, and `template1`. It also refuses a target that already exists, so it will not merge a dump into a database that already has data.

```bash
scripts/db-restore.sh backups/monteiro-20261116.dump monteiro_restore_check
```

The target name must be a plain identifier: letters, digits, and underscores.

Read the restored database back, then drop only the check database when you are finished with it:

```bash
docker compose exec db psql --username "$POSTGRES_USER" --dbname monteiro_restore_check -c '\dt'
docker compose exec db psql --username "$POSTGRES_USER" --dbname postgres -c 'DROP DATABASE monteiro_restore_check WITH (FORCE)'
```

If `POSTGRES_USER` is unset on the host, run the `psql` command without interpolating it and let the container environment supply the user:

```bash
docker compose exec db sh -c 'psql --username "$POSTGRES_USER" --dbname monteiro_restore_check -c "\dt"'
```

Do not point `pg_restore` at the primary database by hand. A failed restore can leave the new empty target behind; drop that target, not `monteiro`.

## Verify a round trip

`scripts/verify-backup-restore.sh` creates two throwaway databases, writes one probe row, dumps the source, restores it into the other database, and reads the row back. It then checks that the probe table is absent from the primary database and drops both throwaway databases. It does not modify the development database.

```bash
scripts/verify-backup-restore.sh
```

The probe table exists only inside those throwaway databases. It is not an application table and it is not a migration.

## Compatibility

- The dump and the server are both PostgreSQL 18. A client older than the server cannot be assumed to restore the file.
- `--no-owner` and `--no-acl` keep the restore from depending on roles that exist only in the source cluster.
- Custom format is for `pg_restore`, not for `psql`.
- The procedure dumps whole databases. When domain tables exist, they are included without a separate backup path.

## Local ports

Compose publishes PostgreSQL, the API, and the web app on `127.0.0.1` only. A backup taken on the host still uses the Compose service, not a publicly reachable database port.
