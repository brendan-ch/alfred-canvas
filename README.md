# Alfred-Canvas

Access Canvas classes, announcements, modules, and more through Alfred. Note that as of right now, this workflow requires you to manually get an API key from Canvas, which is a violation of their terms of service. Please use this workflow at your own risk.

## Setup

1. Import the workflow into Alfred.
2. Obtain an access key by logging into your Canvas page. On the left, click on "Account", then "Settings" after that. Scroll down until you see "Approved Integrations", then click on New Access Token to generate a new key.
3. Use `canvas !save_api_key [key]` to save the key.
4. While on this page, look at the URL bar and note the URL used by your institution for accessing Canvas. It should be similar to this: `[something].canvas.com`.
5. Use `canvas !set_url [url]` to save this URL. This step is required for full functionality of the workflow.

## Usage

- `canvas`: List all classes marked as favorites. You can action these classes to browse through announcements, assignments, modules, and files.
- `canvas !clear_cache`: Clear the workflow cache.
- `canvas !set_url [url]`: Change the URL used by your institution. The URL defaults to `canvas.instructure.com`; however, opening links will not work without entering the institution-specific URL.
- `canvas !save_api_key [key]`: Saves the access token generated from the Canvas website.