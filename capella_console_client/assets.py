from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Union, Dict, Any
import re

import httpx
import rich.progress

from capella_console_client.logconf import logger
from capella_console_client.exceptions import ConnectError


@dataclass
class DownloadRequest:
    url: str
    local_path: Optional[Path] = None
    asset_key: str = "asset"
    stac_id: str = ""


progress_bar = rich.progress.Progress(
    rich.progress.TextColumn("[bold blue]{task.fields[filename]}", justify="left"),
    rich.progress.BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    rich.progress.DownloadColumn(),
    "•",
    rich.progress.TransferSpeedColumn(),
    "•",
    rich.progress.TimeRemainingColumn(),
)


def _flush_progress_bar(progress: rich.progress.Progress) -> None:
    for task_id in progress.task_ids:
        progress.remove_task(task_id)


def _gather_download_requests(
    assets_presigned: Dict[str, Any],
    local_dir: Union[Path, str] = Path(tempfile.gettempdir()),
    include: Union[List[str], str] = None,
    exclude: Union[List[str], str] = None,
    separate_dirs: bool = True,
) -> List[DownloadRequest]:
    local_dir = Path(local_dir)
    assert local_dir.exists(), f"{local_dir} does not exist"

    stac_id = _derive_stac_id(assets_presigned)

    if separate_dirs:
        local_dir /= stac_id
        local_dir.mkdir(exist_ok=True)

    logger.info(f"downloading product {stac_id} to {local_dir}")
    if include:
        include = _prep_include_exclude(include)
        logger.info(f"Only including assets {', '.join(include)}")

    if exclude:
        exclude = _prep_include_exclude(exclude)
        logger.info(f"Excluding assets {', '.join(exclude)}")

    # gather up paths
    download_requests = []
    for key, asset in assets_presigned.items():
        # white-listing
        if include and key not in include:
            continue

        # black-listing
        if exclude and key in exclude:
            continue

        local_path = local_dir / _get_filename(asset["href"])
        download_requests.append(
            DownloadRequest(
                stac_id=stac_id,
                asset_key=key,
                url=asset["href"],
                local_path=local_path,
            )
        )
    return download_requests


def _derive_stac_id(assets_presigned: Dict[str, Any]) -> str:
    raster_asset = assets_presigned.get("HH")
    if raster_asset is None:
        raster_asset = assets_presigned["VV"]

    STAC_ID_REGEX = re.compile("^.*(CAPELLA_C\\d{2}_\\w+_\\w+_\\d{14}_\\d{14}).*$")
    return STAC_ID_REGEX.findall(raster_asset["href"])[0]


def _prep_include_exclude(filter_stmnt: Union[str, List[str]]) -> List[str]:
    if isinstance(filter_stmnt, str):
        filter_stmnt = [filter_stmnt]

    if "raster" in filter_stmnt:
        filter_stmnt.extend(["HH", "VV"])
        filter_stmnt.pop(filter_stmnt.index("raster"))

    return list(set(filter_stmnt))


def _perform_download(
    download_requests: List[DownloadRequest],
    override: bool,
    threaded: bool,
    verbose: bool,
    show_progress: bool = False,
) -> Dict[str, Path]:

    local_paths_by_key = {}

    with progress_bar as progress:

        _flush_progress_bar(progress)

        # serially
        if not threaded:
            for dl_request in download_requests:
                local_paths_by_key[dl_request.asset_key] = _download_asset(
                    dl_request,
                    override=override,
                    verbose=verbose,
                    show_progress=show_progress,
                    progress=progress,
                )

        # threaded
        else:
            with ThreadPoolExecutor(max_workers=len(download_requests)) as executor:
                # Start the load operations and mark each future with its URL
                futures_by_key = {}

                for dl_request in download_requests:
                    futures_by_key[dl_request.asset_key] = executor.submit(
                        _download_asset,
                        dl_request=dl_request,
                        override=override,
                        verbose=verbose,
                        show_progress=show_progress,
                        progress=progress,
                    )

            for key, fut in futures_by_key.items():
                local_paths_by_key[key] = fut.result()

    return local_paths_by_key


def _download_asset(
    dl_request: DownloadRequest,
    override: bool,
    verbose: bool,
    show_progress: bool,
    progress: rich.progress.Progress,
) -> Path:
    local_path = dl_request.local_path
    if local_path is None:
        local_file = _get_filename(dl_request.url)
        local_path = Path(tempfile.gettempdir()) / local_file

    local_path = Path(local_path)

    if not override and local_path.exists():
        logger.info(f"already downloaded to {local_path}")
        return local_path

    suffix = ""

    try:
        asset_size = _get_asset_bytesize(dl_request.url)
        suffix += f"({_sizeof_fmt(asset_size)})"
    except Exception:
        # logger.warning(f"Couldn't derive size of {local_path.name} ... that's ok")
        asset_size = -1

    if not show_progress:
        logger.info(f"downloading to {local_path} {suffix}")

    try:
        with open(local_path, "wb") as f:
            with httpx.stream("GET", dl_request.url) as response:
                if show_progress:
                    download_task_id = _register_progress_task(
                        dl_request, progress, asset_size
                    )

                for chunk in response.iter_bytes():
                    f.write(chunk)

                    if show_progress:
                        progress.update(
                            download_task_id, completed=response.num_bytes_downloaded
                        )
    except httpx.ConnectError as e:
        raise ConnectError(f"Could not connect to {dl_request.url}: {e}") from None

    if not show_progress:
        logger.info(f"successfully downloaded to {local_path}")

    return local_path


def _register_progress_task(
    dl_request: DownloadRequest, progress: rich.progress.Progress, asset_size: int
) -> rich.progress.TaskID:
    file_name_str = str(dl_request.local_path)
    if dl_request.local_path and isinstance(dl_request.local_path, Path):
        file_name_str = dl_request.local_path.name
    download_task_id = progress.add_task(
        "Download", total=asset_size, filename=file_name_str
    )
    return download_task_id


def _get_filename(pre_signed_url: str) -> str:
    return Path(urlparse(pre_signed_url).path).name


def _get_asset_bytesize(pre_signed_url: str) -> int:
    """get size in bytes of `pre_signed_url`"""
    try:
        with httpx.stream("GET", pre_signed_url) as resp:
            total_size = int(resp.headers["Content-Length"])
    except httpx.ConnectError as e:
        raise ConnectError(f"Could not connect to {pre_signed_url}: {e}") from None
    return total_size


def _sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"