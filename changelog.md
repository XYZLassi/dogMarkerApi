# Changelog

## Develop
- Fix #11: Trash not working for own entries
- Add: create_date and update_date to hidden_entries
- Add: Add update update_date if delete or undo delete
- Add: EntryDbModel.is_deleted

## v0.4.3
- Fix: Dependencies for user_entries
- Fix: owner deleted in user trash

## v0.4.2
- Remove: Test :)

## v0.4.1
- Remove: mark_to_delete_flag

## v0.4
- Add: Undo deleted entries
- Refactor: EntryCRUD
- Add: Trash for entries

## v0.3

- Add: Entity-Categories
- Add: WarningLevels

## v0.2.1

- Fix: image_delete_url for non owner-users in get_all_entries
- Change: Dockerfile to 3.11-alpine
- Update: .github/workflows/docker-image.yml

## v0.2
- Add: EntryImageDbModel
- Add: Charset in content-type
- Add: App-Token authentication
- Refactor: query_pagination
- Fix: Add timezones for entries
- Add: date_from in get_all_entries
- Add-Config: POSTGRES_DB_POOL_SIZE and POSTGRES_DB_MAX_OVERFLOW

## v0.1.1
- Fix: image_delete_url for non owner-users

## v0.1
- Initialize Version
