#!/bin/bash

cp -r $1 tmp_profile
rm -rf tmp_profile/browser-extension-data
rm -rf tmp_profile/hrome_debugger_profile
rm -rf tmp_profile/domain_to_categories.sqlite
rm -rf tmp_profile/domain_to_categories.sqlite-journal
rm -rf tmp_profile/favicons.sqlite-shm
rm -rf tmp_profile/features
rm -rf tmp_profile/logins.db
rm -rf tmp_profile/places_semantic.sqlite
rm -rf tmp_profile/places_semantic.sqlite-wal
rm -rf tmp_profile/places.sqlite-shm
rm -rf tmp_profile/ssl_tokens_cache.bin
rm -rf tmp_profile/storage
rm -rf tmp_profile/storage-sync-v2.sqlite
rm -rf tmp_profile/storage-sync-v2.sqlite-shm
rm -rf tmp_profile/storage-sync-v2.sqlite-wal
rm -rf tmp_profile/tabnotes.sqlite
rm -rf tmp_profile/tabnotes.sqlite-wal
rm -rf tmp_profile/targeting.snapshot.json
rm -rf tmp_profile/weave
cd tmp_profile; zip -9r ../profile.zip .; cd ..;
