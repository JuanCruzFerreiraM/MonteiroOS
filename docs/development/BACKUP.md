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

Restoration refuses the primary application database and the maintenance databases `postgres`, `template0`, and `template1`. The primary name is the shell's `POSTGRES_DB` when that is set, otherwise `POSTGRES_DB` in the repository `.env`, otherwise `monteiro`. That is the same order Docker Compose uses. Restoration also refuses a target that already exists, so it will not merge a dump into a database that already has data. It never drops a database.

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

`scripts/verify-backup-restore.sh` checks that a probe row survives `pg_dump` and `pg_restore`. It does not use fixed database names.

Each run allocates two identifiers, `core01_probe_src_...` and `core01_probe_dst_...`. Before creating either one, it asks PostgreSQL whether that name already exists. A name that exists, or that matches the primary or a maintenance database, is left untouched and the script tries another identifier. If it cannot find a free name, it stops. It does not drop an existing database to make room.

The script records a database only after that run has created it. On success, failure, or an interrupt, cleanup drops only the names on that list. A database created by an earlier run, or by someone else, is not on the list and is not dropped.

One limitation remains. `scripts/db-restore.sh` creates the empty target and then runs `pg_restore`. If `pg_restore` fails after that create, the verifier has not yet recorded the target, so it leaves the empty database in place. An interrupted run can do the same. Inspect a leftover `core01_probe_*` database before dropping it, and drop it only when you recognize it as yours. Leaving it is safer than deleting a database the script cannot prove it created.

The probe dump is a unique file under `backups/` and is removed when the script exits. The probe table is not created in the primary database and it is not a migration.

```bash
scripts/verify-backup-restore.sh
```

## Compatibility

- The dump and the server are both PostgreSQL 18. A client older than the server cannot be assumed to restore the file.
- `--no-owner` and `--no-acl` keep the restore from depending on roles that exist only in the source cluster.
- Custom format is for `pg_restore`, not for `psql`.
- The procedure dumps whole databases. When domain tables exist, they are included without a separate backup path.

## Local ports

Compose publishes PostgreSQL, the API, and the web app on `127.0.0.1` only. A backup taken on the host still uses the Compose service, not a publicly reachable database port.
