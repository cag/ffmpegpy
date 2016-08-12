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


def probe(file_or_blob, xargs=()):
    args = ['ffprobe', '-v', 'quiet', '-print_format', 'json']
    args.extend(xargs)

    if isinstance(file_or_blob, str):
        args.extend(('-i', file_or_blob))
        res = run(args, stdout=PIPE, stderr=PIPE)
    elif isinstance(file_or_blob, (bytes, bytearray)):
        args.extend(('-i', 'pipe:0'))
        res = run(args, input=file_or_blob, stdout=PIPE, stderr=PIPE)

    if res.returncode == 0:
        return json.loads(res.stdout.decode())
    else:
        raise ChildProcessError('`{}` failed with exit code {}: {}'.format(
            ' '.join(map(shlex.quote, args)), version_run_res.returncode, version_run_res.stderr))


if __name__ == '__main__':
    print(ffmpeg_bin, ffprobe_bin, bin_version)
