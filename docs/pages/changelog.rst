=======
History
=======

0.1.0 (2021-01-14)
------------------

* search and order APIs


0.2.0 (2021-01-21)
------------------

* download APIs
* unit test suite
* CI & packaging

0.2.1 (2021-01-28)
------------------

* client instantiation with JWT token

0.2.2 (2021-01-28)
------------------

* custom exceptions for auth, search, order, download

0.2.3 (2021-02-03)
------------------

* hardening error handling for custom API error responses

0.2.4 (2021-02-08)
------------------

* token auth -> no_token_check boolean
* submit_order -> check_active_orders boolean


0.2.5 (2021-02-09)
------------------

* option for threaded downloading
* separate API for download_product and download_products


0.2.6 (2021-02-09)
------------------

* include asset key filter for product download
* exclude asset key filter for product download

0.3.0 (2021-02-24)
------------------

* advanced search with __<op>, e.g. look_angle__gt=10


0.3.1 (2021-03-11)
------------------

* hardened pagination logic with retrying.retry

0.3.2 (2021-03-11)
------------------

* sortby support


0.4.0 (2021-03-16)
------------------

* stac id filter for get_presigned_assets
* datetime support
* fixed limit <= 500
* product_download ensure local_dir exists
* improved usage section in README


0.4.1 (2021-05-13)
------------------

* multi environment support (custom catalog base_url)


0.5.0 (2021-06-16)
------------------

* read tasking request information (task request metadata, status)
* derive and download all products associated with tasking request id


0.5.1 (2021-06-17)
------------------

* extend asset include/ exclude filters (single string, raster == HH || VV)
* harden download routine

0.6.0 (2021-06-22)
------------------

* true threading upon client.download_products
* show_progress fanciness
* modularizing assets and search impl
* improving exception handling (INVALID_TOKEN)


0.6.1 (2021-07-07)
------------------

* re-adding client.get_asset_bytesize


0.7.0 (2021-07-12)
------------------

* open sourcing (poetry packaging, docs, lint)
* adding `items` to `submit_order`
* whitelisting additional search fields
* flush progressbar on bulk download
* directly passing in `order_id` into `download_product[s]`


0.7.1 (2021-07-16)
------------------
* upon submitting order: omit search to ensure provided STAC IDs are valid in conjunction with provided items
* routine to retrieve stac items of existing order
* simplistic uuid validation
* split up test suite
* moving download_products_for_task into download_products(tasking_request_id="")
* extending download_products(collect_id="")
* adding `separate_dirs` flag to download_products in order to create one dir per product
* review order


0.7.2 (2021-07-19)
------------------
* prompt for user credentials if not provided
* defaulting threaded=True in download_product[s]


0.7.3 (2021-07-26)
------------------
* omit review call within submit_order


0.7.4 (2021-08-03)
------------------
* download products - filter by product type(s)


0.7.5 (2021-09-22)
------------------
* improved exception handling and non explicit retryable errors
* search speedup (directly search agains <API_GATEWAY>, pagesize 999, rightsizing requested custom limit)


0.7.6 (2021-09-22)
------------------
* searching against API_GATEWAY directly if allowed (determined by lazy HEAD)


0.7.7 (2021-10-07)
------------------
* auto refresh of expired tokens with request retry


0.8.0 (2021-11-17)
------------------
* optional pip installable interactive wizard-like CLI capella-console-wizard


0.8.1 (2021-01-05)
------------------
* configure STAC search endpoint via optional CapellaConsoleClient(search_url="")


0.8.2 (2022-03-11)
------------------
* optional flags for get_presigned_assets: 
    * sort_by: sort presigned assets by provided STAC ID list,
    * assets_only (default==True): return only assets of stac items


0.8.3 (2022-06-07)
------------------
* hardening asset download with retries
* adding py.typed


0.8.4 (2022-08-03)
------------------
* allow preview only download


0.9.0 (2022-08-03)
------------------
* client.search internas to be class based in order to extend functionality of returned SearchResult
* full dependency update
* dropping Python 3.6 support, adding 3.11.0-rc2 support