import json
import re
import shlex
from subprocess import run, PIPE
from shutil import which


VERSION_RE = re.compile(r'ffmpeg version (?P<version>.*) Copyright \(c\)')

class BinaryExistsError(Exception):
    pass


ffmpeg_bin = which('ffmpeg')
ffprobe_bin = which('ffprobe')

if not ffmpeg_bin:
    raise BinaryExistsError('ffmpeg not found')

if not ffprobe_bin:
    raise BinaryExistsError('ffprobe not found')


version_run_res = run(('ffmpeg', '-version'), stdout=PIPE, stderr=PIPE, universal_newlines=True)
if version_run_res.returncode == 0:
    bin_version = VERSION_RE.search(version_run_res.stdout).group('version')
else:
    raise ChildProcessError('`ffmpeg -version` failed with exit code {}: {}'.format(
        version_run_res.returncode, version_run_res.stderr))


def add_input_file_to_args(args, file_or_blob):
    if isinstance(file_or_blob, str):
        args.extend(('-i', file_or_blob))
        return False
    elif isinstance(file_or_blob, (bytes, bytearray)):
        args.extend(('-i', 'pipe:0'))
        return True
    else:
        raise ValueError('unexpected input file {}'.format(file_or_blob))


def probe(file_or_blob, options=('-show_format',)):
    args = [ffprobe_bin, '-v', 'quiet', '-print_format', 'json']
    args.extend(options)
    using_stdin = add_input_file_to_args(args, file_or_blob)

    res = run(args, input=file_or_blob if using_stdin else None, stdout=PIPE, stderr=PIPE)

    if res.returncode == 0:
        return json.loads(res.stdout.decode())
    else:
        raise ChildProcessError('`{}` failed with exit code {}: {}'.format(
            ' '.join(map(shlex.quote, args)), res.returncode, res.stderr))


def convert(file_or_blob, options=(), infile_options=(), outfile_options=()):
    args = [ffmpeg_bin]
    args.extend(options)
    args.extend(infile_options)
    using_stdin = add_input_file_to_args(args, file_or_blob)
    args.extend(outfile_options)
    args.append('pipe:1')

    res = run(args, input=file_or_blob if using_stdin else None, stdout=PIPE, stderr=PIPE)

    if res.returncode == 0:
        return res.stdout
    else:
        raise ChildProcessError('`{}` failed with exit code {}: {}'.format(
            ' '.join(map(shlex.quote, args)), res.returncode, res.stderr))


if __name__ == '__main__':
    print(ffmpeg_bin, ffprobe_bin, bin_version)
