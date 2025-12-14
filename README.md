[![Tests](https://github.com/aleks-iv/ckanext-scientometrics/workflows/Tests/badge.svg?branch=main)](https://github.com/aleks-iv/ckanext-scientometrics/actions)

# ckanext-scientometrics

Scientometrics metrics for CKAN users. The extension lets you:

- store author identifiers (per source) in user extras (`plugin_extras`)
- fetch author-level metrics from external providers
- persist fetched metrics in dedicated DB tables
- display selected metrics on the user page

Supported sources (as implemented):

- Google Scholar (author profile metrics)
- Semantic Scholar (author metrics)
- OpenAlex (author metrics)

## How it works

- User author identifiers are stored in the user `plugin_extras` under `scim`:
  keys like `<source>_author_id` (e.g. `google_scholar_author_id`).
- Metrics are fetched via per-source extractors and stored in:
  - `scim_user_metric` (per user + source)
  - `scim_dataset_metric` (reserved for dataset metrics; currently only model/migration exist)
- The user page template can render cards for enabled sources using the stored metrics.

## Usage

### 1) Configure enabled sources

Enable the plugin in CKAN config:

```ini
ckan.plugins = ... scientometrics
```

Configure which metric sources are enabled:

```ini
ckanext.scientometrics.enabled_metrics = google_scholar semantic_scholar openalex
ckanext.scientometrics.show_on_user_page = true
```

### 2) Add author IDs to a user

In the user edit form, the extension adds extra fields (one per enabled source).
The values are stored under `plugin_extras["scim"]` as:

- `google_scholar_author_id`
- `semantic_scholar_author_id`
- `openalex_author_id`

### 3) Update metrics for a user (action)

The extension provides actions to fetch and store metrics. A typical call:

- `scim_update_user_metrics` with:
  - `user_id` (id or name)
  - `requested_sources` (optional list of sources; defaults to enabled sources)

Stored records are keyed by `(user_id, source)` in `scim_user_metric`.

To retrieve stored metrics:

- `scim_get_user_metrics` with:
  - `user_id`

Returns a dict keyed by `source`, where each value is built from the stored JSON metrics
plus metadata like status and external references (when present).

### 4) Update metrics for all users (CLI)

The extension exposes a CLI command:

```bash
ckan scim update-user-metrics
```

Options:

- `--user-ids <id>` (repeatable): update only specified user IDs
- `--requested-sources <source>` (repeatable): update only specified sources

If no `--user-ids` are provided, it updates all users.

## Database

This extension creates two tables:

- `scim_user_metric`
  - unique constraint: `(user_id, source)`
  - stores:
    - `metrics` (JSONB)
    - `external_id`, `external_url`
    - `status`
    - timestamps
    - `extras` (JSONB for future metadata)

- `scim_dataset_metric`
  - unique constraint: `(package_id, source)`
  - same structure as user metrics table

Foreign keys are configured with `ondelete="CASCADE"`.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no    |
| 2.10+           | yes    |

(Tests run in CI on a CKAN 2.11 container.)

## Installation

To install ckanext-scientometrics:

1. Activate your CKAN virtual environment, for example:

   ```bash
   . /usr/lib/ckan/default/bin/activate
   ```

2. Clone the source and install it on the virtualenv:

   ```bash
   git clone https://github.com/aleks-iv/ckanext-scientometrics.git
   cd ckanext-scientometrics
   pip install -e .
   pip install -r requirements.txt
   ```

3. Add `scientometrics` to the `ckan.plugins` setting in your CKAN config file
   (by default `/etc/ckan/default/ckan.ini`).

4. Restart CKAN (eg on Ubuntu + Apache):

   ```bash
   sudo service apache2 reload
   ```

## Config settings

- `ckanext.scientometrics.enabled_metrics` (type: list)
  - default: `google_scholar semantic_scholar openalex`
  - enabled sources; controls which user fields are shown and which sources can be updated

- `ckanext.scientometrics.show_on_user_page` (type: bool)
  - default: `true`
  - show metrics cards on the user page

Example:

```ini
ckan.plugins = ... scientometrics

ckanext.scientometrics.enabled_metrics = openalex semantic_scholar
ckanext.scientometrics.show_on_user_page = true
```

## Developer installation

To install for development:

```bash
git clone https://github.com/aleks-iv/ckanext-scientometrics.git
cd ckanext-scientometrics
pip install -e .
pip install -r dev-requirements.txt
```

## Tests

To run tests:

```bash
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
