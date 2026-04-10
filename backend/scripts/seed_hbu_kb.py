from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import httpx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app.core.config import settings

def get_admin_credentials() -> tuple[str, str]:
    username = str(settings.admin_username or '').strip()
    password = str(settings.admin_password or '').strip()
    if not username or not password:
        raise SystemExit('admin credentials are not configured in backend/.env')
    return username, password


SEED_DIR = ROOT / 'data' / 'seed_kb' / 'hebei_university'


def iter_seed_files() -> list[Path]:
    files = sorted(SEED_DIR.glob('*.md'))
    if not files:
        raise FileNotFoundError(f'seed files not found under {SEED_DIR}')
    return files


def _seed_doc_names() -> set[str]:
    return {path.name for path in iter_seed_files()}


def seed_local_documents(
    kb_id: int = 1,
    ensure_bootstrap: bool = True,
    force_reindex: bool = False,
) -> dict[str, int]:
    from app.services.bootstrap_service import bootstrap_database
    from app.services.document_service import document_service
    from app.services.ingest_service import ingest_service
    from app.services.kb_service import kb_service

    if ensure_bootstrap:
        bootstrap_database()

    known_kb_ids = {int(item['id']) for item in kb_service.list_kb()}
    if kb_id not in known_kb_ids:
        created = kb_service.create_kb(
            name='河北大学官方知识库',
            description='河北大学官网公开资料整理，用于校园知识问答与检索测试。',
        )
        kb_id = int(created['id'])

    existing = {
        str(item.get('file_name', '')): item
        for item in document_service.list_documents(kb_id=kb_id)
    }

    created_count = 0
    skipped_count = 0
    reindexed_count = 0

    for path in iter_seed_files():
        content = path.read_bytes()
        current = existing.get(path.name)
        if current and str(current.get('status')) == 'indexed' and not force_reindex:
            skipped_count += 1
            continue

        if current:
            ingest_service.ingest_document(
                kb_id=kb_id,
                document_id=int(current['id']),
                file_ext='md',
                content=content,
            )
            reindexed_count += 1
            continue

        doc = document_service.create_document(
            kb_id=kb_id,
            file_name=path.name,
            file_size=len(content),
            file_ext='md',
            mime_type='text/markdown',
            storage_path=str(path.resolve()),
        )
        ingest_service.ingest_document(
            kb_id=kb_id,
            document_id=int(doc['id']),
            file_ext='md',
            content=content,
        )
        created_count += 1

    return {
        'kb_id': kb_id,
        'created': created_count,
        'reindexed': reindexed_count,
        'skipped': skipped_count,
    }


def seed_via_api(
    base_url: str,
    username: str,
    password: str,
    kb_id: int = 1,
    force_reindex: bool = False,
) -> dict[str, int]:
    seed_names = _seed_doc_names()
    base = str(base_url or '').rstrip('/')
    if not base:
        raise ValueError('base_url is required in api mode')

    with httpx.Client(base_url=base, timeout=30.0) as client:
        login = client.post(
            '/api/admin/auth/login',
            json={'username': username, 'password': password},
        )
        login.raise_for_status()
        token = login.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        listed = client.get('/api/admin/documents', headers=headers, params={'kb_id': kb_id})
        listed.raise_for_status()
        existing = {
            str(item.get('file_name', '')): item
            for item in (listed.json().get('items') or [])
            if str(item.get('file_name', '')) in seed_names
        }

        created_count = 0
        skipped_count = 0
        deleted_count = 0

        for path in iter_seed_files():
            current = existing.get(path.name)
            if current and str(current.get('status')) == 'indexed' and not force_reindex:
                skipped_count += 1
                continue

            if current and force_reindex:
                deleted = client.delete(f"/api/admin/documents/{int(current['id'])}", headers=headers)
                deleted.raise_for_status()
                deleted_count += 1

            with path.open('rb') as fh:
                resp = client.post(
                    '/api/admin/documents/upload',
                    headers=headers,
                    data={'kb_id': str(kb_id)},
                    files={'file': (path.name, fh, 'text/markdown')},
                )
            resp.raise_for_status()
            created_count += 1

    return {
        'kb_id': kb_id,
        'created': created_count,
        'skipped': skipped_count,
        'deleted': deleted_count,
    }


def main() -> None:
    admin_username, admin_password = get_admin_credentials()
    parser = argparse.ArgumentParser(description='Seed 河北大学官方知识库种子文档')
    parser.add_argument('--kb-id', type=int, default=1)
    parser.add_argument('--base-url', default='', help='If provided, upload through admin API instead of local services')
    parser.add_argument('--username', default=admin_username)
    parser.add_argument('--password', default=admin_password)
    parser.add_argument('--force-reindex', action='store_true')
    args = parser.parse_args()

    if args.base_url:
        result = seed_via_api(
            base_url=args.base_url,
            username=args.username,
            password=args.password,
            kb_id=args.kb_id,
            force_reindex=args.force_reindex,
        )
        print(
            f"seeded via api kb_id={result['kb_id']} created={result['created']} skipped={result['skipped']} deleted={result.get('deleted', 0)}"
        )
        return

    result = seed_local_documents(
        kb_id=args.kb_id,
        ensure_bootstrap=True,
        force_reindex=args.force_reindex,
    )
    print(
        'seeded locally '
        f"kb_id={result['kb_id']} created={result['created']} reindexed={result['reindexed']} skipped={result['skipped']}"
    )


if __name__ == '__main__':
    main()
