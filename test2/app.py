import argparse
from functools import partial
import logging
import os

from aiohttp import web

from conf import (
    files_path_on_server,
    link_part_for_download,
    default_path_to_download,
)
from utils import upload_file, download_file


async def upload(request):
    try:
        reader = await request.multipart()
    except KeyError:
        return web.HTTPNotFound(text='Send your file')

    field = await reader.next()

    filename = field.filename.replace(' ', '_').replace('/', '_')
    path = files_path_on_server + filename

    logging.info('Start uploading')

    size = await upload_file(field, path)

    return web.Response(
        text=f'{filename} sized of {size} successfully stored,'
             f' link:{link_part_for_download}{filename}'
    )


async def download(request, storage_dir):
    file_name = request.match_info['file_name']

    if os.path.exists(files_path_on_server + file_name) is False:
        return web.HTTPNotFound(text='file not exists')

    path_from = files_path_on_server + file_name
    path_to = storage_dir + file_name

    logging.info('Start downloading')
    await download_file(path_from, path_to)

    return web.Response(text='File was downloaded')


def process_args():
    parser = argparse.ArgumentParser(
        description='Upload and download file.'
    )
    parser.add_argument(
        '-H', '--host', default='0.0.0.0', help='TCP/IP host for HTTP server.'
    )
    parser.add_argument(
        '-P', '--port', default=8080, help='TCP/IP port for HTTP server.'
    )
    parser.add_argument(
        '-D', '--dir', default=default_path_to_download,
        help='File storage directory.'
    )

    return parser.parse_args()


def main():
    args = process_args()

    logging_level = logging.INFO
    logging.basicConfig(level=logging_level)

    download_handler = partial(
        download, storage_dir=args.dir
    )
    app = web.Application()
    app.add_routes([
        web.post('/upload', upload),
        web.get('/download/{file_name}', download_handler),
    ])
    web.run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
